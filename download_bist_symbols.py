import pandas as pd

url = "https://stockanalysis.com/list/borsa-istanbul/"

print(f"Sayfa indiriliyor: {url}")


tables = pd.read_html(url)

if not tables:
    raise SystemExit("Sayfada hiç tablo bulunamadı. Site yapısı değişmiş olabilir.")

df_symbols = None

for t in tables:
    cols = [str(c).strip() for c in t.columns]
    if "Symbol" in cols:
        df_symbols = t
        break

if df_symbols is None:
    print("Hiçbir tabloda 'Symbol' kolonu bulunamadı. Bulunan kolonlar:")
    for i, t in enumerate(tables):
        print(f"Tablo {i}: {list(t.columns)}")
    raise SystemExit("Symbol kolonu olmadığı için işlem durduruldu.")

symbols = (
    df_symbols["Symbol"]
    .dropna()
    .astype(str)
    .str.strip()
    .str.upper()
    .unique()
)

print(f"Toplam {len(symbols)} adet sembol bulundu.")

output_path = r"C:\Users\OMEN\Desktop\forsight\bist_symbols.txt"

with open(output_path, "w", encoding="utf-8") as f:
    for sym in symbols:
        f.write(sym + "\n")

print(f"[OK] Güncel sembol listesi kaydedildi: {output_path}")
