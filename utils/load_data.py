import pandas as pd
import os

def load_rr(year):
    filename = (
        "Rainfall_Data_Suriname_2026.xlsx"
        if year == 2026
        else "Rainfall_Data_Suriname_2025.xlsx"
    )

    # Mogelijke paden waar Streamlit of lokaal het bestand kan plaatsen
    possible_paths = [
        f"data/{filename}",
        f"./data/{filename}",
        f"/mount/src/suriname-daily-rainfall-dashboard/data/{filename}",
        f"/app/data/{filename}",
        filename  # fallback
    ]

    # Zoek het eerste pad dat bestaat
    for path in possible_paths:
        if os.path.exists(path):
            xls = pd.ExcelFile(path)
            frames = []

            for sheet in xls.sheet_names:
                df = pd.read_excel(path, sheet_name=sheet)

                df.columns = [c.strip().lower() for c in df.columns]

                # verplichte kolommen
                for col in ["date", "latitude", "longitude", "stationid"]:
                    if col not in df.columns:
                        df[col] = None

                # neerslagkolom zoeken
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

            if frames:
                return pd.concat(frames, ignore_index=True)
            else:
                return pd.DataFrame()

    # Als geen enkel pad werkt → duidelijke foutmelding
    raise FileNotFoundError(
        f"Kon het bestand {filename} niet vinden in een van de paden: {possible_paths}"
    )
