import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Maandelijkse Neerslagrapportage 2025–2026", layout="wide")

# ---------------------------------------------------------
# HELPER: seizoen
# ---------------------------------------------------------
def season_from_month(m: int) -> str:
    if m in [12, 1, 2]:
        return "Kleine regentijd"
    if m in [3, 4]:
        return "Kleine droge tijd"
    if m in [5, 6, 7]:
        return "Grote regentijd"
    if m in [8, 9, 10, 11]:
        return "Grote droge tijd"
    return ""

# ---------------------------------------------------------
# DATA LADEN
# ---------------------------------------------------------
def load_rr(year: int) -> pd.DataFrame:
    filename = f"Rainfall_Data_Suriname_{year}.xlsx"
    path = os.path.join("data", filename)

    if not os.path.exists(path):
        st.error(f"Bestand niet gevonden: {path}")
        st.stop()

    xls = pd.ExcelFile(path)
    frames = []

    if year == 2025:
        df = pd.read_excel(path, sheet_name="RR_2025")
        df = df.rename(columns={
            "StationId": "stationid",
            "Station_Name": "station_name",
            "Lat": "latitude",
            "Lon": "longitude",
            "PRECIP": "rain_raw"
        })
        df["date"] = pd.to_datetime(df[["Year", "Month", "Day"]].astype(int), errors="coerce")
        df = df[["date", "latitude", "longitude", "stationid, "rain_raw"]]
        frames.append(df)

    else:
        for sheet in xls.sheet_names:
            df = pd.read_excel(path, sheet_name=sheet)
            df.columns = [c.strip().lower() for c in df.columns]

            for col in ["date", "latitude", "longitude", "stationid"]:
                if col not in df.columns:
                    df[col] = None

            rain_col = next((c for c in df.columns if "rain" in c or "precip" in c or c == "rr"), None)
            if rain_col is None:
                continue

            df = df[["date", "latitude", "longitude", "stationid", rain_col]]
            df = df.rename(columns={rain_col: "rain_raw"})
            frames.append(df)

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

# ---------------------------------------------------------
# UNIFORMIZER
# ---------------------------------------------------------
def uniformize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    raw = df["rain_raw"].astype(str).str.strip()
    raw = raw.str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii")
    raw = raw.str.replace(r"\s+", "", regex=True)

    df["is_cumulative"] = raw.str.contains("C", case=False)
    df["rr_value"] = pd.to_numeric(raw.str.replace(r"[cC].*", "", regex=True), errors="coerce")
    df["rr"] = df["rr_value"]
    df.loc[df["is_cumulative"], "rr"] = None

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day

    return df

# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
st.title("🌧️ Maandelijkse Neerslagrapportage voor Suriname — 2025 en 2026")

mode = st.radio(
    "Kies weergave:",
    ["Geheel Suriname (landelijk gemiddelde)", "Per station"],
    horizontal=True
)

month_names = {
    1: "Januari", 2: "Februari", 3: "Maart", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Augustus",
    9: "September", 10: "Oktober", 11: "November", 12: "December"
}

month = st.selectbox("Kies maand:", list(month_names.keys()), format_func=lambda x: month_names[x])

# ---------------------------------------------------------
# DATA LADEN
# ---------------------------------------------------------
df_2025 = uniformize(load_rr(2025))
df_2026 = uniformize(load_rr(2026))

df_2025_m = df_2025[df_2025["month"] == month]
df_2026_m = df_2026[df_2026["month"] == month]

# ---------------------------------------------------------
# MODE 1 — LANDELIJK GEMIDDELDE
# ---------------------------------------------------------
if mode == "Geheel Suriname (landelijk gemiddelde)":

    if df_2025_m.empty and df_2026_m.empty:
        st.warning("Geen landelijke gegevens beschikbaar voor beide jaren.")
        st.stop()

    if df_2025_m.empty:
        st.warning("Geen landelijke gegevens voor 2025.")
        st.stop()

    if df_2026_m.empty:
        st.warning("Geen landelijke gegevens voor 2026.")
        st.stop()

    df26_daily = df_2026_m.groupby("day")["rr"].mean().round(1).reset_index()
    df25_daily = df_2025_m.groupby("day")["rr"].mean().round(1).reset_index()

    stations_2026 = df_2026_m["stationid"].nunique()
    stations_2025 = df_2025_m["stationid"].nunique()

    st.info(f"📡 Beschikbare stations — 2026: **{stations_2026}** | 2025: **{stations_2025}**")

    colA, colB = st.columns(2)

    total26 = df_2026_m["rr_value"].sum()
    total25 = df_2025_m["rr_value"].sum()
    avg26 = df_2026_m["rr_value"].mean()
    avg25 = df_2025_m["rr_value"].mean()

    max_avg26 = df26_daily["rr"].max()
    max_avg25 = df25_daily["rr"].max()

    with colA:
        st.subheader(f"📊 Statistieken — 2026 ({month_names[month]})")
        st.metric("Totaal (mm)", round(total26, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg26, 1))
        st.metric("Hoogste dagwaarde (mm)", round(max_avg26, 1))

    with colB:
        st.subheader(f"📊 Statistieken — 2025 ({month_names[month]})")
        st.metric("Totaal (mm)", round(total25, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg25, 1))
        st.metric("Hoogste dagwaarde (mm)", round(max_avg25, 1))

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(px.bar(df26_daily, x="day", y="rr", title=f"2026 — {month_names[month]}"), use_container_width=True)

    with col2:
        st.plotly_chart(px.bar(df25_daily, x="day", y="rr", title=f"2025 — {month_names[month]}"), use_container_width=True)

    wetter_year = "2026" if total26 > total25 else "2025"

    st.markdown("## 📌 Vergelijking")
    st.markdown(
        f"In **{month_names[month]} 2026** viel **{total26:.1f} mm** regen, "
        f"met een hoogste dagwaarde van **{max_avg26:.1f} mm**.\n\n"
        f"In **{month_names[month]} 2025** viel **{total25:.1f} mm**, "
        f"met een hoogste dagwaarde van **{max_avg25:.1f} mm**.\n\n"
        f"➡️ **{wetter_year}** was het nattere jaar."
    )

    season = season_from_month(month)
    st.markdown(f"🌦️ **Seizoen:** {season}")

    st.markdown("## ⚖️ Verschillen")
    st.markdown(f"""
- **Totale neerslag:** verschil **{abs(total26-total25):.1f} mm**
- **Gemiddelde dagneerslag:** verschil **{abs(avg26-avg25):.1f} mm/dag**
- **Hoogste dagwaarde:** verschil **{abs(max_avg26-max_avg25):.1f} mm**
""")

    st.markdown("## 🧾 Conclusie")
    st.markdown(f"**{wetter_year}** was natter in {month_names[month]}.")

    # Rode disclaimer
    st.markdown(
        """
        <div style="
            background-color:#ffe5e5;
            border-left: 6px solid #cc0000;
            padding: 15px;
            font-size: 18px;
            color:#990000;
            margin-top: 25px;
            border-radius: 6px;
        ">
            <b>⚠️ Belangrijke opmerking:</b><br>
            Sommige stations hebben ontbrekende of onvolledige data. Hierdoor kan het lijken alsof er minder regen is gevallen,
            terwijl dit het gevolg is van datagebrek en niet van werkelijke neerslaghoeveelheden.
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# MODE 2 — PER STATION
# ---------------------------------------------------------
else:

    all_stations = sorted(set(df_2025["stationid"].dropna()).union(df_2026["stationid"].dropna()))
    station = st.selectbox("Kies station:", all_stations)

    df26_s = df_2026_m[df_2026_m["stationid"] == station]
    df25_s = df_2025_m[df_2025_m["stationid"] == station]

    if df25_s.empty and df26_s.empty:
        st.warning(f"Geen gegevens voor station {station}.")
        st.stop()

    if df25_s.empty:
        st.warning(f"Geen gegevens voor 2025 voor station {station}.")
        st.stop()

    if df26_s.empty:
        st.warning(f"Geen gegevens voor 2026 voor station {station}.")
        st.stop()

    df26_s["label"] = df26_s["is_cumulative"].map({True: "Cumulatief", False: "Dagwaarde"})
    df25_s["label"] = df25_s["is_cumulative"].map({True: "Cumulatief", False: "Dagwaarde"})

    total26 = df26_s["rr_value"].sum()
    total25 = df25_s["rr_value"].sum()

    avg26 = df26_s["rr_value"].mean()
    avg25 = df25_s["rr_value"].mean()

    max26 = df26_s.loc[~df26_s["is_cumulative"], "rr_value"].max()
    max25 = df25_s.loc[~df25_s["is_cumulative"], "rr_value"].max()

    day_max26 = df26_s.loc[df26_s["rr_value"] == max26, "day"].iloc[0] if pd.notna(max26) else "-"
    day_max25 = df25_s.loc[df25_s["rr_value"] == max25, "day"].iloc[0] if pd.notna(max25) else "-"

    colA, colB = st.columns(2)

    with colA:
        st.subheader(f"📊 Statistieken — 2026 ({station})")
        st.metric("Totaal (mm)", round(total26, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg26, 1))
        st.metric("Hoogste dagwaarde", f"{max26:.1f} mm (dag {day_max26})")

    with colB:
        st.subheader(f"📊 Statistieken — 2025 ({station})")
        st.metric("Totaal (mm)", round(total25, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg25, 1))
        st.metric("Hoogste dagwaarde", f"{max25:.1f} mm (dag {day_max25})")

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(px.bar(df26_s, x="day", y="rr_value", color="label", title=f"2026 — {station}"), use_container_width=True)

    with col2:
        st.plotly_chart(px.bar(df25_s, x="day", y="rr_value", color="label", title=f"2025 — {station}"), use_container_width=True)

    wetter_year = "2026" if total26 > total25 else "2025"

    st.markdown("## 📌 Vergelijking")
    st.markdown(
        f"In **{month_names[month]} 2026** viel **{total26:.1f} mm**, hoogste dagwaarde **{max26:.1f} mm**.\n\n"
        f"In **{month_names[month]} 2025** viel **{total25:.1f} mm**, hoogste dagwaarde **{max25:.1f} mm**.\n\n"
        f"➡️ **{wetter_year}** was natter."
    )

    season = season_from_month(month)
    st.markdown(f"🌦️ **Seizoen:** {season}")

    st.markdown("## ⚖️ Verschillen")
    st.markdown(f"""
- **Totale neerslag:** verschil **{abs(total26-total25):.1f} mm**
- **Gemiddelde dagneerslag:** verschil **{abs(avg26-avg25):.1f} mm/dag**
- **Hoogste dagwaarde:** verschil **{abs(max26-max25):.1f} mm**
""")

    st.markdown("## 🧾 Conclusie")
    st.markdown(f"**{wetter_year}** was natter op station {station}.")

    # Rode disclaimer
    st.markdown(
        """
        <div style="
            background-color:#ffe5e5;
            border-left: 6px solid #cc0000;
            padding: 15px;
            font-size: 18px;
            color:#990000;
            margin-top: 25px;
            border-radius: 6px;
        ">
            <b>⚠️ Belangrijke opmerking:</b><br>
            Sommige stations hebben ontbrekende of onvolledige data. Hierdoor kan het lijken alsof er minder regen is gevallen,
            terwijl dit het gevolg is van datagebrek en niet van werkelijke neerslaghoeveelheden.
        </div>
        """,
        unsafe_allow_html=True
    )
