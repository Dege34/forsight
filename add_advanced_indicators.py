import pandas as pd
import pandas_ta as ta
import yfinance as yf
import sqlite3
import numpy as np


def add_new_features(db_name="bist_model_ready.db"):
    conn = sqlite3.connect(db_name)

    print("1. Veritabanındaki veriler okunuyor...")
    df = pd.read_sql("SELECT * FROM model_data", conn)

    # Tarih formatını garantiye al
    df['date'] = pd.to_datetime(df['date'])

    # Sayısal dönüşümler
    numeric_cols = ['high', 'low', 'close', 'volume']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    print(f"   -> Toplam Satır Sayısı: {len(df)}")

    # ---------------------------------------------------------
    # BÖLÜM 1: XBANK / XUSIN Rasyosu
    # ---------------------------------------------------------
    print("\n2. XBANK ve XUSIN verileri Yahoo Finance'den çekiliyor...")
    try:
        tickers = ['XBANK.IS', 'XUSIN.IS']
        index_data = yf.download(tickers, start="1997-01-01", progress=False, auto_adjust=True)

        # Yahoo Finance MultiIndex düzeltmesi
        if isinstance(index_data.columns, pd.MultiIndex):
            try:
                index_close = index_data.xs('Close', axis=1, level=0)
            except:
                index_close = index_data['Close']
        else:
            index_close = index_data['Close'] if 'Close' in index_data else index_data

        # Rasyo Hesapla
        index_close['xbank_xusin_ratio'] = index_close['XBANK.IS'] / index_close['XUSIN.IS']

        ratio_df = index_close[['xbank_xusin_ratio']].reset_index()
        ratio_df.rename(columns={'Date': 'date'}, inplace=True)
        ratio_df['date'] = pd.to_datetime(ratio_df['date'])

        # Merge işlemi
        print("   -> Rasyo verisi ana tabloya ekleniyor...")
        if 'xbank_xusin_ratio' in df.columns:
            # Eğer rasyo sütunu zaten varsa silip tekrar ekleyelim (Duplicate hatası olmasın)
            df = df.drop(columns=['xbank_xusin_ratio'])

        df = pd.merge(df, ratio_df, on='date', how='left')

    except Exception as e:
        print(f"UYARI (Rasyo İndirme): {e}")
        print("İşleme rasyo olmadan devam ediliyor...")

    # ---------------------------------------------------------
    # BÖLÜM 2: Teknik İndikatörler (ATR, OBV, MFI) - DÜZELTİLMİŞ KISIM
    # ---------------------------------------------------------
    print("\n3. Teknik İndikatörler Hesaplanıyor (ATR, OBV, MFI)...")
    print("   (Bu işlem veri boyutuna göre biraz zaman alabilir, lütfen bekleyin)")

    def compute_indicators(sub_df):
        # Kopya üzerinde çalışalım, uyarıları engelleyelim
        sub_df = sub_df.copy()

        # Tarihe göre sırala
        sub_df = sub_df.sort_values('date')

        # Yeterli veri yoksa boş dön
        if len(sub_df) < 14:
            sub_df['atr'] = np.nan
            sub_df['obv'] = np.nan
            sub_df['mfi'] = np.nan
            return sub_df

        try:
            # --- 1. ATR ---
            atr_res = sub_df.ta.atr(length=14)
            # Eğer DataFrame dönerse ilk sütunu al (.iloc[:, 0]), değilse kendisini al
            sub_df['atr'] = atr_res.iloc[:, 0] if isinstance(atr_res, pd.DataFrame) else atr_res

            # --- 2. OBV ---
            obv_res = sub_df.ta.obv()
            sub_df['obv'] = obv_res.iloc[:, 0] if isinstance(obv_res, pd.DataFrame) else obv_res

            # --- 3. MFI ---
            mfi_res = sub_df.ta.mfi(length=14)
            sub_df['mfi'] = mfi_res.iloc[:, 0] if isinstance(mfi_res, pd.DataFrame) else mfi_res

        except Exception as inner_e:
            # Nadir hesaplama hataları için (örn: tüm değerler NaN ise)
            # print(f"Hata: {inner_e}")
            pass

        return sub_df

    # GroupBy işlemi
    df = df.groupby('symbol', group_keys=False).apply(compute_indicators)

    # ---------------------------------------------------------
    # BÖLÜM 3: Kayıt
    # ---------------------------------------------------------
    print("\n4. Veritabanına kaydediliyor (model_data güncelleniyor)...")

    # Tarih sütununu string yap
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')

    # Tüm sütun adlarını küçük harfe çevir
    df.columns = [c.lower() for c in df.columns]

    # Sütun tekrarlarını temizle (Önlem amaçlı)
    df = df.loc[:, ~df.columns.duplicated()]

    try:
        df.to_sql('model_data', conn, if_exists='replace', index=False)

        cursor = conn.cursor()
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_symbol_date ON model_data (symbol, date)")

        conn.close()
        print("BAŞARILI: İşlem tamamlandı.")

        # Kontrol çıktısı
        check_cols = ['symbol', 'date', 'atr', 'obv', 'mfi', 'xbank_xusin_ratio']
        # Sadece var olan sütunları göster
        existing_cols = [c for c in check_cols if c in df.columns]
        print(df[existing_cols].tail())

    except Exception as e:
        print(f"Kayıt Hatası: {e}")
        if conn: conn.close()


if __name__ == "__main__":
    add_new_features()