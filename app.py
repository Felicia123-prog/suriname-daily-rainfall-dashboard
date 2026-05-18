import streamlit as st
import pandas as pd
import plotly.express as px
from utils.load_data import load_rr
from utils.seasons import assign_season

st.set_page_config(page_title="Suriname Rainfall Comparison", layout="wide")

# ---------------------------------------------------------
# TITEL
# ---------------------------------------------------------
st.title("🌧️ Suriname — Dagelijkse Neerslag per Station & Landelijk Gemiddelde (WMO‑Conform) — Vergelijking 2025–2026")

# ---------------------------------------------------------
# MODE SELECTIE
# ---------------------------------------------------------
mode = st.radio(
    "Kies weergave:",
    ["Geheel Suriname (WMO‑gemiddelde)", "Per station"],
    horizontal=True
)

# ---------------------------------------------------------
# MAAND SELECTIE
# ---------------------------------------------------------
month_names = {
    1: "Januari", 2: "Februari", 3: "Maart", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Augustus",
    9: "September", 10: "Oktober", 11: "November", 12: "December"
}

month = st.selectbox("Kies maand:", list(month_names.keys()), format_func=lambda x: month_names[x])

# ---------------------------------------------------------
# DATA LADEN
# ---------------------------------------------------------
df_2026 = load_rr(2026)
df_2025 = load_rr(2025)

df_2026["season"] = df_2026.apply(assign_season, axis=1)
df_2025["season"] = df_2025.apply(assign_season, axis=1)

df_2026_m = df_2026[df_2026["month"] == month]
df_2025_m = df_2025[df_2025["month"] == month]

# ---------------------------------------------------------
# MODE 1 — GEHEEL SURINAME (WMO GEMIDDELDE)
# ---------------------------------------------------------
if mode == "Geheel Suriname (WMO‑gemiddelde)":

    # Dagelijkse WMO-gemiddelden (1 decimaal)
    df26_daily = df_2026_m.groupby("day")["RR"].mean().round(1).reset_index()
    df25_daily = df_2025_m.groupby("day")["RR"].mean().round(1).reset_index()

    # Aantal stations
    stations_2026 = df_2026_m["StationID"].nunique()
    stations_2025 = df_2025_m["StationID"].nunique()

    st.info(
        f"📡 Beschikbare stations — 2026: **{stations_2026}** | 2025: **{stations_2025}**"
    )

    # -----------------------------
    # STATISTIEKEN (ALLEEN 3)
    # -----------------------------
    colA, colB = st.columns(2)

    with colA:
        st.subheader(f"📊 Statistieken — 2026 ({month_names[month]})")
        st.metric("Totaal (mm)", round(df26_daily["RR"].sum(), 1))
        st.metric("Gemiddelde (mm/dag)", round(df26_daily["RR"].mean(), 1))
        st.metric("Max dagwaarde (mm)", df26_daily["RR"].max().round(1))

    with colB:
        st.subheader(f"📊 Statistieken — 2025 ({month_names[month]})")
        st.metric("Totaal (mm)", round(df25_daily["RR"].sum(), 1))
        st.metric("Gemiddelde (mm/dag)", round(df25_daily["RR"].mean(), 1))
        st.metric("Max dagwaarde (mm)", df25_daily["RR"].max().round(1))

    # -----------------------------
    # GRAFIEKEN + SEIZOEN
    # -----------------------------
    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(df26_daily, x="day", y="RR",
                      labels={"day": "Dag", "RR": "Neerslag (mm)"},
                      title=f"2026 — {month_names[month]}")
        st.plotly_chart(fig1, use_container_width=True)

        season_2026 = df_2026_m["season"].iloc[0]
        st.caption(f"🌱 Seizoen 2026: **{season_2026}**")

    with col2:
        fig2 = px.bar(df25_daily, x="day", y="RR",
                      labels={"day": "Dag", "RR": "Neerslag (mm)"},
                      title=f"2025 — {month_names[month]}")
        st.plotly_chart(fig2, use_container_width=True)

        season_2025 = df_2025_m["season"].iloc[0]
        st.caption(f"🌱 Seizoen 2025: **{season_2025}**")

# ---------------------------------------------------------
# MODE 2 — PER STATION
# ---------------------------------------------------------
else:
    station = st.selectbox("Kies station:", sorted(df_2026["StationID"].unique()))

    df26_s = df_2026_m[df_2026_m["StationID"] == station].copy()
    df25_s = df_2025_m[df_2025_m["StationID"] == station].copy()

    df26_s["RR"] = df26_s["RR"].round(1)
    df25_s["RR"] = df25_s["RR"].round(1)

    # -----------------------------
    # STATISTIEKEN (ALLEEN 3)
    # -----------------------------
    colA, colB = st.columns(2)

    with colA:
        st.subheader(f"📊 Statistieken — 2026 ({station})")
        st.metric("Totaal (mm)", round(df26_s["RR"].sum(), 1))
        st.metric("Gemiddelde (mm/dag)", round(df26_s["RR"].mean(), 1))
        st.metric("Max dagwaarde (mm)", df26_s["RR"].max().round(1))

    with colB:
        st.subheader(f"📊 Statistieken — 2025 ({station})")
        st.metric("Totaal (mm)", round(df25_s["RR"].sum(), 1))
        st.metric("Gemiddelde (mm/dag)", round(df25_s["RR"].mean(), 1))
        st.metric("Max dagwaarde (mm)", df25_s["RR"].max().round(1))

    # -----------------------------
    # GRAFIEKEN + SEIZOEN
    # -----------------------------
    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(df26_s, x="day", y="RR",
                      labels={"day": "Dag", "RR": "Neerslag (mm)"},
                      title=f"2026 — {station}")
        st.plotly_chart(fig1, use_container_width=True)

        season_2026 = df26_s["season"].iloc[0]
        st.caption(f"🌱 Seizoen 2026: **{season_2026}**")

    with col2:
        fig2 = px.bar(df25_s, x="day", y="RR",
                      labels={"day": "Dag", "RR": "Neerslag (mm)"},
                      title=f"2025 — {station}")
        st.plotly_chart(fig2, use_container_width=True)

        season_2025 = df25_s["season"].iloc[0]
        st.caption(f"🌱 Seizoen 2025: **{season_2025}**")
