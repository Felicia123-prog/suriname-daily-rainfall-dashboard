import pandas as pd
import os

def load_rr(year):
    csv_path = f"data/rr_{year}.csv"
    excel_path = f"data/Rainfall_Data_Suriname_{year}.xlsx"

    # 1. Gebruik CSV als die bestaat en niet leeg is
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 10:
        df = pd.read_csv(csv_path)

    # 2. Anders: lees Excel (alle sheets)
    elif os.path.exists(excel_path):
        xls = pd.ExcelFile(excel_path)
        frames = []

        for sheet in xls.sheet_names:
            temp = pd.read_excel(excel_path, sheet_name=sheet)

            # --- Kolomnamen automatisch herkennen ---
            colmap = {}

            for c in temp.columns:
                cl = c.lower()

                # Datum
                if cl in ["date", "datum", "obsdatetime", "datetime"]:
                    colmap[c] = "date"

                # Neerslag
                if cl in ["rainfall (mm)", "rainfall", "rr", "rain", "precip", "rain_mm"]:
                    colmap[c] = "RR"

                # Latitude
                if cl in ["latitude", "lat"]:
                    colmap[c] = "Latitude"

                # Longitude
                if cl in ["longitude", "lon", "long"]:
                    colmap[c] = "Longitude"

                # Station ID
                if cl in ["stationid", "station", "station_id"]:
                    colmap[c] = "StationID"

            temp = temp.rename(columns=colmap)

            # Alleen kolommen die we nodig hebben
            keep = [c for c in ["date", "RR", "Latitude", "Longitude", "StationID"] if c in temp.columns]
            temp = temp[keep]

            frames.append(temp)

        df = pd.concat(frames, ignore_index=True)

        # CSV opslaan
        df.to_csv(csv_path, index=False)

    else:
        raise FileNotFoundError(
            f"Geen data gevonden voor jaar {year}. "
            f"Upload Rainfall_Data_Suriname_{year}.xlsx in /data."
        )

    # Datum verwerken
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day

    return df
