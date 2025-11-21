#NOT COMPLETED

# -----------------------------------------------------------------------------
# Copyright (c) 2025 Dogan Ege BULTE
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
# -----------------------------------------------------------------------------

import time
from datetime import date
import re

import requests
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

BASE_URL = "https://fintables.com/sirketler/{symbol}/finansal-tablolar/bilanco"
SYMBOL_FILE = "bist_symbols.txt"      
DB_URL = "sqlite:///fintables_bilancolar.db"
TABLE_NAME = "bilanco_kalemleri"

MIN_YEAR = 2016      
SLEEP_SECONDS = 1.5   

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}

SESSION = requests.Session()


def load_symbols(path: str) -> list[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def fetch_balance_table_html(symbol: str) -> str | None:
    url = BASE_URL.format(symbol=symbol)
    print(f"  -> GET {url}")
    try:
        resp = SESSION.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"[HATA] {symbol} için istek hatası: {e}")
        return None


def pick_balance_dataframe(html: str) -> pd.DataFrame | None:
    """
    Sayfadaki tabloları tarayıp, kolon başlıklarında '2024/12' gibi
    dönemsellik olan tabloyu seçmeye çalışır.
    """
    try:
        tables = pd.read_html(html) 
    except ValueError:
        print("  -> HTML içinde tablo bulunamadı.")
        return None

    if not tables:
        print("  -> read_html tablo döndürmedi.")
        return None

    year_pattern = re.compile(r"^\d{4}/\d{1,2}$")

    for idx, df in enumerate(tables):
        if df.shape[1] < 2:
            continue

        cols = df.columns
        periods = cols[1:]

        has_period = False
        for p in periods:
            if isinstance(p, str) and year_pattern.match(p.strip()):
                has_period = True
                break

        if has_period:
            print(f"  -> {idx}. tablo bilanço gibi görünüyor.")
            return df

    print("  -> Bilanço tablosu bulunamadı.")
    return None


def tidy_balance_df(symbol: str, raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Kolon isimlerini temizler, 2016'dan önceki dönemleri atar,
    uzun formata (symbol, kalem, period, value) çevirir.
    """
    df = raw_df.copy()

    first_col = df.columns[0]
    df = df.rename(columns={first_col: "kalem"})

    keep_cols = ["kalem"]
    for col in df.columns[1:]:
        year = None
        if isinstance(col, str) and len(col) >= 4 and col[:4].isdigit():
            year = int(col[:4])
        if year is not None and year >= MIN_YEAR:
            keep_cols.append(col)

    df = df[keep_cols]

    long_df = df.melt(
        id_vars=["kalem"],
        var_name="period",
        value_name="value",
    )

    long_df["symbol"] = symbol
    long_df["as_of_date"] = date.today().isoformat()

    long_df = long_df.dropna(subset=["value"])

    return long_df


def fetch_balance_for_symbol(symbol: str) -> pd.DataFrame | None:
    print(f"\n=== {symbol} ===")
    html = fetch_balance_table_html(symbol)
    if html is None:
        return None

    raw_df = pick_balance_dataframe(html)
    if raw_df is None:
        return None

    cleaned = tidy_balance_df(symbol, raw_df)
    print(cleaned.head())
    return cleaned


def main():
    symbols = load_symbols(SYMBOL_FILE)
    if not symbols:
        print("bist_symbols.txt bulunamadı veya boş. Örneğin HALKB ile denemek istersen kodda main() içini düzenle.")
        return

    print(f"{len(symbols)} sembol bulundu.")

    all_frames: list[pd.DataFrame] = []

    for i, sym in enumerate(symbols, start=1):
        print(f"\n[{i}/{len(symbols)}] {sym} işleniyor...")
        df = fetch_balance_for_symbol(sym)
        if df is not None and not df.empty:
            all_frames.append(df)
        time.sleep(SLEEP_SECONDS)

    if not all_frames:
        print("Hiç veri üretilemedi.")
        return

    result = pd.concat(all_frames, ignore_index=True)
    print("\nToplam satır:", len(result))
    print(result.head())

    engine = create_engine(DB_URL)

    try:
        with engine.begin() as conn:
            result.to_sql(TABLE_NAME, con=conn, if_exists="append", index=False)
        print(f"\n'{TABLE_NAME}' tablosuna {len(result)} satır yazıldı.")
        print("Veritabanı:", DB_URL)
    except SQLAlchemyError as e:
        print("DB'ye yazarken hata oluştu:", e)
        raise


if __name__ == "__main__":
    main()
