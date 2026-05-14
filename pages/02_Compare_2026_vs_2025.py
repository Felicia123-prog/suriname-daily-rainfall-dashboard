import streamlit as st
from utils.load_data import load_rr
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

st.title("Vergelijking Dagelijkse Neerslag – 2026 vs 2025")

# --- Maandselectie ---
month = st.selectbox("Kies maand", list(range(1, 13)))

df26 = load_rr(2026)
df25 = load_rr(2025)

d26 = df26[df26["month"] == month]
d25 = df25[df25["month"] == month]

# Tabs zoals je oude dashboard
tab1, tab2, tab3 = st.tabs([
    "Dagelijkse Vergelijking",
    "Verschil-Heatmap",
    "Verschil-Statistieken"
])

# --- TAB 1: Dagelijkse vergelijking ---
with tab1:
    st.subheader(f"Vergelijking – Maand {month}")

    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(d26["day"], d26["RR"], label="2026", color="#1f77b4")
    ax.plot(d25["day"], d25["RR"], label="2025", color="#ff7f0e")
    ax.set_ylabel("mm")
    ax.set_xlabel("Dag")
    ax.legend()
    st.pyplot(fig)

# --- TAB 2: Verschil-heatmap ---
with tab2:
    st.subheader("Verschil-Heatmap (2026 - 2025)")

    pivot26 = df26.pivot(index="month", columns="day", values="RR")
    pivot25 = df25.pivot(index="month", columns="day", values="RR")
    diff = pivot26 - pivot25

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(diff, cmap="coolwarm", center=0, ax=ax)
    st.pyplot(fig)

# --- TAB 3: Verschil-statistieken ---
with tab3:
    st.subheader(f"Verschillen – Maand {month}")

    stats = {
        "Verschil totaal (mm)": d26["RR"].sum() - d25["RR"].sum(),
        "Verschil gemiddelde": d26["RR"].mean() - d25["RR"].mean(),
        "Verschil natte dagen": (d26["RR"] >= 1).sum() - (d25["RR"] >= 1).sum(),
        "Verschil zware dagen (≥50mm)": (d26["RR"] >= 50).sum() - (d25["RR"] >= 50).sum(),
        "Verschil extreme dagen (≥100mm)": (d26["RR"] >= 100).sum() - (d25["RR"] >= 100).sum(),
    }

    st.json(stats)

