# -----------------------------------------------------------------------------
# Copyright (c) 2025 Dogan Ege BULTE
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
# -----------------------------------------------------------------------------

import os
import time
import sqlite3
from datetime import datetime

import pandas as pd
from isyatirimhisse import fetch_stock_data

USE_TEST_MODE = True


SYMBOLS_FILE_ALL = r"C:\Users\OMEN\Desktop\forsight\bist_symbols.txt"
SYMBOLS_FILE_TEST = r"C:\Users\OMEN\Desktop\forsight\bist_symbols_test.txt"

SYMBOLS_FILE = SYMBOLS_FILE_TEST if USE_TEST_MODE else SYMBOLS_FILE_ALL


DB_FOLDER = r"C:\Users\OMEN\Desktop\forsight\analysis"
os.makedirs(DB_FOLDER, exist_ok=True)

DB_PATH = os.path.join(DB_FOLDER, "bist_prices.db")

DATE_RANGES = [
    ("03-01-1986", "31-12-1999"),
    ("01-01-2000", "31-12-2009"),
    ("01-01-2010", "31-12-2019"),
    ("01-01-2020", datetime.today().strftime("%d-%m-%Y")),
]

REQUEST_SLEEP = 5

if not os.path.exists(SYMBOLS_FILE):
    raise FileNotFoundError(f"Sembol dosyası bulunamadı: {SYMBOLS_FILE}")

with open(SYMBOLS_FILE, "r", encoding="utf-8") as f:
    symbols = [line.strip().upper() for line in f if line.strip()]

print(f"Kullanılan sembol dosyası: {SYMBOLS_FILE}")
print(f"{len(symbols)} adet sembol bulundu.")

if not symbols:
    raise SystemExit("Sembol listesi boş. Sembol dosyasını kontrol et.")


conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS prices (
        symbol      TEXT NOT NULL,
        date        TEXT NOT NULL,
        close       REAL,
        low         REAL,
        high        REAL,
        volume      REAL,
        PRIMARY KEY (symbol, date)
    )
    """
)
conn.commit()

print(f"Veritabanı hazır: {DB_PATH}")


def fetch_full_history(symbol: str) -> pd.DataFrame | None:
    """Verilen sembol için 1986'dan bugüne kadar tüm veriyi parça parça çeker."""
    parts = []

    for start_date, end_date in DATE_RANGES:
        print(f"[{symbol}] {start_date} - {end_date} aralığı çekiliyor...")
        try:
            df_part = fetch_stock_data(
                symbols=symbol,
                start_date=start_date,
                end_date=end_date,
                save_to_excel=False,
            )
        except Exception as e:
            print(f"[{symbol}] HATA ({start_date} - {end_date}): {e}")
            continue

        if df_part is None or df_part.empty:
            print(f"[{symbol}] Uyarı: Bu aralıkta veri yok ({start_date} - {end_date}).")
        else:
            parts.append(df_part)

        time.sleep(REQUEST_SLEEP)

    if not parts:
        print(f"[{symbol}] Hiç veri alınamadı.")
        return None

    df_all = pd.concat(parts, ignore_index=True)

    df_all["HGDG_TARIH"] = pd.to_datetime(df_all["HGDG_TARIH"])
    df_all = df_all.sort_values("HGDG_TARIH")
    df_all = df_all.drop_duplicates(subset=["HGDG_TARIH"], keep="last")

    return df_all


def save_to_db(symbol: str, df: pd.DataFrame, conn: sqlite3.Connection):
    """DataFrame'i prices tablosuna yazar."""
    rename_map = {
        "HGDG_TARIH": "date",
        "HGDG_KAPANIS": "close",
        "HGDG_MIN": "low",
        "HGDG_MAX": "high",
        "HG_HACIM": "volume",
    }


    cols = [c for c in rename_map.keys() if c in df.columns]
    df_db = df[cols].rename(columns=rename_map)


    df_db["date"] = pd.to_datetime(df_db["date"]).dt.strftime("%Y-%m-%d")


    df_db["symbol"] = symbol


    df_db = df_db[["symbol", "date", "close", "low", "high", "volume"]]


    df_db.to_sql("prices", conn, if_exists="append", index=False)



for idx, symbol in enumerate(symbols, start=1):
    print("\n" + "=" * 80)
    print(f"[{idx}/{len(symbols)}] Sembol işleniyor: {symbol}")
    print("=" * 80)

    cursor.execute(
        "SELECT COUNT(*) FROM prices WHERE symbol = ?",
        (symbol,),
    )
    count_existing = cursor.fetchone()[0]

    if count_existing > 0:
        print(f"[{symbol}] Zaten veritabanında {count_existing} satır var. Atlanıyor.")
        continue

    df_symbol = fetch_full_history(symbol)

    if df_symbol is None or df_symbol.empty:
        print(f"[{symbol}] Veri yok, DB'ye yazılmayacak.")
        continue

    print(f"[{symbol}] Toplam {len(df_symbol)} satır veri alındı, DB'ye yazılıyor...")
    save_to_db(symbol, df_symbol, conn)
    conn.commit()
    print(f"[{symbol}] KAYDEDİLDİ.")

print("\nTÜM İŞLEM BİTTİ.")
print(f"Veritabanı dosyası: {DB_PATH}")

conn.close()
