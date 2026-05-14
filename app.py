import streamlit as st
from utils.load_data import load_rr
from utils.seasons import assign_season
import pandas as pd

st.set_page_config(
    page_title="Suriname Rainfall & Climate Dashboard",
    layout="wide"
)

st.title("🌧️ Suriname Rainfall & Climate Dashboard")
st.write("Analyse van dagelijkse neerslag voor 2026 en vergelijking met 2025.")

# --- Dropdowns ---
col1, col2 = st.columns(2)

with col1:
    year = st.selectbox("Kies jaar", [2026, 2025])

with col2:
    month = st.selectbox("Kies maand", list(range(1, 13)))

# --- Data laden ---
df = load_rr(year)
df["season"] = df.apply(assign_season, axis=1)
df_month = df[df["month"] == month]

# --- Introductieblok ---
st.markdown("""
### 📘 Over dit dashboard
Dit dashboard helpt je om:
- Dagelijkse neerslag te analyseren  
- Verschillen tussen 2026 en 2025 te bekijken  
- Seizoenspatronen te begrijpen  
- Statistieken per maand en per jaar te zien  

Gebruik het menu links om naar de detailpagina’s te gaan.
""")

# --- Statistieken preview ---
st.markdown(f"### 📊 Snelle statistieken voor **{year} – maand {month}**")

colA, colB, colC, colD = st.columns(4)

with colA:
    st.metric("Totaal (mm)", round(df_month["RR"].sum(), 1))

with colB:
    st.metric("Gemiddelde (mm/dag)", round(df_month["RR"].mean(), 2))

with colC:
    st.metric("Natte dagen", int((df_month["RR"] >= 1).sum()))

with colD:
    st.metric("Zware dagen (≥50mm)", int((df_month["RR"] >= 50).sum()))

# --- Seizoen info ---
st.markdown("### 🌦️ Seizoen van deze maand")

season_name = df_month["season"].iloc[0] if len(df_month) > 0 else "Onbekend"

st.info(f"**{season_name}** — volgens de tropische seizoensindeling van Suriname.")

# --- Footer ---
st.markdown("""
---
📍 *Data: Dagelijkse neerslagmetingen Suriname (Hydromet)*  
📅 *Jaren: 2025 & 2026*  
""")
