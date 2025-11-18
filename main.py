from isyatirimhisse import fetch_stock_data
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

# ==========================
# 1) Kullanıcıdan sembol al
# ==========================
symbol = input("Hisse sembolü (örn: THYAO): ").strip().upper()

# ==========================
# 2) Tarih aralıklarını tanımla
#    03-01-1986'dan bugüne kadar
# ==========================
date_ranges = [
    ("03-01-1986", "31-12-1999"),
    ("01-01-2000", "31-12-2009"),
    ("01-01-2010", "31-12-2019"),
    ("01-01-2020", datetime.today().strftime("%d-%m-%Y")),
]

all_data = []

for start_date, end_date in date_ranges:
    print(f"{symbol} için {start_date} - {end_date} aralığı çekiliyor...")
    try:
        df_part = fetch_stock_data(
            symbols=symbol,
            start_date=start_date,
            end_date=end_date,
            save_to_excel=False
        )
        if df_part is not None and not df_part.empty:
            all_data.append(df_part)
        else:
            print(f"[Uyarı] Bu aralık için veri gelmedi: {start_date} - {end_date}")
    except Exception as e:
        print(f"[Hata] {start_date} - {end_date} aralığında sorun: {e}")

if not all_data:
    print("Hiçbir aralıktan veri gelemedi. Muhtemelen site bağlantıyı kesiyor veya IP engellenmiş.")
    raise SystemExit

# ==========================
# 3) Tüm veriyi birleştir
# ==========================
df = pd.concat(all_data, ignore_index=True)

df["HGDG_TARIH"] = pd.to_datetime(df["HGDG_TARIH"])
df = df.sort_values("HGDG_TARIH")

# Aynı günü tekrarlayan satırlar varsa sonuncuyu bırak
df = df.drop_duplicates(subset=["HGDG_TARIH"], keep="last")

# ==========================
# 4) Klasör yapısı (analysis / <SEMBOL>)
# ==========================
base_folder = r"C:\Users\OMEN\Desktop\isyatirimhisse\analysis"
symbol_folder = os.path.join(base_folder, symbol)  # örn: ...\analysis\THYAO
os.makedirs(symbol_folder, exist_ok=True)

# ==========================
# 5) Excel'e kaydet
# ==========================
file_name = f"analysis_{symbol}.xlsx"
file_path = os.path.join(symbol_folder, file_name)

try:
    df.to_excel(file_path, index=False)
    print(f"\n[OK] Toplam {len(df)} satır veri kaydedildi: {file_path}")
except PermissionError:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    alt_file_name = f"analysis_{symbol}_{timestamp}.xlsx"
    alt_file_path = os.path.join(symbol_folder, alt_file_name)
    df.to_excel(alt_file_path, index=False)
    print(f"\n[UYARI] {file_path} dosyasına yazılamadı (muhtemelen Excel'de açık).")
    print(f"[OK] Veri yeni dosyaya kaydedildi: {alt_file_path}")

# ==========================
# 6) Terminalde tablo gibi, hisse adıyla birlikte göster
# ==========================

# Kullanmak istediğimiz kolonlar ve yeni isimleri
kolon_harita = {
    "HGDG_TARIH": "Tarih",
    "HGDG_KAPANIS": "Kapanis",
    "HGDG_AOF": "Ortalama",
    "HGDG_MIN": "Min",
    "HGDG_MAX": "Max",
    "HG_HACIM": "Hacim_TL"
}

# Sadece mevcut olan kolonları al
mevcut_harita = {k: v for k, v in kolon_harita.items() if k in df.columns}
ozet_df = df[list(mevcut_harita.keys())].rename(columns=mevcut_harita)

# Tarihi düzgün formatla
if "Tarih" in ozet_df.columns:
    ozet_df["Tarih"] = pd.to_datetime(ozet_df["Tarih"]).dt.strftime("%Y-%m-%d")

# En başa Sembol kolonu ekle
ozet_df.insert(0, "Sembol", symbol)

ilk_tarih = df["HGDG_TARIH"].min().date()
son_tarih = df["HGDG_TARIH"].max().date()

print("\n" + "=" * 80)
print(f"{symbol} - TÜM VERİ (03-01-1986'dan bugüne)")
print(f"Toplam satır: {len(df)} | İlk tarih: {ilk_tarih} | Son tarih: {son_tarih}")
print("=" * 80 + "\n")

# Pandas görüntü ayarları – TÜM satırları göster, tabloyu daha derli toplu yap
pd.set_option("display.max_rows", None)       # tüm satırlar
pd.set_option("display.max_columns", None)    # tüm kolonlar
pd.set_option("display.width", 200)           # satırlar çok bölünmesin
pd.set_option("display.colheader_justify", "center")

# Tüm tabloyu yazdır (index yok, tamamen tablo gibi)
print(ozet_df.to_string(index=False))

print("\n" + "=" * 80)
print("(Daha fazla kolon/detay için Excel dosyasına bakabilirsin.)")
print("=" * 80 + "\n")

# ==========================
# 7) Grafik (kapanış fiyatı) + PNG + SVG + CSV
# ==========================
if "HGDG_KAPANIS" in df.columns:
    plt.figure()
    plt.plot(df["HGDG_TARIH"], df["HGDG_KAPANIS"])
    plt.xlabel("Tarih")
    plt.ylabel("Kapanış Fiyatı")
    plt.title(f"{symbol} - 03-01-1986'dan bugüne kapanış fiyatı")
    plt.tight_layout()

    # ---- Grafik dosyaları ----
    graph_file_name_png = f"{symbol}_graph.png"
    graph_file_name_svg = f"{symbol}_graph.svg"
    graph_path_png = os.path.join(symbol_folder, graph_file_name_png)
    graph_path_svg = os.path.join(symbol_folder, graph_file_name_svg)

    # PNG ve SVG olarak kaydet
    plt.savefig(graph_path_png)
    plt.savefig(graph_path_svg)

    print(f"[OK] Grafik PNG kaydedildi: {graph_path_png}")
    print(f"[OK] Grafik SVG kaydedildi: {graph_path_svg}")

    # ---- Grafik verisini (tarih + kapanış) CSV olarak kaydet ----
    df_plot = pd.DataFrame({
        "Tarih": df["HGDG_TARIH"].dt.strftime("%Y-%m-%d"),
        "Kapanis": df["HGDG_KAPANIS"]
    })

    csv_file_name = f"{symbol}_graph_data.csv"
    csv_path = os.path.join(symbol_folder, csv_file_name)
    df_plot.to_csv(csv_path, index=False)

    print(f"[OK] Grafik verisi CSV olarak kaydedildi: {csv_path}")

    # Grafiği ekranda göster
    plt.show()

print("\n--- BİTTİ ---")
