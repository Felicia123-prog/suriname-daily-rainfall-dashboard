import pandas as pd

def load_rr(year):
    if year == 2026:
        path = r"C:\Users\Felicia\OneDrive\Desktop\Rainfall_Data_Suriname_2026.xlsx"
    else:
        path = r"C:\Users\Felicia\OneDrive\Desktop\Rainfall_Data_Suriname_2025.xlsx"

    xls = pd.ExcelFile(path)

    frames = []

    for sheet in xls.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet)

        # Harmoniseer kolomnamen
        df.columns = [c.strip().lower() for c in df.columns]

        # Zorg dat verplichte kolommen bestaan
        for col in ["date", "latitude", "longitude", "stationid"]:
            if col not in df.columns:
                df[col] = None

        # Zoek neerslagkolom
        rain_col = None
        for c in df.columns:
            if any(k in c for k in ["rain", "precip", "rr", "waarde", "value"]):
                rain_col = c
                break

        if rain_col is None:
            continue

        df = df[["date", "latitude", "longitude", "stationid", rain_col]]
        df = df.rename(columns={rain_col: "rain_raw"})

        frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)
