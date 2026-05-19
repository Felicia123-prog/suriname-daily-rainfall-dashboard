import streamlit as st
import pandas as pd
import plotly.express as px
from utils.load_data import load_rr
from utils.seasons import assign_season

st.set_page_config(page_title="Maandelijkse Neerslagrapportage 2025–2026", layout="wide")

# ---------------------------------------------------------
# TITEL
# ---------------------------------------------------------
st.title("🌧️ Maandelijkse Neerslagrapportage voor Suriname — 2025 en 2026 (WMO‑Conform)")

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
# ANALYSE FUNCTIE
# ---------------------------------------------------------
def generate_analysis(total26, total25, avg26, avg25, max26, max25, season, month_name):

    diff_total = total26 - total25
    perc_total = (diff_total / total25 * 100) if total25 > 0 else 0

    diff_max = max26 - max25

    trend = "natter" if diff_total > 0 else "droger"
    intensity = "intensievere buien" if diff_max > 0 else "minder intense buien"

    return f"""
### 📘 Analyse — {month_name}

**Regenvalverschil:**  
In {month_name} 2026 viel **{abs(perc_total):.1f}% {trend}** neerslag dan in {month_name} 2025  
({total26:.1f} mm vs {total25:.1f} mm).

**Intensiteit:**  
De natste dag in 2026 bereikte **{max26:.1f} mm**, vergeleken met **{max25:.1f} mm** in 2025.  
Dit wijst op **{intensity}** in 2026.

**Seizoenscontext:**  
{month_name} valt in de **{season}**, wat helpt om de regenpatronen te duiden.

**Samenvatting:**  
{month_name} 2026 was **{trend}** dan {month_name} 2025, met {intensity}.
"""

# ---------------------------------------------------------
# MODE 1 — GEHEEL SURINAME (WMO GEMIDDELDE)
# ---------------------------------------------------------
if mode == "Geheel Suriname (WMO‑gemiddelde)":

    # Dagelijkse WMO-gemiddelden (1 decimaal)
    df26_daily = df_2026_m.groupby("day")["RR"].mean().round(1).reset_index()
    df25_daily = df_2025_m.groupby("day")["RR"].mean().round(1).reset_index()

    # Aantal stations per maand (alleen stations met minstens 1 geldige RR)
    stations_2026 = df_2026_m.groupby("StationID")["RR"].apply(lambda x: x.notna().any()).sum()
    stations_2025 = df_2025_m.groupby("StationID")["RR"].apply(lambda x: x.notna().any()).sum()

    st.info(
        f"📡 Beschikbare stations in {month_names[month]} — 2026: **{stations_2026}** | 2025: **{stations_2025}**"
    )

    # -----------------------------
    # STATISTIEKEN (ALLEEN 3)
    # -----------------------------
    colA, colB = st.columns(2)

    total26 = df26_daily["RR"].sum()
    total25 = df25_daily["RR"].sum()
    avg26 = df26_daily["RR"].mean()
    avg25 = df25_daily["RR"].mean()
    max26 = df26_daily["RR"].max()
    max25 = df25_daily["RR"].max()

    with colA:
        st.subheader(f"📊 Statistieken — 2026 ({month_names[month]})")
        st.metric("Totaal (mm)", round(total26, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg26, 1))
        st.metric("Max gemiddelde dagneerslag (mm)", round(max26, 1))

    with colB:
        st.subheader(f"📊 Statistieken — 2025 ({month_names[month]})")
        st.metric("Totaal (mm)", round(total25, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg25, 1))
        st.metric("Max gemiddelde dagneerslag (mm)", round(max25, 1))

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

    # -----------------------------
    # ANALYSE
    # -----------------------------
    st.markdown(generate_analysis(total26, total25, avg26, avg25, max26, max25, season_2026, month_names[month]))

# ---------------------------------------------------------
# MODE 2 — PER STATION
# ---------------------------------------------------------
else:
    station = st.selectbox("Kies station:", sorted(df_2026["StationID"].unique()))

    df26_s = df_2026_m[df_2026_m["StationID"] == station].copy()
    df25_s = df_2025_m[df_2025_m["StationID"] == station].copy()

    df26_s["RR"] = df26_s["RR"].round(1)
    df25_s["RR"] = df25_s["RR"].round(1)

    total26 = df26_s["RR"].sum()
    total25 = df25_s["RR"].sum()
    avg26 = df26_s["RR"].mean()
    avg25 = df25_s["RR"].mean()
    max26 = df26_s["RR"].max()
    max25 = df25_s["RR"].max()

    # -----------------------------
    # STATISTIEKEN (ALLEEN 3)
    # -----------------------------
    colA, colB = st.columns(2)

    with colA:
        st.subheader(f"📊 Statistieken — 2026 ({station})")
        st.metric("Totaal (mm)", round(total26, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg26, 1))
        st.metric("Max dagneerslag (mm)", round(max26, 1))

    with colB:
        st.subheader(f"📊 Statistieken — 2025 ({station})")
        st.metric("Totaal (mm)", round(total25, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg25, 1))
        st.metric("Max dagneerslag (mm)", round(max25, 1))

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

    # -----------------------------
    # ANALYSE
    # -----------------------------
    st.markdown(generate_analysis(total26, total25, avg26, avg25, max26, max25, season_2026, month_names[month]))
