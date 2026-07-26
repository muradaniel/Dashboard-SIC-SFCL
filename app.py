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

    "⚙️ Otimização": [
        st.Page("app_pages/03_Otimizacao_Topologia_A.py", title="Topologia A"),
        st.Page("app_pages/04_Otimizacao_Topologia_B.py", title="Topologia B"),
        st.Page("app_pages/05_Otimizacao_Topologia_C.py", title="Topologia C"),
        st.Page("app_pages/06_Otimizacao_Topologia_D.py", title="Topologia D"),
        st.Page("app_pages/07_Comparacao_Topologias.py", title="Comparação entre Topologias"),
    ],

    "📈 Análises dos Resultados": [
        st.Page("app_pages/08_Visualizar_Sinal.py", title="Visualizar Sinal"),
        st.Page("app_pages/09_RMS.py", title="RMS"),
        st.Page("app_pages/10_Harmonicos.py", title="Harmônicos"),
    ]
}


st.navigation(paginas, expanded=True).run()