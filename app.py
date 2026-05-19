import streamlit as st
import pandas as pd
import plotly.express as px
from utils.load_data import load_rr
from utils.seasons import assign_season

st.set_page_config(page_title="Maandelijkse Neerslagrapportage 2025–2026", layout="wide")

# ---------------------------------------------------------
# SUPER-UNIFORMIZER — houdt ALLEEN de juiste kolommen
# ---------------------------------------------------------
def uniformize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 1. Kolomnamen normaliseren
    df.columns = [c.strip().lower() for c in df.columns]

    # 2. Alleen relevante kolommen behouden
    keep = ["stationid", "rr", "date", "year", "month", "day"]
    df = df[[c for c in df.columns if c in keep]]

    # 3. StationID
    if "stationid" not in df.columns:
        df["stationid"] = None

    # 4. RR
    if "rr" not in df.columns:
        df["rr"] = None
    df["rr"] = pd.to_numeric(df["rr"], errors="coerce")

    # 5. Datum
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        df["date"] = pd.to_datetime(df[["year", "month", "day"]], errors="coerce")

    # 6. Year / Month / Day opnieuw afleiden
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day

    return df


# ---------------------------------------------------------
# Analysefunctie
# ---------------------------------------------------------
def generate_analysis(total26, total25, avg26, avg25,
                      max_avg26, max_avg25,
                      max_station26, max_station25,
                      season, month_name):

    diff_total = total26 - total25
    perc_total = (diff_total / total25 * 100) if total25 > 0 else 0

    if diff_total > 0:
        trend_text = f"In {month_name} 2026 viel {abs(perc_total):.1f}% meer neerslag dan in {month_name} 2025."
    elif diff_total < 0:
        trend_text = f"In {month_name} 2026 viel {abs(perc_total):.1f}% minder neerslag dan in {month_name} 2025."
    else:
        trend_text = f"In {month_name} 2026 viel ongeveer dezelfde hoeveelheid neerslag als in {month_name} 2025."

    if max_station26 > max_station25:
        intensity_text = (
            f"De hoogste stationwaarde in 2026 was {max_station26:.1f} mm, "
            f"tegenover {max_station25:.1f} mm in 2025. Dit wijst op lokaal intensere buien in 2026."
        )
    elif max_station26 < max_station25:
        intensity_text = (
            f"De hoogste stationwaarde in 2026 was {max_station26:.1f} mm, "
            f"lager dan de {max_station25:.1f} mm in 2025."
        )
    else:
        intensity_text = (
            f"De hoogste stationwaarden waren gelijk ({max_station26:.1f} mm)."
        )

    summary = (
        f"{month_name} valt in de **{season}**, wat helpt om de regenpatronen te interpreteren."
    )

    return f"""
### 📘 Analyse — {month_name}

**Regenvalverschil:**  
{trend_text}

**Intensiteit:**  
De hoogste *gemiddelde* dagneerslag was {max_avg26:.1f} mm in 2026 en {max_avg25:.1f} mm in 2025.  
{intensity_text}

**Seizoenscontext:**  
{summary}
"""


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
st.title("🌧️ Maandelijkse Neerslagrapportage voor Suriname — 2025 en 2026")

mode = st.radio(
    "Kies weergave:",
    ["Geheel Suriname (WMO‑gemiddelde)", "Per station"],
    horizontal=True
)

month_names = {
    1: "Januari", 2: "Februari", 3: "Maart", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Augustus",
    9: "September", 10: "Oktober", 11: "November", 12: "December"
}

month = st.selectbox("Kies maand:", list(month_names.keys()), format_func=lambda x: month_names[x])

# ---------------------------------------------------------
# Data laden + uniformiseren
# ---------------------------------------------------------
df_2025_raw = load_rr(2025)
df_2026_raw = load_rr(2026)

df_2025 = uniformize(df_2025_raw)
df_2026 = uniformize(df_2026_raw)

df_2025["season"] = df_2025.apply(assign_season, axis=1)
df_2026["season"] = df_2026.apply(assign_season, axis=1)

df_2025_m = df_2025[df_2025["month"] == month]
df_2026_m = df_2026[df_2026["month"] == month]

# ---------------------------------------------------------
# Mode 1 — Geheel Suriname
# ---------------------------------------------------------
if mode == "Geheel Suriname (WMO‑gemiddelde)":

    df26_daily = df_2026_m.groupby("day")["rr"].mean().round(1).reset_index()
    df25_daily = df_2025_m.groupby("day")["rr"].mean().round(1).reset_index()

    stations_2026 = df_2026_m["stationid"].nunique()
    stations_2025 = df_2025_m["stationid"].nunique()

    st.info(
        f"📡 Beschikbare stations in {month_names[month]} — 2026: **{stations_2026}** | 2025: **{stations_2025}**"
    )

    colA, colB = st.columns(2)

    total26 = df26_daily["rr"].sum()
    total25 = df25_daily["rr"].sum()
    avg26 = df26_daily["rr"].mean()
    avg25 = df25_daily["rr"].mean()

    max_avg26 = df26_daily["rr"].max() if not df26_daily.empty else 0
    max_avg25 = df25_daily["rr"].max() if not df25_daily.empty else 0

    max_station26 = df_2026_m["rr"].max() if not df_2026_m.empty else 0
    max_station25 = df_2025_m["rr"].max() if not df_2025_m.empty else 0

    with colA:
        st.subheader(f"📊 Statistieken — 2026 ({month_names[month]})")
        st.metric("Totaal (mm)", round(total26, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg26, 1))
        st.metric("Max gemiddelde dagneerslag (mm)", round(max_avg26, 1))

    with colB:
        st.subheader(f"📊 Statistieken — 2025 ({month_names[month]})")
        st.metric("Totaal (mm)", round(total25, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg25, 1))
        st.metric("Max gemiddelde dagneerslag (mm)", round(max_avg25, 1))

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(df26_daily, x="day", y="rr",
                      labels={"day": "Dag", "rr": "Neerslag (mm)"},
                      title=f"2026 — {month_names[month]}")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(df25_daily, x="day", y="rr",
                      labels={"day": "Dag", "rr": "Neerslag (mm)"},
                      title=f"2025 — {month_names[month]}")
        st.plotly_chart(fig2, use_container_width=True)

    season_for_text = (
        df_2026_m["season"].iloc[0]
        if not df_2026_m.empty
        else df_2025_m["season"].iloc[0]
        if not df_2025_m.empty
        else "het betreffende seizoen"
    )

    st.markdown(
        generate_analysis(
            total26, total25,
            avg26, avg25,
            max_avg26, max_avg25,
            max_station26, max_station25,
            season_for_text,
            month_names[month]
        )
    )

# ---------------------------------------------------------
# Mode 2 — Per station
# ---------------------------------------------------------
else:
    all_stations = sorted(set(df_2025["stationid"].dropna()).union(df_2026["stationid"].dropna()))
    station = st.selectbox("Kies station:", all_stations)

    df26_s = df_2026_m[df_2026_m["stationid"] == station].copy()
    df25_s = df_2025_m[df_2025_m["stationid"] == station].copy()

    df26_s["rr"] = df26_s["rr"].round(1)
    df25_s["rr"] = df25_s["rr"].round(1)

    total26 = df26_s["rr"].sum()
    total25 = df25_s["rr"].sum()
    avg26 = df26_s["rr"].mean()
    avg25 = df25_s["rr"].mean()

    max26 = df26_s["rr"].max() if not df26_s.empty else 0
    max25 = df25_s["rr"].max() if not df25_s.empty else 0

    colA, colB = st.columns(2)

    with colA:
        st.subheader(f"
