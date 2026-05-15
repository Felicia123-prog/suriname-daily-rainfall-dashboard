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

            # --- Kolomnamen normaliseren ---
            rename_map = {}
            for c in temp.columns:
                cl = c.lower().strip()

                # Datum
                if cl in ["date", "datum", "obsdatetime", "datetime"]:
                    rename_map[c] = "date"

                # Neerslag (alle varianten)
                if cl in [
                    "rainfall (mm)", "rainfall", "rr", "rr(mm)", "rain_mm",
                    "precip", "precipitation", "rain"
                ]:
                    rename_map[c] = "RR"

                # Latitude / Longitude
                if cl in ["latitude", "lat"]:
                    rename_map[c] = "Latitude"
                if cl in ["longitude", "lon", "long"]:
                    rename_map[c] = "Longitude"

                # Station ID
                if cl in ["stationid", "station", "station_id"]:
                    rename_map[c] = "StationID"

            temp = temp.rename(columns=rename_map)

            # Alleen relevante kolommen
            keep = [c for c in ["date", "RR", "Latitude", "Longitude", "StationID"] if c in temp.columns]
            if not keep:
                continue

            temp = temp[keep]
            frames.append(temp)

        if not frames:
            raise ValueError(f"Geen bruikbare neerslagkolom gevonden in {year}.")

        df = pd.concat(frames, ignore_index=True)

        # RR numeriek maken
        if "RR" not in df.columns:
            df["RR"] = 0

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
