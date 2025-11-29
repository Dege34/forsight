# -----------------------------------------------------------------------------
# Copyright (c) 2025 Dogan Ege BULTE
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
# -----------------------------------------------------------------------------

import pandas as pd
import sqlite3


def merge_all_into_single_table(db_name="bist_model_ready.db"):
    print(f"Veritabanına bağlanılıyor: {db_name} ...")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        print("1. Tablolar okunuyor (model_data ve global_inputs)...")

        df_main = pd.read_sql("SELECT * FROM model_data", conn)

        df_global = pd.read_sql("SELECT * FROM global_inputs", conn)

        print(f"   -> Hisse Verisi Satır Sayısı: {len(df_main)}")
        print(f"   -> Global Veri Satır Sayısı: {len(df_global)}")

        df_main['date'] = df_main['date'].astype(str)
        df_global['date'] = df_global['date'].astype(str)

        print("2. Tablolar birleştiriliyor (Merge)...")
        df_merged = pd.merge(df_main, df_global, on='date', how='left')

        print("3. Yeni birleştirilmiş tablo 'model_data' üzerine yazılıyor...")

        df_merged.to_sql('model_data', conn, if_exists='replace', index=False)

        print("4. 'global_inputs' tablosu siliniyor (temizlik)...")
        cursor.execute("DROP TABLE IF EXISTS global_inputs")

        print("5. İndeksler yeniden oluşturuluyor...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON model_data (date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_symbol ON model_data (symbol)")

        conn.commit()
        print("\n--- İŞLEM BAŞARILI ---")
        print("Artık sadece 'model_data' tablonuz var ve içinde Brent, SP500, VIX verileri mevcut.")
        print("Sütunlar:", list(df_merged.columns))

    except Exception as e:
        print(f"\nHATA OLUŞTU: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    merge_all_into_single_table()
