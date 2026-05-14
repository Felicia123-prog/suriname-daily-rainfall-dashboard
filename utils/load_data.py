import pandas as pd
import os

def load_rr(year):
    csv_path = f"data/rr_{year}.csv"
    excel_path = f"data/Rainfall_Data_Suriname_{year}.xlsx"

    # 1. Als CSV bestaat én niet leeg is → gebruik CSV
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 10:
        df = pd.read_csv(csv_path)

    # 2. Anders: lees Excel → maak CSV → gebruik CSV
    elif os.path.exists(excel_path):
        df = pd.read_excel(excel_path)
        df.to_csv(csv_path, index=False)

    # 3. Geen data gevonden → foutmelding
    else:
        raise FileNotFoundError(
            f"Geen data gevonden voor jaar {year}. "
            f"Upload Rainfall_Data_Suriname_{year}.xlsx in /data."
        )

    # Datumkolom verwerken
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day

    return df
