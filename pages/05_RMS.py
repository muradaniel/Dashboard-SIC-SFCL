from io import BytesIO
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dashboard_footer import mostrar_rodape

ICON_PATH = Path(__file__).resolve().parents[1] / "imagens" / "coil.png"



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
BASE_DIR = Path(__file__).resolve().parents[1]
PASTA_EXEMPLOS = BASE_DIR / "Dataset" / "root_mean_square"
EXEMPLOS = {
    caminho.stem: caminho
    for caminho in sorted(PASTA_EXEMPLOS.glob("*"))
    if caminho.suffix.lower() in {".csv", ".txt"}
}


def nome_sinal_sintetico(nome_arquivo):
    nome = nome_arquivo.lower().removesuffix(".txt")
    if nome.startswith("sinal_60hz_"):
        return "Sinal qualquer"
    if nome == "exemplo_127_vrms":
        return "Exemplo 127 VRMS"
    return None


@st.cache_data(show_spinner="Carregando arquivo TXT...")
def carregar_txt(conteudo_arquivo, nome_arquivo):
    dados = pd.read_csv(
        BytesIO(conteudo_arquivo),
        sep=r"\s{2,}",
        engine="python",
        comment="%",
        header=None,
        names=COLUNAS_TXT,
        usecols=range(len(COLUNAS_TXT)),
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


def selecionar_arquivo():
    with st.sidebar:
        st.header("Entrada")
        opcoes_entrada = ["Enviar arquivo"]
        if EXEMPLOS:
            opcoes_entrada.insert(0, "Usar exemplo")

        modo_entrada = st.radio(
            "Fonte dos dados",
            opcoes_entrada,
            horizontal=False,
        )

        if modo_entrada == "Usar exemplo":
            nomes_exemplos = sorted(EXEMPLOS.keys())
            indice_exemplo = 0
            if "exemplo_127_VRMS" in nomes_exemplos:
                indice_exemplo = nomes_exemplos.index("exemplo_127_VRMS")
            nome_exemplo = st.selectbox(
                "Arquivo de exemplo",
                nomes_exemplos,
                index=indice_exemplo,
            )
            caminho = EXEMPLOS[nome_exemplo]
            return caminho.read_bytes(), caminho.name

        arquivo = st.file_uploader(
            "Selecione um arquivo CSV ou TXT",
            type=["csv", "txt"],
        )

    if arquivo is None:
        st.warning("Selecione um arquivo ou escolha um exemplo para iniciar a analise.")
        st.stop()

    return arquivo.getvalue(), arquivo.name

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

    if nome_sinal_sintetico(nome_arquivo) == "Exemplo 127 VRMS" and "Queda de Tensao (V)" in colunas_numericas:
        indice_sinal = colunas_numericas.index("Queda de Tensao (V)")
    elif "Corrente de Curto (A)" in colunas_numericas:
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

tempo_minimo = float(np.min(tempo))
tempo_maximo = float(np.max(tempo))
if tempo_maximo > tempo_minimo:
    passo_tempo = max((tempo_maximo - tempo_minimo) / 1000, 1e-9)
    with st.sidebar:
        st.subheader("Filtro de tempo")
        faixa_tempo = st.slider(
            "Intervalo analisado (s)",
            min_value=tempo_minimo,
            max_value=tempo_maximo,
            value=(tempo_minimo, tempo_maximo),
            step=passo_tempo,
            format="%.6f",
        )
else:
    faixa_tempo = (tempo_minimo, tempo_maximo)

mascara_tempo = (tempo >= faixa_tempo[0]) & (tempo <= faixa_tempo[1])
tempo = tempo[mascara_tempo]
sinal = sinal[mascara_tempo]

if len(tempo) < 2:
    st.error("O intervalo de tempo selecionado precisa ter pelo menos dois pontos validos.")
    st.stop()

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
