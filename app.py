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
    st.Page("app_pages/02_Curva_BH.py", title="Curva B-H"),
    st.Page("app_pages/03_Otimizacao.py", title="Otimização - 1 Núcleo & 1 Bobina"),
    st.Page("app_pages/09_Otimizacao_1_Nucleo_2_Bobinas.py", title="Otimização - 1 Núcleo & 2 Bobinas"),
    st.Page("app_pages/07_Otimizacao_2_Nucleos_1_Bobina.py", title="Otimização - 2 Núcleos & 1 Bobina"),
    st.Page("app_pages/08_Otimizacao_2_Nucleos_2_Bobinas.py", title="Otimização - 2 Núcleos & 2 Bobinas"),
    st.Page("app_pages/04_Visualizar_Sinal.py", title="Visualizar Sinal"),
    st.Page("app_pages/05_RMS.py", title="RMS"),
    st.Page("app_pages/06_Harmonicos.py", title="Harmônicos"),
]

st.navigation(paginas, expanded=True).run()


