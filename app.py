from pathlib import Path

import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
ICON_PATH = BASE_DIR / "imagens" / "coil.png"

st.set_page_config(
    page_title="SIC-SFCL Dashboard",
    page_icon=str(ICON_PATH),
    layout="wide",
)

paginas = {
    "🏠 Geral": [
        st.Page("introducao.py", title="Introdução", default=True),
        st.Page("app_pages/02_Curva_BH.py", title="Curva B-H"),
    ],

    "⚙️ Topologias": [
        st.Page("app_pages/03_Otimizacao.py", title="A - 1 Núcleo & 1 Bobina DC & 1 Bobina AC"),
        st.Page("app_pages/09_Otimizacao_1_Nucleo_2_Bobinas.py", title="B - 1 Núcleo & 1 Bobina DC & 2 Bobinas AC"),
        st.Page("app_pages/07_Otimizacao_2_Nucleos_1_Bobina.py", title="C - 2 Núcleos & 1 Bobina DC & 2 Bobinas AC"),
        st.Page("app_pages/08_Otimizacao_2_Nucleos_2_Bobinas.py", title="D - 2 Núcleos & 2 Bobinas DC & 2 Bobinas AC"),
        st.Page("app_pages/10_Comparacao_Topologias.py", title="Comparação entre Topologias"),
    ],

    "📈 Análises dos Resultados": [
        st.Page("app_pages/04_Visualizar_Sinal.py", title="Visualizar Sinal"),
        st.Page("app_pages/05_RMS.py", title="RMS"),
        st.Page("app_pages/06_Harmonicos.py", title="Harmônicos"),
    ]
}


st.navigation(paginas, expanded=True).run()