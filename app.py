import streamlit as st
import pandas as pd
import plotly.express as px
from utils.load_data import load_rr
from utils.seasons import assign_season

st.set_page_config(page_title="Suriname Rainfall Comparison", layout="wide")

st.title("🌧️ Dagelijkse Neerslag — Suriname (WMO‑conform)")

# -----------------------------
# MODE SELECTIE
# -----------------------------
mode = st.radio(
    "Kies weergave:",
    ["Geheel Suriname (WMO‑gemiddelde)", "Per station / district"],
    horizontal=True
)

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

df_2026_m = df_2026[df_2026["month"] == month]
df_2025_m = df_2025[df_2025["month"] == month]

# -----------------------------
# MODE 1 — GEHEEL SURINAME (WMO GEMIDDELDE)
# -----------------------------
if mode == "Geheel Suriname (WMO‑gemiddelde)":

    # Dagelijkse WMO-gemiddelden
    df26_daily = df_2026_m.groupby("day")["RR"].mean().reset_index()
    df25_daily = df_2025_m.groupby("day")["RR"].mean().reset_index()

    # Statistieken
    colA, colB = st.columns(2)

    with colA:
        st.subheader(f"📊 Statistieken — 2026 ({month_names[month]})")
        st.metric("Totaal (mm)", round(df26_daily["RR"].sum(), 1))
        st.metric("Gemiddelde (mm/dag)", round(df26_daily["RR"].mean(), 2))
        st.metric("Natte dagen (≥1mm)", int((df26_daily["RR"] >= 1).sum()))
        st.metric("Zware dagen (≥50mm)", int((df26_daily["RR"] >= 50).sum()))

    with colB:
        st.subheader(f"📊 Statistieken — 2025 ({month_names[month]})")
        st.metric("Totaal (mm)", round(df25_daily["RR"].sum(), 1))
        st.metric("Gemiddelde (mm/dag)", round(df25_daily["RR"].mean(), 2))
        st.metric("Natte dagen (≥1mm)", int((df25_daily["RR"] >= 1).sum()))
        st.metric("Zware dagen (≥50mm)", int((df25_daily["RR"] >= 50).sum()))

    # Grafieken
    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(df26_daily, x="day", y="RR", title=f"2026 — {month_names[month]}")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(df25_daily, x="day", y="RR", title=f"2025 — {month_names[month]}")
        st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# MODE 2 — PER STATION / DISTRICT
# -----------------------------
else:
    choice = st.selectbox("Kies weergave:", ["Per station"])

    if choice == "Per station":
        station = st.selectbox("Kies station:", sorted(df_2026["StationID"].unique()))

        df26_s = df_2026_m[df_2026_m["StationID"] == station]
        df25_s = df_2025_m[df_2025_m["StationID"] == station]

        colA, colB = st.columns(2)

        with colA:
            st.subheader(f"📊 Statistieken — 2026 ({station})")
            st.metric("Totaal (mm)", round(df26_s["RR"].sum(), 1))
            st.metric("Gemiddelde (mm/dag)", round(df26_s["RR"].mean(), 2))
            st.metric("Natte dagen (≥1mm)", int((df26_s["RR"] >= 1).sum()))
            st.metric("Zware dagen (≥50mm)", int((df26_s["RR"] >= 50).sum()))

        with colB:
            st.subheader(f"📊 Statistieken — 2025 ({station})")
            st.metric("Totaal (mm)", round(df25_s["RR"].sum(), 1))
            st.metric("Gemiddelde (mm/dag)", round(df25_s["RR"].mean(), 2))
            st.metric("Natte dagen (≥1mm)", int((df25_s["RR"] >= 1).sum()))
            st.metric("Zware dagen (≥50mm)", int((df25_s["RR"] >= 50).sum()))

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.bar(df26_s, x="day", y="RR", title=f"2026 — {station}")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.bar(df25_s, x="day", y="RR", title=f"2025 — {station}")
            st.plotly_chart(fig2, use_container_width=True)
