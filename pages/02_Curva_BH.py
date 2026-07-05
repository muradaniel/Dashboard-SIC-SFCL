from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from scipy.constants import mu_0
from dashboard_footer import mostrar_rodape
ICON_PATH = Path(__file__).resolve().parents[1] / "imagens" / "coil.png"

st.set_page_config(page_title="Curva B-H e μr", page_icon=str(ICON_PATH), layout="wide")

st.title("Curva B-H e Permeabilidade Relativa")

st.markdown(
    r"""
    **Regimes de operacao**

    Em regime permanente, o nucleo opera proximo da saturacao para manter baixa
    permeabilidade e baixa impedancia inserida no circuito. Durante o curto-circuito,
    a mudanca do ponto de operacao magnetico aumenta a impedancia equivalente e contribui
    para limitar a corrente.

    A curva B-H relaciona o campo magnetico $H$ com a densidade de fluxo $B$. A
    permeabilidade incremental usada no grafico e calculada por:

    $$
    \mu_r = \frac{1}{\mu_0}\frac{dB}{dH}
    $$
    """
)

BASE_DIR = Path(__file__).resolve().parents[1]

# Leitura
df = pd.read_csv(
    BASE_DIR / "Dataset" / "b_h_curve" / "Curva_B_H_Sem_Perdas.txt",
    sep=r"\s+",
    engine="python"
)

mostrar_rodape()

df.columns = ["H", "B"]

# 🔥 SUA LÓGICA ORIGINAL
dBdH = np.gradient(df["B"], df["H"])
mir = dBdH * 1 / mu_0
mir = np.insert(mir, 0, 0)
mir = mir[:-1]

df["μr"] = mir

# Remover valores inválidos para log
df_plot = df[df["μr"] > 0]

# Gráfico
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_plot["H"],
    y=df_plot["B"],
    mode="lines+markers",
    name="B (T)",
    line=dict(color="blue", width=3),
    marker=dict(symbol="circle", size=6),
    yaxis="y1"
))

fig.add_trace(go.Scatter(
    x=df_plot["H"],
    y=df_plot["μr"],
    mode="lines+markers",
    name="μr",
    line=dict(color="red", width=3),
    marker=dict(symbol="triangle-up", size=7),
    yaxis="y2"
))

fig.update_layout(
    xaxis=dict(title="H (A/m)"),

    yaxis=dict(
        title=dict(text="B (T)", font=dict(color="blue")),
        tickfont=dict(color="blue")
    ),

    yaxis2=dict(
        title=dict(text="μr (log)", font=dict(color="red")),
        tickfont=dict(color="red"),
        type="log",
        overlaying="y",
        side="right"
    ),

    height=780,
    template="plotly_white"
)

col1, col2 = st.columns([0.8, 0.2])

with col1:
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.dataframe(df, use_container_width=True, height=780)
