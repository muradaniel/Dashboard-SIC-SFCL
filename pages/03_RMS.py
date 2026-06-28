import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go


# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Análise RMS",
    layout="wide"
)

st.title("Análise RMS de Sinais Elétricos")


# =========================================================
# MEMÓRIA DA SESSÃO
# =========================================================

if "dados_rms" not in st.session_state:
    st.session_state.dados_rms = None

if "nome_arquivo_rms" not in st.session_state:
    st.session_state.nome_arquivo_rms = None


# =========================================================
# UPLOAD DO CSV
# =========================================================

arquivo_csv = st.file_uploader(
    "Carregue um arquivo CSV com o sinal no domínio do tempo",
    type=["csv"]
)

if arquivo_csv is not None:
    try:
        dados = pd.read_csv(arquivo_csv, sep=None, engine="python")
        st.session_state.dados_rms = dados
        st.session_state.nome_arquivo_rms = arquivo_csv.name

    except Exception as erro:
        st.error(f"Erro ao ler o arquivo CSV: {erro}")
        st.stop()


if st.session_state.dados_rms is None:
    st.warning("Carregue um arquivo CSV para iniciar a análise.")
    st.stop()


dados = st.session_state.dados_rms

st.success(f"Arquivo carregado: {st.session_state.nome_arquivo_rms}")


# =========================================================
# SELEÇÃO DAS COLUNAS
# =========================================================

st.subheader("Seleção das colunas")

colunas = dados.columns.tolist()

col1, col2 = st.columns(2)

with col1:
    coluna_tempo = st.selectbox(
        "Selecione a coluna de tempo",
        colunas,
        index=0
    )

with col2:
    coluna_sinal = st.selectbox(
        "Selecione a coluna do sinal elétrico",
        colunas,
        index=1 if len(colunas) > 1 else 0
    )


# =========================================================
# TRATAMENTO DOS DADOS
# =========================================================

try:
    tempo = pd.to_numeric(dados[coluna_tempo], errors="coerce").to_numpy()
    sinal = pd.to_numeric(dados[coluna_sinal], errors="coerce").to_numpy()

except Exception as erro:
    st.error(f"Erro ao converter as colunas selecionadas: {erro}")
    st.stop()


mascara_valida = np.isfinite(tempo) & np.isfinite(sinal)

tempo = tempo[mascara_valida]
sinal = sinal[mascara_valida]

if len(tempo) < 2:
    st.error("O arquivo precisa ter pelo menos dois pontos válidos de tempo e sinal.")
    st.stop()


# Ordena os dados pelo tempo
ordem = np.argsort(tempo)
tempo = tempo[ordem]
sinal = sinal[ordem]


# =========================================================
# CÁLCULO DO RMS TOTAL
# =========================================================

rms_total = np.sqrt(np.mean(sinal ** 2))

rms_total_linha = np.full_like(sinal, rms_total)


# =========================================================
# EXIBIÇÃO DO VALOR RMS TOTAL
# =========================================================

st.subheader("Resultado RMS total")

st.metric(
    label="Valor RMS total do sinal",
    value=f"{rms_total:.2f}"
)


# =========================================================
# GRÁFICO ÚNICO
# =========================================================

st.subheader("Sinal original e RMS total")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=tempo,
        y=sinal,
        mode="lines",
        name="Sinal original",
        line=dict(width=2),
        hovertemplate=
        "Tempo: %{x:.6f} s<br>"
        "Sinal: %{y:.6f}<extra></extra>"
    )
)

fig.add_trace(
    go.Scatter(
        x=tempo,
        y=rms_total_linha,
        mode="lines",
        name=f"RMS total = {rms_total:.2f}",
        line=dict(width=3, dash="dash"),
        hovertemplate=
        "Tempo: %{x:.6f} s<br>"
        "RMS total: %{y:.2f}<extra></extra>"
    )
)

fig.update_layout(
    title="Análise RMS do sinal elétrico",
    xaxis_title="Tempo [s]",
    yaxis_title="Amplitude / RMS",
    hovermode="x unified",
    template="plotly_white",
    height=650,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

fig.update_xaxes(showgrid=True)
fig.update_yaxes(showgrid=True)

st.plotly_chart(fig, use_container_width=True)
