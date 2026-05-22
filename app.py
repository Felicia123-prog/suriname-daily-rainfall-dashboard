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
    if year == 2026:
        filename = "Rainfall_Data_Suriname_2026.xlsx"
    else:
        filename = "Rainfall_Data_Suriname_2025.xlsx"

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

        df["date"] = pd.to_datetime(
            df[["Year", "Month", "Day"]].astype(int),
            errors="coerce"
        )

        df = df[["date", "latitude", "longitude", "stationid", "rain_raw"]]
        frames.append(df)

    else:
        for sheet in xls.sheet_names:
            df = pd.read_excel(path, sheet_name=sheet)
            df.columns = [c.strip().lower() for c in df.columns]

            for col in ["date", "latitude", "longitude", "stationid"]:
                if col not in df.columns:
                    df[col] = None

            rain_col = None
            for c in df.columns:
                if "rainfall" in c or "precip" in c or c == "rr":
                    rain_col = c
                    break

            if rain_col is None:
                continue

            df = df[["date", "latitude", "longitude", "stationid", rain_col]]
            df = df.rename(columns={rain_col: "rain_raw"})
            frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)

# ---------------------------------------------------------
# UNIFORMIZER
# ---------------------------------------------------------
def uniformize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    raw = df["rain_raw"].apply(lambda x: str(x).strip())
    raw = raw.str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii")
    raw = raw.str.replace(r"\s+", "", regex=True)

    df["is_cumulative"] = raw.str.contains("C", case=False)

    df["rr_value"] = raw.str.replace(r"[cC].*", "", regex=True)
    df["rr_value"] = pd.to_numeric(df["rr_value"], errors="coerce")

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

    has_2025 = not df_2025_m.empty
    has_2026 = not df_2026_m.empty

    if not has_2025 and not has_2026:
        st.warning("Voor deze maand ontbreken landelijke gegevens voor zowel 2025 als 2026. Een vergelijking is niet mogelijk.")
        st.stop()

    if not has_2025:
        st.warning("Voor deze maand ontbreken landelijke gegevens voor 2025. Een vergelijking met 2026 is niet mogelijk.")
        st.stop()

    if not has_2026:
        st.warning("Voor deze maand ontbreken landelijke gegevens voor 2026. Een vergelijking met 2025 is niet mogelijk.")
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

    max_avg26 = df26_daily["rr"].max() if not df26_daily.empty else 0
    max_avg25 = df25_daily["rr"].max() if not df25_daily.empty else 0

    with colA:
        st.subheader(f"📊 Statistieken — 2026 ({month_names[month]})")
        st.metric("Totaal (mm)", round(total26, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg26, 1))
        st.metric("Hoogste gemiddelde dagneerslag (mm)", round(max_avg26, 1))

    with colB:
        st.subheader(f"📊 Statistieken — 2025 ({month_names[month]})")
        st.metric("Totaal (mm)", round(total25, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg25, 1))
        st.metric("Hoogste gemiddelde dagneerslag (mm)", round(max_avg25, 1))

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

    wetter_year = "2026" if total26 > total25 else "2025"

    st.markdown("## 📌 Vergelijking")
    st.markdown(
        f"In **{month_names[month]} 2026** viel landelijk in totaal **{total26:.1f} mm** regen. "
        f"De regenval was redelijk gelijkmatig verdeeld, met een hoogste gemiddelde dagwaarde van **{max_avg26:.1f} mm**.\n\n"
        f"In **{month_names[month]} 2025** bedroeg de totale neerslag **{total25:.1f} mm**, "
        f"met een duidelijkere afwisseling tussen natte en drogere dagen. "
        f"De hoogste gemiddelde dagwaarde lag op **{max_avg25:.1f} mm**.\n\n"
        f"Op basis hiervan was **{wetter_year}** het nattere jaar."
    )

    season = season_from_month(month)
    st.markdown(
        f"🌦️ **Seizoen:** {season} — deze maand valt binnen de *{season.lower()}*, "
        f"wat past binnen het typische regenpatroon van Suriname."
    )

    st.markdown("## ⚖️ Verschillen tussen de jaren")

    verschil_totaal = abs(total26 - total25)
    verschil_gem = abs(avg26 - avg25)
    verschil_max = abs(max_avg26 - max_avg25)

    st.markdown(f"""
**Belangrijkste verschillen:**

- **Totale neerslag:** {wetter_year} had **{verschil_totaal:.1f} mm** meer neerslag.
- **Gemiddelde dagneerslag:** verschil van **{verschil_gem:.1f} mm/dag**.
- **Hoogste dagwaarde:** verschil van **{verschil_max:.1f} mm**.
""")

    st.markdown("## 🧾 Conclusie")

    if wetter_year == "2026":
        conclusie = (
            f"{month_names[month]} van 2026 was natter dan 2025, "
            f"met hogere totalen en intensievere dagpieken."
        )
    else:
        conclusie = (
            f"{month_names[month]} van 2025 was natter dan 2026, "
            f"met hogere totalen en duidelijkere variatie tussen natte en drogere dagen."
        )

    st.markdown(f"**{conclusie}**")
    
    )

# ---------------------------------------------------------
# MODE 2 — PER STATION
# ---------------------------------------------------------
else:
    all_stations = sorted(
        set(df_2025["stationid"].dropna()).union(df_2026["stationid"].dropna())
    )
    station = st.selectbox("Kies station:", all_stations)

    df26_s = df_2026_m[df_2026_m["stationid"] == station].copy()
    df25_s = df_2025_m[df_2025_m["stationid"] == station].copy()

    has_2025 = not df25_s.empty
    has_2026 = not df26_s.empty

    if not has_2025 and not has_2026:
        st.warning(f"Voor station **{station}** ontbreken gegevens voor zowel 2025 als 2026. Een vergelijking is niet mogelijk.")
        st.stop()

    if not has_2025:
        st.warning(f"Voor station **{station}** ontbreken gegevens voor 2025. Een vergelijking met 2026 is niet mogelijk.")
        st.stop()

    if not has_2026:
        st.warning(f"Voor station **{station}** ontbreken gegevens voor 2026. Een vergelijking met 2025 is niet mogelijk.")
        st.stop()

    df26_s["label"] = df26_s.apply(lambda r: "Cumulatief" if r["is_cumulative"] else "Dagwaarde", axis=1)
    df25_s["label"] = df25_s.apply(lambda r: "Cumulatief" if r["is_cumulative"] else "Dagwaarde", axis=1)

    total26 = df26_s["rr_value"].sum()
    total25 = df25_s["rr_value"].sum()

    avg26 = df26_s["rr_value"].mean()
    avg25 = df25_s["rr_value"].mean()

    valid_rr_26 = df26_s.loc[~df26_s["is_cumulative"], "rr_value"]
    valid_rr_25 = df25_s.loc[~df25_s["is_cumulative"], "rr_value"]

    max26 = valid_rr_26.max() if not valid_rr_26.dropna().empty else 0
    max25 = valid_rr_25.max() if not valid_rr_25.dropna().empty else 0

    day_max26 = df26_s.loc[df26_s["rr_value"] == max26, "day"].iloc[0] if max26 > 0 else "-"
    day_max25 = df25_s.loc[df25_s["rr_value"] == max25, "day"].iloc[0] if max25 > 0 else "-"

    colA, colB = st.columns(2)

    with colA:
        st.subheader(f"📊 Statistieken — 2026 ({station})")
        st.metric("Totaal (mm)", round(total26, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg26, 1))
        st.metric("Hoogste dagneerslag (mm)", f"{max26:.1f} (dag {day_max26})")

    with colB:
        st.subheader(f"📊 Statistieken — 2025 ({station})")
        st.metric("Totaal (mm)", round(total25, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg25, 1))
        st.metric("Hoogste dagneerslag (mm)", f"{max25:.1f} (dag {day_max25})")

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(
            df26_s,
            x="day",
            y="rr_value",
            color="label",
            color_discrete_map={"Dagwaarde": "blue", "Cumulatief": "red"},
            labels={"day": "Dag", "rr_value": "Neerslag (mm)", "label": "Type"},
            title=f"2026 — {station}"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(
            df25_s,
            x="day",
            y="rr_value",
            color="label",
            color_discrete_map={"Dagwaarde": "blue", "Cumulatief": "red"},
            labels={"day": "Dag", "rr_value": "Neerslag (mm)", "label": "Type"},
            title=f"2025 — {station}"
        )
        st.plotly_chart(fig2, use_container_width=True)

    wetter_year = "2026" if total26 > total25 else "2025"

    st.markdown("## 📌 Vergelijking")
    st.markdown(
        f"In **{month_names[month]} 2026** registreerde station **{station}** een totale "
        f"neerslag van **{total26:.1f} mm**, met een hoogste dagwaarde van "
        f"**{max26:.1f} mm** op **dag {day_max26}**.\n\n"
        f"In **{month_names[month]} 2025** bedroeg de totale neerslag **{total25:.1f} mm**, "
        f"met een maximale dagwaarde van **{max25:.1f} mm** op **dag {day_max25}**.\n\n"
        f"Op basis van deze gegevens was **{wetter_year}** het nattere jaar."
    )

    season = season_from_month(month)
    st.markdown(
        f"🌦️ **Seizoen:** {season} — deze maand valt binnen de *{season.lower()}*, "
        f"wat duidelijk zichtbaar is in het neerslagpatroon van dit station."
    )

    st.markdown("## ⚖️ Verschillen tussen de jaren")

    verschil_totaal = abs(total26 - total25)
    verschil_gem = abs(avg26 - avg25)
    verschil_max = abs(max26 - max25)

    st.markdown(f"""
**Belangrijkste verschillen:**

- **Totale neerslag:** {wetter_year} had **{verschil_totaal:.1f} mm** meer neerslag.
- **Gemiddelde dagneerslag:** verschil van **{verschil_gem:.1f} mm/dag**.
- **Hoogste dagwaarde:** verschil van **{verschil_max:.1f} mm**.
- **Dag van hoogste waarde:** 2026: dag {day_max26}, 2025: dag {day_max25}.
""")
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


