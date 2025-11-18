import sqlite3
import pandas as pd

db_path = r"C:\Users\OMEN\Desktop\forsight\analysis\bist_prices.db"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

print(f"Veritabanı: {db_path}\n")

print("Tablolar:")
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cur.fetchall()]
for t in tables:
    print(" -", t)

print("\n")

cur.execute("SELECT COUNT(*) FROM prices;")
total_rows = cur.fetchone()[0]
print(f"prices tablosundaki toplam satır sayısı: {total_rows}\n")

cur.execute("SELECT DISTINCT symbol FROM prices ORDER BY symbol;")
symbols = [row[0] for row in cur.fetchall()]

print(f"Toplam sembol sayısı: {len(symbols)}")
print("Semboller:")
print(", ".join(symbols))
print("\n")

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

default_symbol = "QNBTR"
example_symbol = input(f"Detay görmek istediğin hisse (boş bırakırsan {default_symbol}): ").strip().upper()
if not example_symbol:
    example_symbol = default_symbol

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

df_dates = pd.read_sql_query(
    "SELECT MIN(date) AS first_date, MAX(date) AS last_date FROM prices WHERE symbol = ?;",
    conn,
    params=(example_symbol,)
)

print(f"{example_symbol} için tarih aralığı:")
print(df_dates)
print("\n")

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
