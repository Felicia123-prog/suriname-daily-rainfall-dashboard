import pandas as pd

def load_rr(year):
    df = pd.read_csv(f"data/rr_{year}.csv")
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    return df

