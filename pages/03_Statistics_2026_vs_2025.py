import streamlit as st
from utils.load_data import load_rr
from utils.seasons import assign_season
import pandas as pd

st.title("Statistieken – 2026 vs 2025")

df26 = load_rr(2026)
df25 = load_rr(2025)

df26["season"] = df26.apply(assign_season, axis=1)
df25["season"] = df25.apply(assign_season, axis=1)

# Tabs zoals je oude dashboard
tab1, tab2, tab3, tab4 = st.tabs([
    "Jaarstatistieken",
    "Maandstatistieken",
    "Seizoenen",
    "Verschillen"
])

# --- TAB 1: Jaarstatistieken ---
with tab1:
    st.subheader("Jaarstatistieken")

    def year_stats(df):
        return {
            "Totaal (mm)": df["RR"].sum(),
            "Gemiddelde per dag": df["RR"].mean(),
            "Mediaan per dag": df["RR"].median(),
            "Droge dagen (RR=0)": (df["RR"] == 0).sum(),
            "Natte dagen (RR≥1)": (df["RR"] >= 1).sum(),
            "Zware dagen (RR≥50)": (df["RR"] >= 50).sum(),
            "Extreme dagen (RR≥100)": (df["RR"] >= 100).sum(),
            "Max dagwaarde": df["RR"].max(),
        }

    st.write("### 2026")
    st.json(year_stats(df26))

    st.write("### 2025")
    st.json(year_stats(df25))

# --- TAB 2: Maandstatistieken ---
with tab2:
    st.subheader("Maandstatistieken")

    def month_stats(df):
        return df.groupby("month").agg(
            total_rr=("RR", "sum"),
            mean_rr=("RR", "mean"),
            wet_days=("RR", lambda x: (x >= 1).sum()),
            heavy_days=("RR", lambda x: (x >= 50).sum()),
            extreme_days=("RR", lambda x: (x >= 100).sum())
        )

    st.write("### 2026")
    st.dataframe(month_stats(df26))

    st.write("### 2025")
    st.dataframe(month_stats(df25))

# --- TAB 3: Seizoenen ---
with tab3:
    st.subheader("Seizoensanalyse")

    def season_stats(df):
        return df.groupby("season").agg(
            total_rr=("RR", "sum"),
            mean_rr=("RR", "mean"),
            wet_days=("RR", lambda x: (x >= 1).sum()),
            heavy_days=("RR", lambda x: (x >= 50).sum()),
            extreme_days=("RR", lambda x: (x >= 100).sum())
        )

    st.write("### 2026")
    st.dataframe(season_stats(df26))

    st.write("### 2025")
    st.dataframe(season_stats(df25))

# --- TAB 4: Verschillen ---
with tab4:
    st.subheader("Verschillen 2026 - 2025")

    st.write("### Seizoenen")
    st.dataframe(season_stats(df26) - season_stats(df25))

    st.write("### Maanden")
    st.dataframe(month_stats(df26) - month_stats(df25))

