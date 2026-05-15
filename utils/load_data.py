import pandas as pd
import os

def load_rr(year):
    csv_path = f"data/rr_{year}.csv"
    excel_path = f"data/Rainfall_Data_Suriname_{year}.xlsx"

    # 1. Als CSV bestaat → gebruik die
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 10:
        df = pd.read_csv(csv_path)

    # 2. Anders: lees Excel (voor nu: alleen 2026‑structuur)
    elif os.path.exists(excel_path):
        # Als er meerdere sheets zijn: alles inlezen en onder elkaar plakken
        xls = pd.ExcelFile(excel_path)
        frames = []
        for sheet in xls.sheet_names:
            temp = pd.read_excel(excel_path, sheet_name=sheet)

            # Verwacht deze kolommen:
            # Date, Latitude, Longitude, StationID, Rainfall (mm)
            if "Date" not in temp.columns or "Rainfall (mm)" not in temp.columns:
                continue  # sheet overslaan als hij niet deze structuur heeft

            temp = temp[["Date", "Latitude", "Longitude", "StationID", "Rainfall (mm)"]].copy()
            temp = temp.rename(columns={
                "Date": "date",
                "Rainfall (mm)": "RR"
            })
            frames.append(temp)

        if not frames:
            raise ValueError("Geen enkele sheet bevat kolommen 'Date' en 'Rainfall (mm)'.")

        df = pd.concat(frames, ignore_index=True)

        # RR numeriek maken
        df["RR"] = pd.to_numeric(df["RR"], errors="coerce").fillna(0)

        # CSV opslaan voor volgende keer
        df.to_csv(csv_path, index=False)

    else:
        raise FileNotFoundError(
            f"Geen data gevonden voor jaar {year}. "
            f"Zorg dat Rainfall_Data_Suriname_{year}.xlsx in /data staat."
        )

    # Datum verwerken
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day

    return df
