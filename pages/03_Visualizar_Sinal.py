from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from dashboard_footer import mostrar_rodape


st.set_page_config(
    page_title="Visualizar sinal",
    layout="wide",
)

mostrar_rodape()

st.title("Visualizar sinal")
st.caption("Corrente de curto e queda de tensao no dominio do tempo")


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
COLUNA_TEMPO = "Time (s)"
COLUNA_CORRENTE = "Corrente de Curto (A)"
COLUNA_TENSAO = "Queda de Tensao (V)"
COLUNAS_PARAMETROS = ["H (cm)", "W (cm)", "N_DC", "N_AC"]
COR_CORRENTE = "#DC2626"
COR_TENSAO = "#0B4DDB"
DASHES_CASOS = ["solid", "dash", "dot", "dashdot", "longdash", "longdashdot"]
EXEMPLOS = {
    "Sinal COMSOL - otimizacao 28A 16V": Path("Dataset/signal/otimizacao 28A 16V.txt"),
    "Sinal senoidal 60 Hz": Path("Dataset/harmonics/sinal_60hz_senoidal.txt"),
    "Sinal com harmonicos 3, 5 e 7": Path("Dataset/harmonics/sinal_60hz_com_harmonicos_3_5_7.txt"),
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
            "Selecione um arquivo TXT exportado do COMSOL",
            type=["txt"],
        )
        if arquivo is None:
            st.warning("Selecione um arquivo TXT para visualizar os sinais.")
            st.stop()
        return arquivo.getvalue(), arquivo.name

    nome_exemplo = st.selectbox("Arquivo de exemplo", list(EXEMPLOS))
    caminho = EXEMPLOS[nome_exemplo]
    return caminho.read_bytes(), caminho.name


@st.cache_data(show_spinner="Carregando arquivo TXT...")
def carregar_txt(conteudo_arquivo, nome_arquivo):
    dados = pd.read_csv(
        BytesIO(conteudo_arquivo),
        sep=r"\s+",
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


def filtrar_sinal(dados, chave):
    sinal = dados[dados[COLUNA_CHAVE] == chave].copy()
    sinal = sinal.sort_values(COLUNA_TEMPO)
    mascara_valida = (
        np.isfinite(sinal[COLUNA_TEMPO])
        & np.isfinite(sinal[COLUNA_CORRENTE])
        & np.isfinite(sinal[COLUNA_TENSAO])
    )
    return sinal[mascara_valida]


conteudo_arquivo, nome_arquivo = selecionar_arquivo()

try:
    dados = carregar_txt(conteudo_arquivo, nome_arquivo)
except Exception as erro:
    st.error(f"Erro ao ler o arquivo TXT: {erro}")
    st.stop()

if dados.empty:
    st.warning("O arquivo selecionado nao possui dados validos.")
    st.stop()

chaves = sorted(dados[COLUNA_CHAVE].unique())

with st.sidebar:
    st.header("Selecao")
    if len(chaves) == 1:
        chaves_selecionadas = chaves
    else:
        chaves_selecionadas = st.multiselect(
            "Combinacoes",
            chaves,
            default=chaves[:1],
        )

    sinal_exibido = st.radio(
        "Sinal exibido",
        ["Ambos", "Somente corrente", "Somente tensao"],
        horizontal=False,
    )

    modo_linha = st.radio(
        "Modo de exibicao",
        ["Linhas", "Linhas e marcadores"],
        horizontal=False,
    )

    tempo_minimo = float(dados[COLUNA_TEMPO].min())
    tempo_maximo = float(dados[COLUNA_TEMPO].max())
    tempo_padrao_final = min(0.1, tempo_maximo)
    faixa_tempo = st.slider(
        "Intervalo exibido (s)",
        min_value=round(tempo_minimo, 4),
        max_value=round(tempo_maximo, 4),
        value=(round(tempo_minimo, 4), round(tempo_padrao_final, 4)),
        step=0.001,
    )

    mostrar_grade = st.checkbox("Mostrar grade", value=True)

if not chaves_selecionadas:
    st.warning("Selecione pelo menos uma combinacao para visualizar.")
    st.stop()

sinais_por_chave = {
    chave: filtrar_sinal(dados, chave)
    for chave in chaves_selecionadas
}
sinais_por_chave = {
    chave: sinal[
        sinal[COLUNA_TEMPO].between(faixa_tempo[0], faixa_tempo[1])
    ]
    for chave, sinal in sinais_por_chave.items()
}
sinais_por_chave = {
    chave: sinal
    for chave, sinal in sinais_por_chave.items()
    if len(sinal) >= 2
}

if not sinais_por_chave:
    st.error("Nenhuma combinacao selecionada possui pelo menos dois pontos validos.")
    st.stop()

primeiro_sinal = next(iter(sinais_por_chave.values()))
parametros = primeiro_sinal[COLUNAS_PARAMETROS].iloc[0]
total_pontos = sum(len(sinal) for sinal in sinais_por_chave.values())
sinais_sinteticos = all(chave == "Sinal qualquer" for chave in sinais_por_chave)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Sinais", len(sinais_por_chave))
col2.metric("Pontos exibidos", total_pontos)
if sinais_sinteticos:
    col3.metric("Fonte", "Sinal sintetico")
    col4.metric("Parametros", "Nao aplicavel")
else:
    col3.metric("Primeira H/W", f"{parametros['H (cm)']:.0f} / {parametros['W (cm)']:.2f}")
    col4.metric("Primeiras espiras", f"DC {parametros['N_DC']:.0f} | AC {parametros['N_AC']:.0f}")
mostrar_corrente = sinal_exibido in ["Ambos", "Somente corrente"]
mostrar_tensao = sinal_exibido in ["Ambos", "Somente tensao"]
modo_plotly = "lines+markers" if modo_linha == "Linhas e marcadores" else "lines"

fig = make_subplots(specs=[[{"secondary_y": True}]])

for indice, (chave, sinal) in enumerate(sinais_por_chave.items()):
    dash = DASHES_CASOS[indice % len(DASHES_CASOS)]
    nome_curto = chave

    if mostrar_corrente:
        fig.add_trace(
            go.Scatter(
                x=sinal[COLUNA_TEMPO],
                y=sinal[COLUNA_CORRENTE],
                mode=modo_plotly,
                name=f"Corrente - {nome_curto}",
                line=dict(color=COR_CORRENTE, width=2.4, dash=dash),
                marker=dict(size=5),
                customdata=np.repeat(chave, len(sinal)),
                hovertemplate=(
                    "Combinacao: %{customdata}<br>"
                    "Tempo: %{x:.6f} s<br>"
                    "Corrente: %{y:.4f} A<extra></extra>"
                ),
            ),
            secondary_y=False,
        )

    if mostrar_tensao:
        fig.add_trace(
            go.Scatter(
                x=sinal[COLUNA_TEMPO],
                y=sinal[COLUNA_TENSAO],
                mode=modo_plotly,
                name=f"Tensao - {nome_curto}",
                line=dict(color=COR_TENSAO, width=2.4, dash=dash),
                marker=dict(size=5),
                customdata=np.repeat(chave, len(sinal)),
                hovertemplate=(
                    "Combinacao: %{customdata}<br>"
                    "Tempo: %{x:.6f} s<br>"
                    "Tensao: %{y:.4f} V<extra></extra>"
                ),
            ),
            secondary_y=True,
        )

fig.update_layout(
    title=f"Sinais no dominio do tempo | {faixa_tempo[0]:.3f} a {faixa_tempo[1]:.3f} s",
    template="plotly_white",
    height=720,
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
    ),
    margin=dict(t=90, r=80, b=70, l=80),
)
fig.update_xaxes(
    title_text="Tempo (s)",
    showgrid=mostrar_grade,
    gridcolor="rgba(0,0,0,0.10)",
)
fig.update_yaxes(
    title_text="Corrente de curto (A)",
    showgrid=mostrar_grade,
    gridcolor="rgba(0,0,0,0.10)",
    secondary_y=False,
    visible=mostrar_corrente,
)
fig.update_yaxes(
    title_text="Queda de tensao (V)",
    showgrid=False,
    secondary_y=True,
    visible=mostrar_tensao,
)

st.plotly_chart(fig, use_container_width=True)
