import time
from datetime import date

import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# ================== AYARLAR ==================
SYMBOL_FILE = "bist_symbols.txt"
DB_URL = "sqlite:///bist_valuation_measures.db"
TABLE_NAME = "valuation_measures"

SLEEP_SECONDS = 1.0   # semboller arası bekleme (rate limit için)

# Yahoo info içindeki alanlar -> bizim kolon isimleri
VALUATION_FIELDS = {
    "marketCap": "market_cap",
    "enterpriseValue": "enterprise_value",
    "trailingPE": "trailing_pe",
    "forwardPE": "forward_pe",
    "pegRatio": "peg_ratio",
    "priceToSalesTrailing12Months": "price_to_sales_ttm",
    "priceToBook": "price_to_book",
    "enterpriseToRevenue": "ev_to_revenue",
    "enterpriseToEbitda": "ev_to_ebitda",
}


def load_symbols(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def to_yahoo_symbol(raw: str) -> str:
    # Zaten .IS vb. uzantı varsa dokunma
    if "." in raw:
        return raw
    return raw + ".IS"


def fetch_current_valuations(raw_symbol: str) -> dict | None:
    yahoo_symbol = to_yahoo_symbol(raw_symbol)
    print(f"\n=== {raw_symbol} (Yahoo: {yahoo_symbol}) ===")

    tkr = yf.Ticker(yahoo_symbol)

    try:
        # Yeni yfinance sürümlerinde get_info() öneriliyor
        info = tkr.get_info()
    except Exception as e:
        print(f"[HATA] {raw_symbol} için get_info() başarısız: {e}")
        return None

    if not info:
        print(f"[UYARI] {raw_symbol} için info boş geldi.")
        return None

    row = {
        "symbol": raw_symbol,
        "yahoo_symbol": yahoo_symbol,
        # Bu kaydı hangi gün çektiğimiz
        "as_of_date": date.today().isoformat(),
        # Valuation Measures tablosundaki 'Current' sütunu gibi düşünebilirsin
        "period": "Current",
    }

    for yahoo_key, col_name in VALUATION_FIELDS.items():
        row[col_name] = info.get(yahoo_key)

    print(row)
    return row


def main():
    symbols = load_symbols(SYMBOL_FILE)
    print(f"{len(symbols)} sembol bulundu.")

    rows = []

    for i, sym in enumerate(symbols, start=1):
        print(f"\n[{i}/{len(symbols)}] {sym} işleniyor...")
        row = fetch_current_valuations(sym)
        if row is not None:
            rows.append(row)
        time.sleep(SLEEP_SECONDS)

    if not rows:
        print("Hiç veri çekilemedi.")
        return

    df = pd.DataFrame(rows)
    print("\nÖrnek satırlar:")
    print(df.head())

    engine = create_engine(DB_URL)

    try:
        # if_exists='append' -> her çalıştırmada yeni tarihli satırlar eklenir
        with engine.begin() as conn:
            df.to_sql(TABLE_NAME, con=conn, if_exists="append", index=False)
        print(f"\n'{TABLE_NAME}' tablosuna {len(df)} satır yazıldı.")
        print("Veritabanı:", DB_URL)
    except SQLAlchemyError as e:
        print("DB'ye yazarken hata oluştu:", e)
        raise


if __name__ == "__main__":
    main()
