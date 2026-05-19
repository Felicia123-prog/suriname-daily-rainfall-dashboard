import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Maandelijkse Neerslagrapportage 2025–2026", layout="wide")

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

    # -------------------------
    # 2025 — 1 sheet RR_2025
    # -------------------------
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

    # -------------------------
    # 2026 — meerdere sheets
    # -------------------------
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
# UNIFORMIZER — cumulatieven eruit voor statistiek
# ---------------------------------------------------------
def uniformize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    raw = df["rain_raw"].apply(lambda x: str(x).strip())
    raw = raw.str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii")
    raw = raw.str.replace(r"\s+", "", regex=True)

    df["is_cumulative"] = raw.str.contains("C", case=False)

    df["rr_value"] = raw.str.replace(r"[cC].*", "", regex=True)
    df["rr_value"] = pd.to_numeric(df["rr_value"], errors="coerce")

    # rr = dagwaarde (zonder cumulatief)
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
# DATA LADEN + OPSCHONEN
# ---------------------------------------------------------
df_2025 = uniformize(load_rr(2025))
df_2026 = uniformize(load_rr(2026))

df_2025_m = df_2025[df_2025["month"] == month]
df_2026_m = df_2026[df_2026["month"] == month]

# ---------------------------------------------------------
# HELPER: seizoensnaam
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
# MODE 1 — LANDELIJK GEMIDDELDE
# ---------------------------------------------------------
if mode == "Geheel Suriname (landelijk gemiddelde)":

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

    # ----------------- ANALYSE (originele stijl) -----------------
    st.markdown("### 📌 Analyse")
    st.markdown(
        f"In **{month_names[month]} 2026** zien we een totale neerslag van **{total26:.1f} mm**. "
        f"De regenval is vrij gelijkmatig verdeeld over de maand, met een piek rond de dagen "
        f"waar de gemiddelde dagneerslag oploopt tot **{max_avg26:.1f} mm**.\n\n"
        
        f"In **{month_names[month]} 2025** lag de totale neerslag hoger (**{total25:.1f} mm**). "
        f"De maand toont een duidelijker variatie tussen natte en drogere dagen, met een "
        f"hoogste gemiddelde dagneerslag van **{max_avg25:.1f} mm**.\n\n"

        f"Over het algemeen toont **{month_names[month]}** een duidelijk verschil tussen beide jaren, "
        f"waarbij 2025 natter was dan 2026."
    )

    # ----------------- SEIZOEN -----------------
    season = season_from_month(month)
    st.markdown(
        f"🌦️ **Seizoen:** {season} — deze maand valt binnen de *{season.lower()}*, "
        f"wat typisch is voor het regenpatroon in Suriname."
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

    df26_s["label"] = df26_s.apply(lambda r: "Cumulatief" if r["is_cumulative"] else "Dagwaarde", axis=1)
    df25_s["label"] = df25_s.apply(lambda r: "Cumulatief" if r["is_cumulative"] else "Dagwaarde", axis=1)

    # ----------------- STATISTIEKEN -----------------
    total26 = df26_s["rr_value"].sum()
    total25 = df25_s["rr_value"].sum()

    avg26 = df26_s["rr_value"].mean()
    avg25 = df25_s["rr_value"].mean()

    valid_rr_26 = df26_s.loc[~df26_s["is_cumulative"], "rr_value"]
    valid_rr_25 = df25_s.loc[~df25_s["is_cumulative"], "rr_value"]

    max26 = valid_rr_26.max() if not valid_rr_26.dropna().empty else 0
    max25 = valid_rr_25.max() if not valid_rr_25.dropna().empty else 0

    colA, colB = st.columns(2)

    with colA:
        st.subheader(f"📊 Statistieken — 2026 ({station})")
        st.metric("Totaal (mm)", round(total26, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg26, 1))
        st.metric("Hoogste dagneerslag (mm)", round(max26, 1))

    with colB:
        st.subheader(f"📊 Statistieken — 2025 ({station})")
        st.metric("Totaal (mm)", round(total25, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg25, 1))
        st.metric("Hoogste dagneerslag (mm)", round(max25, 1))

    # ----------------- GRAFIEKEN -----------------
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

    # ----------------- ANALYSE (originele stijl) -----------------
    st.markdown(f"### 📌 Analyse voor station {station}")
    st.markdown(
        f"In **{month_names[month]} 2026** registreerde station **{station}** een totale "
        f"neerslag van **{total26:.1f} mm**. De hoogste dagwaarde (niet‑cumulatief) kwam uit op "
        f"**{max26:.1f} mm**.\n\n"

        f"In **{month_names[month]} 2025** lag de totale neerslag op **{total25:.1f} mm**, "
        f"met een maximale dagwaarde van **{max25:.1f} mm**.\n\n"

        f"Het verschil tussen beide jaren laat zien hoe variabel de regenval kan zijn op dit station."
    )

    # ----------------- SEIZOEN -----------------
    season = season_from_month(month)
    st.markdown(
        f"🌦️ **Seizoen:** {season} — deze maand valt binnen de *{season.lower()}*, "
        f"wat duidelijk terug te zien is in het neerslagpatroon van dit station."
    )
