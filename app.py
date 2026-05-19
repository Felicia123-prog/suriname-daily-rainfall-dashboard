import os
st.write("📁 Current working directory:", os.getcwd())

try:
    st.write("📂 Files in working directory:", os.listdir())
except:
    st.write("Kan hoofdmap niet lezen")

try:
    st.write("📂 Files in ./data:", os.listdir("data"))
except:
    st.write("data folder not found")

try:
    st.write("📂 Files in /mount/src/suriname-daily-rainfall-dashboard:", 
             os.listdir("/mount/src/suriname-daily-rainfall-dashboard"))
except:
    st.write("Map /mount/src/... bestaat niet")

try:
    st.write("📂 Files in /app/data:", os.listdir("/app/data"))
except:
    st.write("/app/data folder not found")

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Maandelijkse Neerslagrapportage 2025–2026", layout="wide")

# ---------------------------------------------------------
# LOAD ALL SHEETS FROM EXCEL
# ---------------------------------------------------------
def load_rr(year):
    if year == 2026:
        path = r"C:\Users\Felicia\OneDrive\Desktop\Rainfall_Data_Suriname_2026.xlsx"
    else:
        path = r"C:\Users\Felicia\OneDrive\Desktop\Rainfall_Data_Suriname_2025.xlsx"

    xls = pd.ExcelFile(path)
    frames = []

    for sheet in xls.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet)

        df.columns = [c.strip().lower() for c in df.columns]

        # verplicht
        for col in ["date", "latitude", "longitude", "stationid"]:
            if col not in df.columns:
                df[col] = None

        # neerslagkolom zoeken
        rain_col = None
        for c in df.columns:
            if any(k in c for k in ["rain", "precip", "rr", "waarde", "value"]):
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
# UNIFORMIZER — verwijdert ALLE cumulatieven
# ---------------------------------------------------------
def uniformize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Forceer alles naar tekst
    raw = df["rain_raw"].apply(lambda x: str(x).strip())

    # Unicode normalisatie
    raw = raw.str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii")

    # Whitespace verwijderen
    raw = raw.str.replace(r"\s+", "", regex=True)

    # Detecteer cumulatief (alles met C)
    df["is_cumulative"] = raw.str.contains("C", case=False)

    # Haal numerieke waarde eruit
    df["rr_value"] = raw.str.replace(r"[cC].*", "", regex=True)
    df["rr_value"] = pd.to_numeric(df["rr_value"], errors="coerce")

    # Dagwaarde = niet-cumulatief
    df["rr"] = df["rr_value"]
    df.loc[df["is_cumulative"], "rr"] = None

    # Datum
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
# DATA LADEN
# ---------------------------------------------------------
df_2025 = uniformize(load_rr(2025))
df_2026 = uniformize(load_rr(2026))

df_2025_m = df_2025[df_2025["month"] == month]
df_2026_m = df_2026[df_2026["month"] == month]


# ---------------------------------------------------------
# MODE 1 — GEHEEL SURINAME
# ---------------------------------------------------------
if mode == "Geheel Suriname (WMO‑gemiddelde)":

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

    valid_rr_26 = df_2026_m.loc[~df_2026_m["is_cumulative"], "rr_value"]
    valid_rr_25 = df_2025_m.loc[~df_2025_m["is_cumulative"], "rr_value"]

    max_station26 = valid_rr_26.max() if not valid_rr_26.dropna().empty else 0
    max_station25 = valid_rr_25.max() if not valid_rr_25.dropna().empty else 0

    with colA:
        st.subheader(f"📊 Statistieken — 2026 ({month_names[month]})")
        st.metric("Totaal (mm)", round(total26, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg26, 1))
        st.metric("Max dagneerslag (mm)", round(max_avg26, 1))

    with colB:
        st.subheader(f"📊 Statistieken — 2025 ({month_names[month]})")
        st.metric("Totaal (mm)", round(total25, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg25, 1))
        st.metric("Max dagneerslag (mm)", round(max_avg25, 1))

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

    df26_s["rr"] = df26_s["rr"].round(1)
    df25_s["rr"] = df25_s["rr"].round(1)

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
        st.metric("Max dagneerslag (mm)", round(max26, 1))

    with colB:
        st.subheader(f"📊 Statistieken — 2025 ({station})")
        st.metric("Totaal (mm)", round(total25, 1))
        st.metric("Gemiddelde (mm/dag)", round(avg25, 1))
        st.metric("Max dagneerslag (mm)", round(max25, 1))

    col1, col2 = st.columns(2)

    with col1:
        if not df26_s.empty:
            fig1 = px.bar(df26_s, x="day", y="rr", color="label",
                          color_discrete_map={"Dagwaarde": "blue", "Cumulatief": "red"},
                          labels={"day": "Dag", "rr": "Neerslag (mm)", "label": "Type"},
                          title=f"2026 — {station}")
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        if not df25_s.empty:
            fig2 = px.bar(df25_s, x="day", y="rr", color="label",
                          color_discrete_map={"Dagwaarde": "blue", "Cumulatief": "red"},
                          labels={"day": "Dag", "rr": "Neerslag (mm)", "label": "Type"},
                          title=f"2025 — {station}")
            st.plotly_chart(fig2, use_container_width=True)
