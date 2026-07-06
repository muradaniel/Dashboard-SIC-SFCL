from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dashboard_footer import mostrar_rodape
ICON_PATH = Path(__file__).resolve().parents[1] / "imagens" / "coil.png"


st.set_page_config(
    page_title="Analise RMS",
    page_icon=str(ICON_PATH),
    layout="wide",
)

mostrar_rodape()

st.title("Analise RMS de Sinais Eletricos")

st.markdown(
    r"""
    A funcao principal desta pagina e calcular a tensao RMS em regime a partir do
    sinal selecionado:

    $$
    V_{RMS} = \sqrt{\frac{1}{T}\int_0^T v^2(t)\,dt}
    $$

    Como criterio de projeto, considera-se que a queda maxima admissivel seja de 10% da entrada:

    $$
    V_{limite,RMS} = 0{,}10 \cdot 127 = 12{,}7\,V_{RMS}
    $$

    $$
    V_{limite,pico} = 12{,}7\sqrt{2} \approx 18\,V
    $$
    """
)


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
EXEMPLOS = {
    "Tensao RMS": Path("Dataset/root_mean_square/Tensão RMS.csv"),
    "Sinal COMSOL - otimizacao 28A 16V": Path("Dataset/signal/otimizacao 28A 16V.txt"),
    "Sinal senoidal 60 Hz": Path("Dataset/harmonics/sinal_60hz_senoidal.txt"),
}


def nome_sinal_sintetico(nome_arquivo):
    nome = nome_arquivo.lower().removesuffix(".txt")
    if nome.startswith("sinal_60hz_"):
        return "Sinal qualquer"
    return None


def selecionar_arquivo():
    st.subheader("Dados de entrada")
    fonte = st.radio(
        "Fonte dos dados",
        ["Usar arquivo de exemplo", "Enviar arquivo"],
        horizontal=True,
    )

    if fonte == "Enviar arquivo":
        arquivo = st.file_uploader(
            "Selecione um arquivo TXT exportado do COMSOL ou CSV com separador ';'",
            type=["txt", "csv"],
        )
        if arquivo is None:
            st.warning("Selecione um arquivo para iniciar a analise.")
            st.stop()
        return arquivo.getvalue(), arquivo.name

    nome_exemplo = st.selectbox("Arquivo de exemplo", list(EXEMPLOS))
    caminho = EXEMPLOS[nome_exemplo]
    return caminho.read_bytes(), caminho.name


@st.cache_data(show_spinner="Carregando arquivo TXT...")
def carregar_txt(conteudo_arquivo, nome_arquivo):
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
    nome_sintetico = nome_sinal_sintetico(nome_arquivo)
    if nome_sintetico:
        dados[COLUNA_CHAVE] = nome_sintetico
    else:
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


@st.cache_data(show_spinner="Carregando arquivo CSV...")
def carregar_csv(conteudo_arquivo, nome_arquivo):
    dados = pd.read_csv(BytesIO(conteudo_arquivo), sep=";")
    for coluna in dados.columns:
        dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce")
    dados = dados.dropna(how="all").copy()
    dados[COLUNA_CHAVE] = nome_arquivo.removesuffix(".csv")
    return dados


def carregar_arquivo(conteudo_arquivo, nome_arquivo):
    if nome_arquivo.lower().endswith(".csv"):
        return carregar_csv(conteudo_arquivo, nome_arquivo)
    return carregar_txt(conteudo_arquivo, nome_arquivo)


conteudo_arquivo, nome_arquivo = selecionar_arquivo()

try:
    dados = carregar_arquivo(conteudo_arquivo, nome_arquivo)
except Exception as erro:
    st.error(f"Erro ao ler o arquivo: {erro}")
    st.stop()

if dados.empty:
    st.warning("O arquivo selecionado nao possui dados validos.")
    st.stop()

chaves = sorted(dados[COLUNA_CHAVE].unique())
if len(chaves) == 1:
    chave_selecionada = chaves[0]
else:
    with st.sidebar:
        st.subheader("Selecao dos dados")
        chave_selecionada = st.selectbox("Combinacao", chaves)

with st.sidebar:
    colunas_numericas = [
        coluna
        for coluna in dados.columns
        if coluna != COLUNA_CHAVE and pd.api.types.is_numeric_dtype(dados[coluna])
    ]
    if not colunas_numericas:
        st.error("O arquivo precisa ter pelo menos uma coluna numerica.")
        st.stop()

    if "Time (s)" in colunas_numericas:
        coluna_tempo = "Time (s)"
    elif "Time" in colunas_numericas:
        coluna_tempo = "Time"
    else:
        st.error("O arquivo precisa ter a coluna de tempo 'Time (s)' ou 'Time'.")
        st.stop()

    if "Corrente de Curto (A)" in colunas_numericas:
        indice_sinal = colunas_numericas.index("Corrente de Curto (A)")
    elif "Tensao" in colunas_numericas:
        indice_sinal = colunas_numericas.index("Tensao")
    else:
        indice_sinal = min(1, len(colunas_numericas) - 1)

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
        hovertemplate="Sinal: %{y:.6f}<extra></extra>",
    )
)
fig.add_trace(
    go.Scatter(
        x=tempo,
        y=rms_total_linha,
        mode="lines",
        name=f"RMS total = {rms_total:.2f}",
        line=dict(width=3, dash="dash"),
        hovertemplate="RMS total: %{y:.2f}<extra></extra>",
    )
)
fig.update_layout(
    title="Analise RMS do sinal selecionado",
    xaxis_title=coluna_tempo,
    yaxis_title=coluna_sinal,
    hovermode="closest",
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
