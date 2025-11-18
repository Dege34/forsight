import sqlite3
import pandas as pd

# Veritabanı yolu
db_path = r"C:\Users\OMEN\Desktop\isyatirimhisse\analysis\bist_prices.db"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

print(f"Veritabanı: {db_path}\n")

# 1) Tabloları listele
print("Tablolar:")
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cur.fetchall()]
for t in tables:
    print(" -", t)

print("\n")

# 2) prices tablosundaki toplam satır sayısı
cur.execute("SELECT COUNT(*) FROM prices;")
total_rows = cur.fetchone()[0]
print(f"prices tablosundaki toplam satır sayısı: {total_rows}\n")

# 3) Toplam sembol sayısı ve tüm sembollerin listesi
cur.execute("SELECT DISTINCT symbol FROM prices ORDER BY symbol;")
symbols = [row[0] for row in cur.fetchall()]

print(f"Toplam sembol sayısı: {len(symbols)}")
print("Semboller:")
print(", ".join(symbols))
print("\n")

# 4) İlk 5 sembol için satır sayıları (hızlı özet)
print("İlk 5 sembol için satır sayıları:")
cur.execute("""
    SELECT symbol, COUNT(*) AS cnt
    FROM prices
    GROUP BY symbol
    ORDER BY symbol
    LIMIT 5;
""")
for symbol, cnt in cur.fetchall():
    print(f" {symbol}: {cnt} satır")

print("\n")

# 5) Örnek sembol seç (ilk 5 satır + tarih aralığı + belirli tarihte close)
default_symbol = "QNBTR"
example_symbol = input(f"Detay görmek istediğin hisse (boş bırakırsan {default_symbol}): ").strip().upper()
if not example_symbol:
    example_symbol = default_symbol

# 5.a) Seçilen sembol için ilk 5 satır
df_sample = pd.read_sql_query(
    "SELECT * FROM prices WHERE symbol = ? ORDER BY date LIMIT 5;",
    conn,
    params=(example_symbol,)
)

print(f"\n{example_symbol} için ilk 5 satır:")
if df_sample.empty:
    print("Bu sembol için veritabanında kayıt bulunamadı.")
else:
    print(df_sample)

print("\n")

# 5.b) Seçilen sembol için tarih aralığı
df_dates = pd.read_sql_query(
    "SELECT MIN(date) AS first_date, MAX(date) AS last_date FROM prices WHERE symbol = ?;",
    conn,
    params=(example_symbol,)
)

print(f"{example_symbol} için tarih aralığı:")
print(df_dates)
print("\n")

# 5.c) Belirli tarihte close (kapanış) değeri
example_date = input("Close değerini görmek istediğin tarih (YYYY-MM-DD, örn: 2024-01-02): ").strip()

if example_date:
    df_close = pd.read_sql_query(
        """
        SELECT symbol, date, close, low, high, volume
        FROM prices
        WHERE symbol = ? AND date = ?
        """,
        conn,
        params=(example_symbol, example_date)
    )

    if df_close.empty:
        print(f"\n{example_symbol} için {example_date} tarihinde kayıt bulunamadı.")
    else:
        print(f"\n{example_symbol} için {example_date} tarihli kayıt:")
        print(df_close.to_string(index=False))
else:
    print("Tarih girmedin, close değeri sorgulanmadı.")

conn.close()
