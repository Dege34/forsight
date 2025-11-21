import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Çekilecek sembol
SYMBOL = "XU100.IS"

print(f"{SYMBOL} için veri çekiliyor...")

# 1) Yahoo Finance'ten veri çek
try:
    df = yf.download(SYMBOL, period="max", interval="1d", auto_adjust=False)
except Exception as e:
    print("Veri çekerken hata oluştu:", e)
    raise

if df.empty:
    print("Yahoo Finance veri döndürmedi (DataFrame boş).")
    raise SystemExit(1)

# 2) Date index'ini kolona çevir
df.reset_index(inplace=True)

# 3) MultiIndex kolonları düzleştir
if isinstance(df.columns, pd.MultiIndex):
    new_cols = []
    for col in df.columns:
        # Örn: ("Open", "XU100.IS") -> "Open_XU100.IS"
        parts = [str(x) for x in col if x is not None and x != ""]
        new_cols.append("_".join(parts))
    df.columns = new_cols
else:
    df.columns = [str(c) for c in df.columns]

# 4) Kolon isimlerini küçült
df.columns = [c.lower() for c in df.columns]

# 5) date kolonunu sadece tarih (DATE) yap
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"]).dt.date

print("Kolonlar:", df.columns)
print(df.head())

# 6) Veritabanına yaz (SQLite)
db_url = "sqlite:///bist100.db"   # İstersen burayı PostgreSQL / MySQL ile değiştirebilirsin
table_name = "bist100_history"

engine = create_engine(db_url)

try:
    # if_exists="replace" -> tablo varsa sil ve baştan oluştur
    with engine.begin() as conn:
        df.to_sql(table_name, con=conn, if_exists="replace", index=False)
    print(f"{len(df)} satır '{table_name}' tablosuna yazıldı.")
    print("Veritabanı dosyası: bist100.db")
except SQLAlchemyError as e:
    print("DB'ye yazarken hata oluştu:", e)
    raise
