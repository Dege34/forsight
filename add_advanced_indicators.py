# -----------------------------------------------------------------------------
# Copyright (c) 2025 Dogan Ege BULTE
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
# -----------------------------------------------------------------------------

import pandas as pd
import pandas_ta as ta
import yfinance as yf
import sqlite3
import numpy as np


def add_new_features(db_name="bist_model_ready.db"):
    conn = sqlite3.connect(db_name)

    print("1. Veritabanındaki veriler okunuyor...")
    df = pd.read_sql("SELECT * FROM model_data", conn)

    df['date'] = pd.to_datetime(df['date'])

    numeric_cols = ['high', 'low', 'close', 'volume']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    print(f"   -> Toplam Satır Sayısı: {len(df)}")

    print("\n2. XBANK ve XUSIN verileri Yahoo Finance'den çekiliyor...")
    try:
        tickers = ['XBANK.IS', 'XUSIN.IS']
        index_data = yf.download(tickers, start="1997-01-01", progress=False, auto_adjust=True)

        if isinstance(index_data.columns, pd.MultiIndex):
            try:
                index_close = index_data.xs('Close', axis=1, level=0)
            except:
                index_close = index_data['Close']
        else:
            index_close = index_data['Close'] if 'Close' in index_data else index_data

        index_close['xbank_xusin_ratio'] = index_close['XBANK.IS'] / index_close['XUSIN.IS']

        ratio_df = index_close[['xbank_xusin_ratio']].reset_index()
        ratio_df.rename(columns={'Date': 'date'}, inplace=True)
        ratio_df['date'] = pd.to_datetime(ratio_df['date'])

        print("   -> Rasyo verisi ana tabloya ekleniyor...")
        if 'xbank_xusin_ratio' in df.columns:
            df = df.drop(columns=['xbank_xusin_ratio'])

        df = pd.merge(df, ratio_df, on='date', how='left')

    except Exception as e:
        print(f"UYARI (Rasyo İndirme): {e}")
        print("İşleme rasyo olmadan devam ediliyor...")

    print("\n3. Teknik İndikatörler Hesaplanıyor (ATR, OBV, MFI)...")
    print("   (Bu işlem veri boyutuna göre biraz zaman alabilir, lütfen bekleyin)")

    def compute_indicators(sub_df):
        sub_df = sub_df.copy()

        sub_df = sub_df.sort_values('date')

        if len(sub_df) < 14:
            sub_df['atr'] = np.nan
            sub_df['obv'] = np.nan
            sub_df['mfi'] = np.nan
            return sub_df

        try:
            atr_res = sub_df.ta.atr(length=14)
            sub_df['atr'] = atr_res.iloc[:, 0] if isinstance(atr_res, pd.DataFrame) else atr_res

            obv_res = sub_df.ta.obv()
            sub_df['obv'] = obv_res.iloc[:, 0] if isinstance(obv_res, pd.DataFrame) else obv_res

            mfi_res = sub_df.ta.mfi(length=14)
            sub_df['mfi'] = mfi_res.iloc[:, 0] if isinstance(mfi_res, pd.DataFrame) else mfi_res

        except Exception as inner_e:
            pass

        return sub_df

    df = df.groupby('symbol', group_keys=False).apply(compute_indicators)

    print("\n4. Veritabanına kaydediliyor (model_data güncelleniyor)...")

    df['date'] = df['date'].dt.strftime('%Y-%m-%d')

    df.columns = [c.lower() for c in df.columns]

    df = df.loc[:, ~df.columns.duplicated()]

    try:
        df.to_sql('model_data', conn, if_exists='replace', index=False)

        cursor = conn.cursor()
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_symbol_date ON model_data (symbol, date)")

        conn.close()
        print("BAŞARILI: İşlem tamamlandı.")

        check_cols = ['symbol', 'date', 'atr', 'obv', 'mfi', 'xbank_xusin_ratio']
        existing_cols = [c for c in check_cols if c in df.columns]
        print(df[existing_cols].tail())

    except Exception as e:
        print(f"Kayıt Hatası: {e}")
        if conn: conn.close()


if __name__ == "__main__":
    add_new_features()
