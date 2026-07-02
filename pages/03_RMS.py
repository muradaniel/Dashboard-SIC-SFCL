from io import BytesIO

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Analise RMS",
    layout="wide",
)

st.title("Analise RMS de Sinais Eletricos")


COLUNAS_TXT = [
    "H (cm)",
    "W (cm)",
    "N_DC",
    "N_AC",
    "Time (s)",
    "Corrente de Curto (A)",
    "Queda de Tensao (V)",
]
COLUNA_CHAVE = "Chave"


@st.cache_data(show_spinner="Carregando arquivo TXT...")
def carregar_txt(conteudo_arquivo):
    dados = pd.read_csv(
        BytesIO(conteudo_arquivo),
        sep=r"\s{2,}",
        engine="python",
        comment="%",
        header=None,
        names=COLUNAS_TXT,
    )

    for coluna in COLUNAS_TXT:
        dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce")

    dados = dados.dropna(subset=COLUNAS_TXT).copy()
    dados[COLUNA_CHAVE] = (
        dados["H (cm)"].map(lambda valor: f"{valor:g}")
        + " "
        + dados["W (cm)"].map(lambda valor: f"{valor:g}".replace(".", ","))
        + " "
        + dados["N_DC"].map(lambda valor: f"{valor:g}")
        + " "
        + dados["N_AC"].map(lambda valor: f"{valor:g}")
    )
    return dados


arquivo_txt = st.file_uploader(
    "Selecione um arquivo TXT exportado do COMSOL",
    type=["txt"],
)

if arquivo_txt is None:
    st.warning("Selecione um arquivo TXT para iniciar a analise.")
    st.stop()

nome_arquivo = arquivo_txt.name

try:
    dados = carregar_txt(arquivo_txt.getvalue())
except Exception as erro:
    st.error(f"Erro ao ler o arquivo TXT: {erro}")
    st.stop()

if dados.empty:
    st.warning("O arquivo selecionado nao possui dados validos.")
    st.stop()

with st.sidebar:
    st.subheader("Selecao dos dados")
    chaves = sorted(dados[COLUNA_CHAVE].unique())
    chave_selecionada = st.selectbox("Combinacao", chaves)

    colunas_numericas = COLUNAS_TXT.copy()
    indice_tempo = colunas_numericas.index("Time (s)")
    indice_sinal = colunas_numericas.index("Corrente de Curto (A)")

    coluna_tempo = st.selectbox(
        "Coluna de tempo",
        colunas_numericas,
        index=indice_tempo,
    )
    coluna_sinal = st.selectbox(
        "Coluna do sinal",
        colunas_numericas,
        index=indice_sinal,
    )

dados_selecionados = dados[dados[COLUNA_CHAVE] == chave_selecionada].copy()

try:
    tempo = pd.to_numeric(
        dados_selecionados[coluna_tempo],
        errors="coerce",
    ).to_numpy()
    sinal = pd.to_numeric(
        dados_selecionados[coluna_sinal],
        errors="coerce",
    ).to_numpy()
except Exception as erro:
    st.error(f"Erro ao converter as colunas selecionadas: {erro}")
    st.stop()

mascara_valida = np.isfinite(tempo) & np.isfinite(sinal)
tempo = tempo[mascara_valida]
sinal = sinal[mascara_valida]

if len(tempo) < 2:
    st.error("A combinacao precisa ter pelo menos dois pontos validos de tempo e sinal.")
    st.stop()

ordem = np.argsort(tempo)
tempo = tempo[ordem]
sinal = sinal[ordem]

rms_total = np.sqrt(np.mean(sinal ** 2))
rms_total_linha = np.full_like(sinal, rms_total)

st.success(f"Arquivo carregado: {nome_arquivo} | Combinacao: {chave_selecionada}")

col1, col2, col3 = st.columns(3)
col1.metric("Valor RMS total", f"{rms_total:.2f}")
col2.metric("Pontos analisados", len(sinal))
col3.metric("Coluna analisada", coluna_sinal)

st.subheader("Sinal selecionado e RMS total")

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=tempo,
        y=sinal,
        mode="lines",
        name="Sinal selecionado",
        line=dict(width=2),
        hovertemplate=(
            "Tempo: %{x:.6f} s<br>"
            "Sinal: %{y:.6f}<extra></extra>"
        ),
    )
)
fig.add_trace(
    go.Scatter(
        x=tempo,
        y=rms_total_linha,
        mode="lines",
        name=f"RMS total = {rms_total:.2f}",
        line=dict(width=3, dash="dash"),
        hovertemplate=(
            "Tempo: %{x:.6f} s<br>"
            "RMS total: %{y:.2f}<extra></extra>"
        ),
    )
)
fig.update_layout(
    title="Analise RMS do sinal selecionado",
    xaxis_title=coluna_tempo,
    yaxis_title=coluna_sinal,
    hovermode="x unified",
    template="plotly_white",
    height=650,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
)
fig.update_xaxes(showgrid=True)
fig.update_yaxes(showgrid=True)

st.plotly_chart(fig, use_container_width=True)