# -----------------------------------------------------------------------------
# Gerekli Kütüphaneler:
# pip install pandas pandas_ta isyatirimhisse
# -----------------------------------------------------------------------------

import os
import time
import sqlite3
from datetime import datetime

import pandas as pd
import pandas_ta as ta
from isyatirimhisse import fetch_stock_data

# --- AYARLAR ---
USE_TEST_MODE = True  # Test için True, tüm hisseler için False yapın
SYMBOLS_FILE_ALL = r"C:\Users\emre\Desktop\borsa\bist_symbols.txt"
SYMBOLS_FILE_TEST = r"C:\Users\emre\Desktop\borsa\bist_symbols_test.txt"
DB_FOLDER = r"C:\Users\emre\Desktop\borsa"

# Veritabanı ismi
DB_NAME = "bist_final_clean.db"

# Klasör oluştur
os.makedirs(DB_FOLDER, exist_ok=True)
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)

# Dosya seçimi
SYMBOLS_FILE = SYMBOLS_FILE_TEST if USE_TEST_MODE else SYMBOLS_FILE_ALL

# Tarih aralıkları
DATE_RANGES = [
    ("03-01-1990", "31-12-1999"),
    ("01-01-2000", "31-12-2009"),
    ("01-01-2010", "31-12-2019"),
    ("01-01-2020", datetime.today().strftime("%d-%m-%Y")),
]

REQUEST_SLEEP = 1.5

# --- SEMBOL LİSTESİ KONTROLÜ ---
if not os.path.exists(SYMBOLS_FILE):
    raise FileNotFoundError(f"Sembol dosyası bulunamadı: {SYMBOLS_FILE}")

with open(SYMBOLS_FILE, "r", encoding="utf-8") as f:
    symbols = [line.strip().upper() for line in f if line.strip()]

print(f"Sembol dosyası: {SYMBOLS_FILE}")
print(f"İşlenecek hisse sayısı: {len(symbols)}")

if not symbols:
    raise SystemExit("Sembol listesi boş.")

# --- DB BAĞLANTISI ---
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
print(f"Veritabanı yolu: {DB_PATH}")


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Teknik indikatörleri ekler. Hesaplama yapılamazsa sütunları boş (None) olarak ekler
    ki veritabanı şeması bozulmasın.
    """
    # Veritabanında mutlaka olmasını istediğimiz indikatör sütunları
    expected_cols = [
        'pct_change',
        'RSI_14',
        'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9',
        'SMA_50', 'SMA_200',
    ]

    # Veri setinde 'close' yoksa veya veri çok azsa hesaplama yapma ama sütunları aç
    if 'close' not in df.columns or len(df) < 2:
        for col in expected_cols:
            df[col] = None
        return df

    try:
        # 1. Değişim Oranı
        df['pct_change'] = df['close'].pct_change()

        # 2. RSI (Veri yeterliyse)
        if len(df) >= 14:
            df['RSI_14'] = df.ta.rsi(close='close', length=14)

        # 3. MACD (Veri yeterliyse)
        if len(df) >= 26:
            df.ta.macd(close='close', fast=12, slow=26, signal=9, append=True)

        # 4. Hareketli Ortalamalar
        if len(df) >= 50:
            df['SMA_50'] = df.ta.sma(close='close', length=50)
        if len(df) >= 200:
            df['SMA_200'] = df.ta.sma(close='close', length=200)

        # 5. Bollinger Bantları
        if len(df) >= 20:
            df.ta.bbands(close='close', length=20, std=2, append=True)

    except Exception as e:
        print(f"    ! İndikatör hesaplama hatası: {e}")

    # KRİTİK NOKTA: Hesaplama başarısız olduysa veya veri yetmediyse bile
    # o sütunların DataFrame'de var olduğundan emin olmalıyız.
    # Yoksa veritabanı şeması bozulur.
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None

    return df


def fetch_full_history(symbol: str) -> pd.DataFrame | None:
    """Parçalı veri çekimi yapar."""
    parts = []
    for start_date, end_date in DATE_RANGES:
        print(f"  -> {start_date} - {end_date} çekiliyor...")
        try:
            df_part = fetch_stock_data(
                symbols=symbol,
                start_date=start_date,
                end_date=end_date
            )
            if df_part is not None and not df_part.empty:
                parts.append(df_part)

            time.sleep(REQUEST_SLEEP)

        except Exception:
            continue

    if not parts:
        return None

    df_all = pd.concat(parts, ignore_index=True)

    if "HGDG_TARIH" in df_all.columns:
        df_all["HGDG_TARIH"] = pd.to_datetime(df_all["HGDG_TARIH"])
        df_all = df_all.sort_values("HGDG_TARIH")
        df_all = df_all.drop_duplicates(subset=["HGDG_TARIH"], keep="last")

    return df_all


def process_and_save(symbol: str, df: pd.DataFrame, conn: sqlite3.Connection):
    """
    İstenmeyen sütunları siler, sıralamayı düzenler ve kaydeder.
    """

    # 1. Rename
    rename_map = {
        "HGDG_TARIH": "date",
        "HGDG_KAPANIS": "close",
        "HGDG_MIN": "low",
        "HGDG_MAX": "high",
        "HG_HACIM": "volume",
    }
    df = df.rename(columns=rename_map)

    # 2. DROP (İstenmeyenler)
    unwanted_cols = [
        'HGDG_HS_KODU', 'END_ENDEKS_KODU', 'END_SEANS',
        'DD_DT_KODU', 'END_TARIH',
        'HG_KAPANIS', 'HG_AOF', 'HG_MIN', 'HG_MAX'
    ]
    df = df.drop(columns=unwanted_cols, errors='ignore')

    # 3. Sembol Ekle
    df['symbol'] = symbol

    # 4. Tarih Formatı
    if 'date' in df.columns:
        df['date'] = df['date'].dt.strftime("%Y-%m-%d")

    # 5. İndikatörler (Close numeric yapılmalı)
    if 'close' in df.columns:
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        # Burada artık şema garantili fonksiyonu çağırıyoruz
        df = add_technical_indicators(df)

    # 6. Sıralama
    cols = df.columns.tolist()
    if 'symbol' in cols:
        cols.insert(0, cols.pop(cols.index('symbol')))
    if 'date' in cols:
        cols.insert(1, cols.pop(cols.index('date')))

    df = df[cols]

    # 7. Kayıt
    try:
        df.to_sql("prices", conn, if_exists="append", index=False)
        return True
    except Exception as e:
        print(f"    ! DB Hatası: {e}")
        return False


# --- ANA DÖNGÜ ---

for idx, symbol in enumerate(symbols, start=1):
    print("\n" + "-" * 50)
    print(f"[{idx}/{len(symbols)}] {symbol}")

    try:
        cursor.execute("SELECT COUNT(*) FROM prices WHERE symbol = ?", (symbol,))
        if cursor.fetchone()[0] > 0:
            print(f" -> Zaten var. Geçiliyor.")
            continue
    except sqlite3.OperationalError:
        pass

    df_symbol = fetch_full_history(symbol)

    if df_symbol is None or df_symbol.empty:
        print(f" -> Veri yok.")
        continue

    print(f" -> {len(df_symbol)} satır. İşleniyor...")

    if process_and_save(symbol, df_symbol, conn):
        print(" -> KAYDEDİLDİ.")
    else:
        print(" -> HATA OLUŞTU.")

conn.close()
print("\nBİTTİ.")
