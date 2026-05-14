import streamlit as st
from utils.load_data import load_rr
from utils.seasons import assign_season
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

st.title("Dagelijkse Neerslag – Kies Jaar & Maand")

# --- Jaarselectie ---
year = st.selectbox("Kies jaar", [2026, 2025])

# --- Maandselectie ---
month = st.selectbox("Kies maand", list(range(1, 13)))

df = load_rr(year)
df["season"] = df.apply(assign_season, axis=1)

df_month = df[df["month"] == month]

# Tabs zoals je oude dashboard
tab1, tab2, tab3, tab4 = st.tabs([
    "Staafdiagram",
    "Regenval Matrix",
    "Statistieken",
    "Seizoenen"
])

# --- TAB 1: Staafdiagram ---
with tab1:
    st.subheader(f"Staafdiagram – {year}, maand {month}")

    fig, ax = plt.subplots(figsize=(10, 3))
    ax.bar(df_month['day'], df_month['RR'], color="#1f77b4")
    ax.set_ylabel("mm")
    ax.set_xlabel("Dag")
    st.pyplot(fig)

# --- TAB 2: Heatmap ---
with tab2:
    st.subheader(f"Heatmap – {year}")

    pivot = df.pivot(index='month', columns='day', values='RR')

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(pivot, cmap="Blues", ax=ax)
    st.pyplot(fig)

# --- TAB 3: Statistieken ---
with tab3:
    st.subheader(f"Statistieken – {year}, maand {month}")

    stats = {
        "Totaal (mm)": df_month["RR"].sum(),
        "Gemiddelde per dag": df_month["RR"].mean(),
        "Mediaan per dag": df_month["RR"].median(),
        "Droge dagen (RR=0)": (df_month["RR"] == 0).sum(),
        "Natte dagen (RR≥1)": (df_month["RR"] >= 1).sum(),
        "Zware dagen (RR≥50)": (df_month["RR"] >= 50).sum(),
        "Extreme dagen (RR≥100)": (df_month["RR"] >= 100).sum(),
        "Max dagwaarde": df_month["RR"].max(),
    }

    st.json(stats)

# --- TAB 4: Seizoenen ---
with tab4:
    st.subheader(f"Seizoensanalyse – {year}")

    season_stats = df.groupby("season").agg(
        total_rr=("RR", "sum"),
        mean_rr=("RR", "mean"),
        wet_days=("RR", lambda x: (x >= 1).sum()),
        heavy_days=("RR", lambda x: (x >= 50).sum()),
        extreme_days=("RR", lambda x: (x >= 100).sum())
    )

    st.dataframe(season_stats)

