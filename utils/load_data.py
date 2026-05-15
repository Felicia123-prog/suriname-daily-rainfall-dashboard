import pandas as pd
import os
import re

def clean_rain_value(x):
    """Maakt elke neerslagwaarde veilig numeriek."""
    if pd.isna(x):
        return 0

    s = str(x).strip().lower()

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

    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 10:
        df = pd.read_csv(csv_path)

    elif os.path.exists(excel_path):
        xls = pd.ExcelFile(excel_path)
        frames = []

        for sheet in xls.sheet_names:
            temp = pd.read_excel(excel_path, sheet_name=sheet)

            colmap = {}
            for c in temp.columns:
                cl = c.lower().strip()

                if cl in ["date", "datum", "obsdatetime", "datetime"]:
                    colmap[c] = "date"
                if any(x in cl for x in ["rain", "rr", "precip", "rainfall", "mm"]):
                    colmap[c] = "RR"
                if cl in ["latitude", "lat"]:
                    colmap[c] = "Latitude"
                if cl in ["longitude", "lon", "long"]:
                    colmap[c] = "Longitude"
                if cl in ["stationid", "station", "station_id"]:
                    colmap[c] = "StationID"

            temp = temp.rename(columns=colmap)

            keep = [c for c in ["date", "RR", "Latitude", "Longitude", "StationID"] if c in temp.columns]
            temp = temp[keep]

            frames.append(temp)

        df = pd.concat(frames, ignore_index=True)

        if "RR" not in df.columns:
            df["RR"] = 0

        df["RR"] = df["RR"].apply(clean_rain_value)

        df.to_csv(csv_path, index=False)

    else:
        raise FileNotFoundError(
            f"Geen data gevonden voor jaar {year}. Upload Rainfall_Data_Suriname_{year}.xlsx in /data."
        )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day

    return df
