import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(page_title="Lab 1 — GoT Networks", layout="wide")

st.title("Lab 1 — Game of Thrones Networks")
st.caption("Task 1: Kings Battles • Task 2: Houses/Dynasties")

# Paths to exported HTMLs (must be at repo root)
BATTLES_HTML = Path("Lab1-task1-net5kings.html")
HOUSES_HTML = Path("L1_Task2_GameOfThronesHouses.html")

with st.sidebar:
    st.header("How this app works")
    st.markdown(
        """
        This streamlit app embeds the HTML graphs created in your notebooks:
    

        If you update the notebooks, re-run them to regenerate the HTMLs, then refresh this app.
        """
    )
    st.divider()
    st.markdown("**Files expected at project root:**")
    st.code("Lab1-task1-net5kings.html\nL1_Task2_GameOfThronesHouses.html", language="bash")

tab1, tab2 = st.tabs(["🛡️ Kings Battles (Task 1)", "🏰 Houses / Dynasties (Task 2)"])

with tab1:
    st.subheader("Task 1 — Kings Battles Network")
    if BATTLES_HTML.exists():
        html = BATTLES_HTML.read_text(encoding="utf-8")
        components.html(html, height=1000, scrolling=True)
    else:
        st.error(f"Missing file: {BATTLES_HTML.name}. Run the Task 1 notebook to generate it.")

with tab2:
    st.subheader("Task 2 — Houses / Dynasties Network")
    if HOUSES_HTML.exists():
        html = HOUSES_HTML.read_text(encoding="utf-8")
        components.html(html, height=1000, scrolling=True)
    else:
        st.error(f"Missing file: {HOUSES_HTML.name}. Run the Task 2 notebook to generate it.")
