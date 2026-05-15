import streamlit as st
import pandas as pd
import plotly.express as px
from utils.load_data import load_rr
from utils.seasons import assign_season

st.set_page_config(page_title="Suriname Rainfall Comparison", layout="wide")

st.title("🌧️ Dagelijkse Neerslag Vergelijking — Suriname")
st.write("Vergelijk dagelijkse neerslag tussen 2025 en 2026 per maand.")

# -----------------------------
# MAAND SELECTIE
# -----------------------------
month_names = {
    1: "Januari", 2: "Februari", 3: "Maart", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Augustus",
    9: "September", 10: "Oktober", 11: "November", 12: "December"
}

month = st.selectbox("Kies maand:", list(month_names.keys()), format_func=lambda x: month_names[x])

# -----------------------------
# DATA LADEN
# -----------------------------
df_2026 = load_rr(2026)
df_2025 = load_rr(2025)

df_2026["season"] = df_2026.apply(assign_season, axis=1)
df_2025["season"] = df_2025.apply(assign_season, axis=1)

# Filter op maand
df_2026_m = df_2026[df_2026["month"] == month]
df_2025_m = df_2025[df_2025["month"] == month]

# -----------------------------
# STATISTIEKEN
# -----------------------------
colA, colB = st.columns(2)

with colA:
    st.subheader(f"📊 Statistieken — 2026 ({month_names[month]})")
    st.metric("Totaal (mm)", round(df_2026_m["RR"].sum(), 1))
    st.metric("Gemiddelde (mm/dag)", round(df_2026_m["RR"].mean(), 2))
    st.metric("Natte dagen (≥1mm)", int((df_2026_m["RR"] >= 1).sum()))
    st.metric("Zware dagen (≥50mm)", int((df_2026_m["RR"] >= 50).sum()))

with colB:
    st.subheader(f"📊 Statistieken — 2025 ({month_names[month]})")
    st.metric("Totaal (mm)", round(df_2025_m["RR"].sum(), 1))
    st.metric("Gemiddelde (mm/dag)", round(df_2025_m["RR"].mean(), 2))
    st.metric("Natte dagen (≥1mm)", int((df_2025_m["RR"] >= 1).sum()))
    st.metric("Zware dagen (≥50mm)", int((df_2025_m["RR"] >= 50).sum()))

# -----------------------------
# GRAFIEKEN NAAST ELKAAR
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"📅 Dagelijkse neerslag — 2026 ({month_names[month]})")
    fig1 = px.bar(
        df_2026_m,
        x="day",
        y="RR",
        labels={"day": "Dag", "RR": "Neerslag (mm)"},
        title=f"2026 — {month_names[month]}"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader(f"📅 Dagelijkse neerslag — 2025 ({month_names[month]})")
    fig2 = px.bar(
        df_2025_m,
        x="day",
        y="RR",
        labels={"day": "Dag", "RR": "Neerslag (mm)"},
        title=f"2025 — {month_names[month]}"
    )
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# SEIZOEN INFO
# -----------------------------
st.markdown("### 🌦️ Seizoensindeling")
st.info(f"**2026:** {df_2026_m['season'].iloc[0] if len(df_2026_m)>0 else 'Onbekend'}")
st.info(f"**2025:** {df_2025_m['season'].iloc[0] if len(df_2025_m)>0 else 'Onbekend'}")
