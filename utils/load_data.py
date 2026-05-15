import pandas as pd
import os
import re

def clean_rain_value(x):
    """Zet elke neerslagwaarde om naar een veilig numeriek getal."""
    try:
        s = str(x).strip().lower()
    except:
        return 0

    if s in ["", "-", "—", "na", "none", "nan"]:
        return 0
    if "trace" in s or s == "t":
        return 0

    s = re.sub(r"[^0-9.,]", "", s)
    s = s.replace(",", ".")

    try:
        return float(s)
    except:
        return 0


def load_rr(year):
    csv_path = f"data/rr_{year}.csv"
    excel_path = f"data/Rainfall_Data_Suriname_{year}.xlsx"

    # Gebruik CSV als die bestaat
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 10:
        df = pd.read_csv(csv_path)
        return df

    # Anders: lees Excel
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Bestand ontbreekt: {excel_path}")

    xls = pd.ExcelFile(excel_path)
    frames = []

    for sheet in xls.sheet_names:
        temp = pd.read_excel(excel_path, sheet_name=sheet)

        cols = [c.lower() for c in temp.columns]

        # -------------------------
        # 2026 STRUCTUUR
        # -------------------------
        if "date" in cols and "rainfall (mm)" in cols:
            temp = temp.rename(columns={
                "Date": "date",
                "Rainfall (mm)": "RR",
                "Latitude": "Latitude",
                "Longitude": "Longitude",
                "StationID": "StationID"
            })

            temp["RR"] = temp["RR"].apply(clean_rain_value)
            frames.append(temp)
            continue

        # -------------------------
        # 2025 STRUCTUUR (CLIMSOFT)
        # -------------------------
        if {"year", "month", "day", "precip"}.issubset(set(cols)):
            temp = temp.rename(columns={
                "Year": "year",
                "Month": "month",
                "Day": "day",
                "PRECIP": "RR",
                "Lat": "Latitude",
                "Lon": "Longitude",
                "StationId": "StationID"
            })

            # Datum bouwen
            temp["date"] = pd.to_datetime(
                temp[["year", "month", "day"]], errors="coerce"
            )

            temp["RR"] = temp["RR"].apply(clean_rain_value)
            frames.append(temp)
            continue

    if not frames:
        raise ValueError(f"Geen bruikbare data gevonden in {excel_path}")

    df = pd.concat(frames, ignore_index=True)

    # Datum verwerken
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day

    df.to_csv(csv_path, index=False)
    return df
