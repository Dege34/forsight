# -----------------------------------------------------------------------------
# Copyright (c) 2025 Dogan Ege BULTE
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
# -----------------------------------------------------------------------------

import os
import time
from datetime import date, datetime

import pandas as pd
from yahooquery import Ticker
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

SYMBOL_FILE = "bist_symbols.txt"
DB_URL = "sqlite:///bist_valuation_measures.db"
TABLE_NAME = "valuation_measures"

SLEEP_SECONDS = 1.0
START_DATE = date(2016, 1, 1)  # 2016'dan itibaren veri

# Yahoo Finance Premium kullanıyorsan bu ortam değişkenlerini ayarla
YF_USERNAME = os.getenv("YF_USERNAME")
YF_PASSWORD = os.getenv("YF_PASSWORD")

# yahooquery kolon isimlerini veritabanındaki kolonlara map et
# (Gelen gerçek kolonları bir kere print(df.columns) ile kontrol etmen iyi olur.)
VALUATION_FIELDS = {
    "EnterpriseValue": "enterprise_value",
    "EnterpriseValueEBITDA": "ev_to_ebitda",     # isim farklıysa df.columns'tan bakıp düzelt
    "EnterpriseValueRevenue": "ev_to_revenue",   # aynı şekilde kontrol edebilirsin
    "ForwardPeRatio": "forward_pe",
    "MarketCap": "market_cap",
    "PbRatio": "price_to_book",
    "PeRatio": "trailing_pe",
    "PegRatio": "peg_ratio",
    "PsRatio": "price_to_sales_ttm",
}


def load_symbols(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def to_yahoo_symbol(raw: str) -> str:
    if "." in raw:
        return raw
    return raw + ".IS"


def _build_ticker(yahoo_symbol: str) -> Ticker:
    """
    Premium varsa p_valuation_measures kullanılabilecek şekilde Ticker oluşturur.
    """
    if YF_USERNAME and YF_PASSWORD:
        return Ticker(
            yahoo_symbol,
            username=YF_USERNAME,
            password=YF_PASSWORD,
        )
    return Ticker(yahoo_symbol)


def _normalize_valuation_df(data) -> pd.DataFrame | None:
    """
    yahooquery'nin valuation_measures / p_valuation_measures çıktısını
    normalize eder: tip kontrolü, kolon isimlerini garanti eder ve tarih filtresini uygular.
    """

    # Önce tip kontrolü: bazı sembollerde string veya dict dönebilir
    if data is None:
        return None

    if isinstance(data, str):
        # Ör: "No fundamentals data found for XU100.IS"
        print(f"[UYARI] valuation_measures string döndü: {data}")
        return None

    if isinstance(data, dict):
        # Ör: {"XU100.IS": "No fundamentals data found ..."}
        print(f"[UYARI] valuation_measures dict döndü: {data}")
        return None

    if not isinstance(data, pd.DataFrame):
        print(f"[UYARI] valuation_measures beklenmeyen tip: {type(data)}")
        return None

    df: pd.DataFrame = data

    if df.empty:
        return None

    # Bazı versiyonlarda 'symbol' ve/veya 'asOfDate' index'te olabilir, garanti edelim
    if "symbol" not in df.columns or "asOfDate" not in df.columns:
        df = df.reset_index()

    if "asOfDate" not in df.columns:
        print("[UYARI] DataFrame içinde 'asOfDate' kolonu bulunamadı.")
        return None

    # Tarihi date objesine çevir ve 2016 filtresi uygula
    df = df.copy()
    df["asOfDate"] = pd.to_datetime(df["asOfDate"]).dt.date
    df = df[df["asOfDate"] >= START_DATE]

    if df.empty:
        return None

    return df


def fetch_valuation_history(raw_symbol: str) -> list[dict]:
    """
    Verilen sembol için 2016'dan itibaren mevcut olan valuation_measures
    kayıtlarını çeker ve her satırı dict olarak döner.
    """
    yahoo_symbol = to_yahoo_symbol(raw_symbol)
    print(f"\n=== {raw_symbol} (Yahoo: {yahoo_symbol}) ===")

    try:
        tkr = _build_ticker(yahoo_symbol)
    except Exception as e:
        print(f"[HATA] {raw_symbol} için Ticker oluşturulamadı: {e}")
        return []

    df = None

    try:
        if YF_USERNAME and YF_PASSWORD:
            # Premium: uzun dönem tarihsel veri, aylık (m) frekans
            df = tkr.p_valuation_measures(frequency="m")
            print("Premium p_valuation_measures(frequency='m') kullanılıyor.")
        else:
            # Ücretsiz: son 4 çeyrek + en güncel tarih (sınırlı)
            df = tkr.valuation_measures
            print("Ücretsiz valuation_measures kullanılıyor (sınırlı tarih).")
    except Exception as e:
        print(f"[HATA] {raw_symbol} için valuation_measures alınamadı: {e}")
        return []

    df = _normalize_valuation_df(df)
    if df is None:
        print(f"[UYARI] {raw_symbol} için 2016 sonrası uygun valuation verisi yok.")
        return []

    # Sadece bu sembole ait satırlar (teoride zaten tek sembol ama garanti edelim)
    if "symbol" in df.columns:
        df = df[df["symbol"].str.upper() == yahoo_symbol.upper()]

    if df.empty:
        print(f"[UYARI] {raw_symbol} için 2016 sonrası satır kalmadı.")
        return []

    records: list[dict] = []

    for _, rec in df.iterrows():
        as_of = rec["asOfDate"]
        if isinstance(as_of, datetime):
            as_of = as_of.date()
        as_of_str = as_of.isoformat() if isinstance(as_of, date) else str(as_of)

        row: dict = {
            "symbol": raw_symbol,
            "yahoo_symbol": yahoo_symbol,
            "as_of_date": as_of_str,
            "period": rec.get("periodType", None),
        }

        # Valuation alanlarını map et
        for yahoo_key, col_name in VALUATION_FIELDS.items():
            row[col_name] = rec.get(yahoo_key, None)

        records.append(row)

    print(f"{raw_symbol} için {len(records)} satır oluşturuldu.")
    return records


def main():
    symbols = load_symbols(SYMBOL_FILE)
    print(f"{len(symbols)} sembol bulundu.")

    all_rows: list[dict] = []

    for i, sym in enumerate(symbols, start=1):
        print(f"\n[{i}/{len(symbols)}] {sym} işleniyor...")
        recs = fetch_valuation_history(sym)
        if recs:
            all_rows.extend(recs)
        time.sleep(SLEEP_SECONDS)

    if not all_rows:
        print("Hiç veri çekilemedi.")
        return

    df = pd.DataFrame(all_rows)
    print("\nÖrnek satırlar:")
    print(df.head())

    engine = create_engine(DB_URL)

    try:
        with engine.begin() as conn:
            df.to_sql(TABLE_NAME, con=conn, if_exists="append", index=False)
        print(f"\n'{TABLE_NAME}' tablosuna {len(df)} satır yazıldı.")
        print("Veritabanı:", DB_URL)
    except SQLAlchemyError as e:
        print("DB'ye yazarken hata oluştu:", e)
        raise


if __name__ == "__main__":
    main()
