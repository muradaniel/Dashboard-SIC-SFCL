from pathlib import Path

import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
ICON_PATH = BASE_DIR / "imagens" / "coil.png"

st.set_page_config(
    page_title="SIC-SFCL Dashboard",
    page_icon=str(ICON_PATH),
    layout="wide",
)

paginas = [
    st.Page("introducao.py", title="Introdução", default=True),
    st.Page("pages/02_Curva_BH.py", title="Curva B-H"),
    st.Page("pages/03_Otimizacao.py", title="Otimização - 1 Núcleo"),
    st.Page("pages/04_Visualizar_Sinal.py", title="Visualizar Sinal"),
    st.Page("pages/05_RMS.py", title="RMS"),
    st.Page("pages/06_Harmonicos.py", title="Harmônicos"),
]

st.navigation(paginas, expanded=True).run()
