# -----------------------------------------------------------------------------
# Copyright (c) 2025 Dogan Ege BULTE
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
# -----------------------------------------------------------------------------

import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

SYMBOL = "XU100.IS"

print(f"{SYMBOL} için veri çekiliyor...")

try:
    df = yf.download(SYMBOL, period="max", interval="1d", auto_adjust=False)
except Exception as e:
    print("Veri çekerken hata oluştu:", e)
    raise

if df.empty:
    print("Yahoo Finance veri döndürmedi (DataFrame boş).")
    raise SystemExit(1)

df.reset_index(inplace=True)

if isinstance(df.columns, pd.MultiIndex):
    new_cols = []
    for col in df.columns:
        parts = [str(x) for x in col if x is not None and x != ""]
        new_cols.append("_".join(parts))
    df.columns = new_cols
else:
    df.columns = [str(c) for c in df.columns]

df.columns = [c.lower() for c in df.columns]

if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"]).dt.date

print("Kolonlar:", df.columns)
print(df.head())

db_url = "sqlite:///bist100.db" 
table_name = "bist100_history"

engine = create_engine(db_url)

try:
    with engine.begin() as conn:
        df.to_sql(table_name, con=conn, if_exists="replace", index=False)
    print(f"{len(df)} satır '{table_name}' tablosuna yazıldı.")
    print("Veritabanı dosyası: bist100.db")
except SQLAlchemyError as e:
    print("DB'ye yazarken hata oluştu:", e)
    raise
