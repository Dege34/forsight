# -----------------------------------------------------------------------------
# TCMB Reeskont Faiz Oranı
#
# Kaynak: TCMB - Reeskont ve Avans Faiz Oranları (HTML metin)
# URL   : https://www.tcmb.gov.tr/wps/wcm/connect/TR/TCMB%2BTR/Main%2BMenu/
#         Temel%2BFaaliyetler/Para%2BPolitikasi/Reeskont%2Bve%2BAvans%2BFaiz%2BOranlari
#
# Bu script:
#   1) Sayfayı indirir.
#   2) HTML metni içinde regex ile "Yürürlük Tarihi + Reeskont + Avans" satırlarını
#      YAKALAR (linkteki tabloyla birebir aynı)
#      -> tcmb_rediscount_events.csv
#   3) Bu event'lerden 1996'dan itibaren HER AY için,
#      AY SONU itibarıyla geçerli reeskont/avans oranını hesaplar
#      -> tcmb_rediscount_monthly.csv
#
# API KEY GEREKTİRMEZ.
#
# GEREKEN PAKETLER:
#   pip install pandas requests sqlalchemy
# -----------------------------------------------------------------------------

import calendar
import re
import sys
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List

import requests
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# --------------------------- AYARLAR -----------------------------------------

TCMB_REDISCOUNT_URL = (
    "https://www.tcmb.gov.tr/wps/wcm/connect/TR/TCMB%2BTR/Main%2BMenu/"
    "Temel%2BFaaliyetler/Para%2BPolitikasi/Reeskont%2Bve%2BAvans%2BFaiz%2BOranlari"
)

START_YEAR = 1996  # aylık seriyi bu yıldan itibaren istiyoruz

CSV_EVENTS = "tcmb_rediscount_events.csv"
CSV_MONTHLY = "tcmb_rediscount_monthly.csv"

USE_SQLITE = True
DB_URL = "sqlite:///tcmb_policy_rate.db"
DB_TABLE_EVENTS = "tcmb_policy_events"
DB_TABLE_MONTHLY = "tcmb_policy_rate"  # senin sorgunda kullandığın isim


# --------------------------- DATA CLASS --------------------------------------


@dataclass
class MonthlyRediscountRate:
    year: int
    month: int
    month_end_date: date
    rediscount_rate: float
    advance_rate: Optional[float]


# --------------------------- FONKSİYONLAR ------------------------------------


def download_rediscount_page(url: str = TCMB_REDISCOUNT_URL) -> str:
    """
    TCMB 'Reeskont ve Avans Faiz Oranları' sayfasını HTML olarak indirir.
    """
    print(f"[TCMB] Reeskont ve Avans Faiz Oranları sayfası indiriliyor:\n  {url}")
    resp = requests.get(url, timeout=60)
    try:
        resp.raise_for_status()
    except Exception as e:
        print(f"[HATA] Sayfa indirilemedi: {e}")
        print(f"Status kodu: {resp.status_code}, ilk 200 karakter:\n{resp.text[:200]}")
        raise
    print("[TCMB] Sayfa indirildi (boyut: {:.1f} KB)".format(len(resp.content) / 1024))
    return resp.text


def _parse_tr_float(s: str) -> Optional[float]:
    """
    Türkçe formatlı sayıyı (48,25 / 40 / 1.250,00 vb.) float'a çevirir.
    """
    if s is None:
        return None
    s = s.strip()
    if not s:
        return None
    # Binlik ayırıcı noktaları kaldır, virgülü ondalığa çevir
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def parse_events_from_html(html: str) -> pd.DataFrame:
    """
    HTML metni içinden TCMB'nin tablo satırlarını birebir çıkarır.

    Metindeki sıra (örnek, sayfadan birebir):
      Yürürlük Tarihi Reeskont ... Avans ...
      01.01.1990 40 45
      20.09.1990 43     48,25
      ...
      17.09.2025 41,25 42,25

    Pattern: "dd.mm.yyyy <(tag vs olabilir)> <sayı> <(tag vs olabilir)> <sayı>"
    """
    # "Yürürlük Tarihi"nden sonrasını alırsak gereksiz kısımları atmış oluruz
    idx = html.find("Yürürlük Tarihi")
    if idx != -1:
        text = html[idx:]
    else:
        text = html

    pattern = r"(\d{2}\.\d{2}\.\d{4})\D+([\d.,]+)\D+([\d.,]+)"
    matches = re.findall(pattern, text, flags=re.UNICODE | re.DOTALL)

    if not matches:
        raise ValueError("HTML içinde 'tarih + reeskont + avans' pattern'i bulunamadı.")

    print(f"[TCMB] {len(matches)} adet satır yakalandı (tarih + reeskont + avans).")

    records = []
    for date_str, reeskont_str, avans_str in matches:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        reeskont = _parse_tr_float(reeskont_str)
        avans = _parse_tr_float(avans_str)
        records.append(
            {
                "effective_date": dt.date(),   # sayfadaki Yürürlük Tarihi
                "rediscount_rate": reeskont,
                "advance_rate": avans,
            }
        )

    df = pd.DataFrame.from_records(records)
    df = df.sort_values("effective_date").reset_index(drop=True)

    print("[TCMB] Etkin tarih aralığı: {} -> {}".format(
        df["effective_date"].min(), df["effective_date"].max()
    ))

    # Yıl / ay kolonlarını da ekleyelim (kontrol için faydalı)
    df["year"] = pd.to_datetime(df["effective_date"]).dt.year
    df["month"] = pd.to_datetime(df["effective_date"]).dt.month

    return df


def compute_monthly_series(events_df: pd.DataFrame, start_year: int = START_YEAR) -> List[MonthlyRediscountRate]:
    """
    Event (değişiklik) tablosundan, her AY sonu itibarıyla geçerli olan
    reeskont/avans oranını hesaplar.

    Mantık:
      - Her ay için ay sonu tarihi (year, month -> last_day_of_month).
      - O tarihe kadar gerçekleşmiş SON değişiklik bulunur (effective_date <= ay sonu).
      - O satırdaki reeskont/avans oranı, o ayın "ay sonu" oranı kabul edilir.
    """
    if events_df.empty:
        raise ValueError("Event DataFrame'i boş.")

    # event tarihlerini datetime yap
    df = events_df.copy()
    df["date"] = pd.to_datetime(df["effective_date"])

    records: List[MonthlyRediscountRate] = []

    first_year = df["date"].dt.year.min()
    first_month = df["date"].dt.month.min()
    last_year = df["date"].dt.year.max()
    last_month = df["date"].dt.month.max()

    start_year_eff = max(start_year, first_year)

    for year in range(start_year_eff, last_year + 1):
        if year == first_year:
            month_start = first_month
        else:
            month_start = 1

        if year == last_year:
            month_end = last_month
        else:
            month_end = 12

        for month in range(month_start, month_end + 1):
            last_day = calendar.monthrange(year, month)[1]
            month_end_date = datetime(year, month, last_day)

            eligible = df[df["date"] <= month_end_date]
            if eligible.empty:
                continue

            last_row = eligible.iloc[-1]

            rec = MonthlyRediscountRate(
                year=year,
                month=month,
                month_end_date=month_end_date.date(),
                rediscount_rate=float(last_row["rediscount_rate"])
                if pd.notna(last_row["rediscount_rate"])
                else None,
                advance_rate=float(last_row["advance_rate"])
                if pd.notna(last_row["advance_rate"])
                else None,
            )
            records.append(rec)

    if not records:
        raise ValueError(f"{start_year} sonrasına ait aylık seri oluşturulamadı.")

    print(
        f"[TCMB] Aylık seri: {records[0].year}-{records[0].month:02d} "
        f"-> {records[-1].year}-{records[-1].month:02d}"
    )
    return records


def monthly_records_to_dataframe(records: List[MonthlyRediscountRate]) -> pd.DataFrame:
    data = [
        {
            "year": r.year,
            "month": r.month,
            "month_end_date": r.month_end_date.isoformat(),  # TÜRETİLMİŞ tarih
            "rediscount_rate": r.rediscount_rate,
            "advance_rate": r.advance_rate,
        }
        for r in records
    ]
    return pd.DataFrame(data)


def save_to_csv(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)
    print(f"[DOSYA] CSV kaydedildi: {path}")


def save_to_sqlite(
    df: pd.DataFrame,
    db_url: str,
    table_name: str,
) -> Optional[int]:
    engine = create_engine(db_url)
    try:
        with engine.begin() as conn:
            df.to_sql(table_name, con=conn, if_exists="replace", index=False)
        print(
            f"[DB] '{db_url}' veritabanında '{table_name}' tablosuna "
            f"{len(df)} satır yazıldı."
        )
        return len(df)
    except SQLAlchemyError as e:
        print("[HATA] SQLite'e yazarken hata oluştu:", e)
        return None


# ----------------------------- MAIN ------------------------------------------


def main():
    try:
        html = download_rediscount_page()
        events_df = parse_events_from_html(html)          # linkteki tabloyla birebir
        monthly_records = compute_monthly_series(events_df, START_YEAR)
        monthly_df = monthly_records_to_dataframe(monthly_records)
    except Exception as e:
        print("\n[KRİTİK HATA] İşlem durduruldu:", e)
        sys.exit(1)

    print("\n--- TCMB Reeskont Faiz Oranları: EVENT TABLOSU (sayfadakiyle aynı) ---")
    print(events_df)

    print("\n--- {}'dan İtibaren Aylık TCMB Reeskont Faiz Oranları (AY SONU) ---".format(START_YEAR))
    print(monthly_df.head(24))  # ilk 2 yılın aylık serisini göster

    # CSV'ler
    save_to_csv(events_df, CSV_EVENTS)
    save_to_csv(monthly_df, CSV_MONTHLY)

    # SQLite
    if USE_SQLITE:
        save_to_sqlite(events_df, DB_URL, DB_TABLE_EVENTS)
        save_to_sqlite(monthly_df, DB_URL, DB_TABLE_MONTHLY)


if __name__ == "__main__":
    main()
