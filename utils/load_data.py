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

    elif os.path.exists(excel_path):
        xls = pd.ExcelFile(excel_path)
        frames = []

        for sheet in xls.sheet_names:
            temp = pd.read_excel(excel_path, sheet_name=sheet)

            # Alleen deze kolommen gebruiken als ze bestaan
            expected = ["Date", "Rainfall (mm)", "Latitude", "Longitude", "StationID"]
            available = [c for c in expected if c in temp.columns]

            # Sheet overslaan als hij geen neerslagkolom heeft
            if "Rainfall (mm)" not in temp.columns:
                continue

            temp = temp[available].copy()

            # Hernoemen
            rename_map = {
                "Date": "date",
                "Rainfall (mm)": "RR",
                "Latitude": "Latitude",
                "Longitude": "Longitude",
                "StationID": "StationID"
            }
            temp = temp.rename(columns=rename_map)

            frames.append(temp)

        if not frames:
            raise ValueError("Geen enkele sheet bevat 'Rainfall (mm)'.")

        df = pd.concat(frames, ignore_index=True)

        # RR numeriek maken
        df["RR"] = df["RR"].apply(clean_rain_value)

        df.to_csv(csv_path, index=False)

    else:
        raise FileNotFoundError(
            f"Geen data gevonden voor jaar {year}. Upload Rainfall_Data_Suriname_{year}.xlsx in /data."
        )

    # Datum verwerken
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day

    return df
