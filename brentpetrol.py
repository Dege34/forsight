import pandas as pd
import sqlite3


def merge_all_into_single_table(db_name="bist_model_ready.db"):
    print(f"Veritabanına bağlanılıyor: {db_name} ...")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        # 1. Mevcut iki tabloyu da DataFrame olarak belleğe al
        print("1. Tablolar okunuyor (model_data ve global_inputs)...")

        # Ana hisse verileri
        df_main = pd.read_sql("SELECT * FROM model_data", conn)

        # Global veriler
        df_global = pd.read_sql("SELECT * FROM global_inputs", conn)

        # Veri boyutlarını kontrol et
        print(f"   -> Hisse Verisi Satır Sayısı: {len(df_main)}")
        print(f"   -> Global Veri Satır Sayısı: {len(df_global)}")

        # 2. Tarih formatlarının çakıştığından emin ol (Garanti olsun diye)
        # Her ikisini de string formatına çeviriyoruz ki eşleşme hatası olmasın
        df_main['date'] = df_main['date'].astype(str)
        df_global['date'] = df_global['date'].astype(str)

        # 3. MERGE İŞLEMİ (Sol taraf: Hisseler, Sağ taraf: Global veriler)
        # how='left': Hisse verilerini koru. O güne ait global veri varsa ekle, yoksa boş kalsın.
        print("2. Tablolar birleştiriliyor (Merge)...")
        df_merged = pd.merge(df_main, df_global, on='date', how='left')

        # 4. Veritabanına Geri Yazma
        print("3. Yeni birleştirilmiş tablo 'model_data' üzerine yazılıyor...")

        # if_exists='replace': Eski model_data tablosunu siler, yerine yenisini yazar.
        df_merged.to_sql('model_data', conn, if_exists='replace', index=False)

        # 5. Gereksiz olan 'global_inputs' tablosunu sil
        print("4. 'global_inputs' tablosu siliniyor (temizlik)...")
        cursor.execute("DROP TABLE IF EXISTS global_inputs")

        # 6. Performans için tekrar index oluştur
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