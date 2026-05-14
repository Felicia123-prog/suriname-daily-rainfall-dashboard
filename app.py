import streamlit as st

st.set_page_config(
    page_title="Suriname Daily Rainfall Dashboard",
    layout="wide"
)

st.title("Suriname Daily Rainfall Dashboard")
st.write("Analyse van dagelijkse neerslag voor 2026 en vergelijking met 2025.")

st.markdown("""
### 📊 Beschikbare pagina’s
Gebruik het menu links om te navigeren:

- **Dagelijkse Neerslag 2026**  
  Dagelijkse staafdiagrammen per maand + heatmap.

- **Vergelijking 2026 vs 2025**  
  Dagelijkse vergelijking per maand + verschil‑heatmap.

- **Statistieken 2026 vs 2025**  
  Jaar-, maand- en seizoensstatistieken.
""")

st.info("Selecteer een pagina in het menu links om te beginnen.")

