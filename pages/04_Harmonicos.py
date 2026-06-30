from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Análise de Harmônicos", layout="wide")
st.title("Análise de Harmônicos - FFT")

BASE_DIR = Path(__file__).resolve().parents[1]
PASTA_DADOS = BASE_DIR / "Dataset" / "optimization"

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
def carregar_txt(caminho, data_modificacao):
    dados = pd.read_csv(
        caminho,
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


if not PASTA_DADOS.exists():
    st.error(f"Pasta de dados não encontrada: {PASTA_DADOS}")
    st.stop()

arquivos_txt = tuple(sorted(PASTA_DADOS.glob("*.txt")))

if not arquivos_txt:
    st.error(f"Nenhum arquivo TXT encontrado em: {PASTA_DADOS}")
    st.stop()

nomes_arquivos = [arquivo.name for arquivo in arquivos_txt]
arquivos_por_nome = dict(zip(nomes_arquivos, arquivos_txt))

with st.sidebar:
    st.header("Entrada")
    nome_arquivo = st.selectbox("Arquivo TXT", nomes_arquivos)

arquivo = arquivos_por_nome[nome_arquivo]

try:
    sinal = carregar_txt(arquivo, arquivo.stat().st_mtime_ns)
except Exception as erro:
    st.error(f"Erro ao ler o arquivo TXT: {erro}")
    st.stop()

if sinal.empty:
    st.warning("O arquivo selecionado não possui dados válidos.")
    st.stop()

with st.sidebar:
    st.subheader("Seleção dos dados")
    chaves = sorted(sinal[COLUNA_CHAVE].unique())
    chave_selecionada = st.selectbox("Combinação", chaves)

    colunas_numericas = COLUNAS_TXT.copy()
    coluna_tempo = st.selectbox(
        "Coluna de tempo",
        colunas_numericas,
        index=colunas_numericas.index("Time (s)"),
    )
    coluna_sinal = st.selectbox(
        "Coluna do sinal",
        colunas_numericas,
        index=colunas_numericas.index("Corrente de Curto (A)"),
    )

    st.subheader("FFT")
    limite_freq = st.number_input(
        "Limite de frequência exibida [Hz]",
        min_value=1,
        max_value=10000,
        value=1600,
        step=100,
    )
    frequencia_fundamental = st.number_input(
        "Frequência fundamental [Hz]",
        min_value=1.0,
        max_value=1000.0,
        value=60.0,
        step=1.0,
        format="%.2f",
    )
    amplitude_minima = st.number_input(
        "Amplitude mínima para destacar picos [RMS]",
        min_value=0.0,
        value=0.10,
        step=0.01,
        format="%.4f",
    )

dados_selecionados = sinal[sinal[COLUNA_CHAVE] == chave_selecionada].copy()

tempo = pd.to_numeric(
    dados_selecionados[coluna_tempo],
    errors="coerce",
).to_numpy()
vout = pd.to_numeric(
    dados_selecionados[coluna_sinal],
    errors="coerce",
).to_numpy()

mascara_valida = np.isfinite(tempo) & np.isfinite(vout)
tempo = tempo[mascara_valida]
vout = vout[mascara_valida]

if len(tempo) < 2:
    st.error("A combinação precisa ter pelo menos dois pontos válidos.")
    st.stop()

ordem = np.argsort(tempo)
tempo = tempo[ordem]
vout = vout[ordem]

intervalos = np.diff(tempo)
intervalos_validos = intervalos[intervalos > 0]

if len(intervalos_validos) == 0:
    st.error("A coluna de tempo precisa ter valores crescentes para calcular a FFT.")
    st.stop()

dt = float(np.median(intervalos_validos))
fs = 1 / dt
N = len(vout)

fft = np.fft.fft(vout)
fft_freq = np.fft.fftfreq(N, d=dt)
fft_mag = np.abs(fft) / N
fft_mag[1:N // 2] = 2 * fft_mag[1:N // 2]

fft_rms = fft_mag.copy()
fft_rms[1:N // 2] = fft_rms[1:N // 2] / np.sqrt(2)

mascara_positiva = fft_freq >= 0
freq_positiva = fft_freq[mascara_positiva]
rms_positiva = fft_rms[mascara_positiva]

numero_max_harmonico = int(limite_freq // frequencia_fundamental)
harmonicos = np.arange(0, numero_max_harmonico + 1)
freq_harmonicas = harmonicos * frequencia_fundamental

rms_harmonicas = []
for freq_alvo in freq_harmonicas:
    indice_mais_proximo = np.argmin(np.abs(freq_positiva - freq_alvo))
    rms_harmonicas.append(rms_positiva[indice_mais_proximo])

rms_harmonicas = np.array(rms_harmonicas)

if len(rms_harmonicas) > 1 and rms_harmonicas[1] != 0:
    percentual_harmonicas = (rms_harmonicas / rms_harmonicas[1]) * 100
else:
    percentual_harmonicas = np.zeros_like(rms_harmonicas)

mascara_picos = rms_harmonicas >= amplitude_minima
freq_picos = freq_harmonicas[mascara_picos]
rms_picos = rms_harmonicas[mascara_picos]
harmonicos_picos = harmonicos[mascara_picos]
percentual_picos = percentual_harmonicas[mascara_picos]

st.success(f"Arquivo carregado: {nome_arquivo} | Combinação: {chave_selecionada}")

col1, col2, col3 = st.columns(3)
col1.metric("Pontos analisados", N)
col2.metric("Amostragem estimada", f"{fs:.2f} Hz")
col3.metric("Coluna analisada", coluna_sinal)

fig_fft = go.Figure()
fig_fft.add_trace(
    go.Bar(
        x=freq_harmonicas,
        y=rms_harmonicas,
        name="Harmônicos RMS",
        width=frequencia_fundamental * 0.35,
        hovertemplate=(
            "Harmônico: %{customdata}ª<br>"
            "Frequência: %{x:.2f} Hz<br>"
            "Amplitude RMS: %{y:.6f}<br>"
            "Percentual: %{text:.2f}%<extra></extra>"
        ),
        customdata=harmonicos,
        text=percentual_harmonicas,
    )
)
fig_fft.add_trace(
    go.Scatter(
        x=freq_picos,
        y=rms_picos,
        mode="markers+text",
        name=f"Componentes ≥ {amplitude_minima:.4f} RMS",
        text=[
            f"{int(h)}ª<br>{f:.0f} Hz<br>{a:.4f} RMS<br>{p:.2f}%"
            for h, f, a, p in zip(
                harmonicos_picos,
                freq_picos,
                rms_picos,
                percentual_picos,
            )
        ],
        textposition="top center",
        marker=dict(size=9),
        hovertemplate=(
            "Frequência: %{x:.2f} Hz<br>"
            "Amplitude RMS: %{y:.6f}<br>"
            "Percentual: %{customdata:.2f}%<extra></extra>"
        ),
        customdata=percentual_picos,
    )
)
fig_fft.update_layout(
    title="Transformada Rápida de Fourier - Harmônicos em RMS",
    xaxis_title="Frequência harmônica [Hz]",
    yaxis_title="Amplitude RMS",
    hovermode="x unified",
    template="plotly_white",
    height=600,
)
fig_fft.update_xaxes(
    showgrid=True,
    tickmode="array",
    tickvals=freq_harmonicas,
    ticktext=[f"{int(f)}" for f in freq_harmonicas],
)
fig_fft.update_yaxes(showgrid=True)

st.plotly_chart(fig_fft, use_container_width=True)

dados_fft = pd.DataFrame({
    "Harmônico": harmonicos,
    "Frequência [Hz]": freq_harmonicas,
    "Amplitude RMS": rms_harmonicas,
    "Percentual em relação ao n=1 [%]": percentual_harmonicas,
})

st.dataframe(
    dados_fft.style.format({
        "Frequência [Hz]": "{:.2f}",
        "Amplitude RMS": "{:.6f}",
        "Percentual em relação ao n=1 [%]": "{:.2f}",
    }),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Sinal selecionado no domínio do tempo")

fig_sinal = go.Figure()
fig_sinal.add_trace(
    go.Scatter(
        x=tempo,
        y=vout,
        mode="lines",
        name="Sinal selecionado",
        line=dict(width=2),
        hovertemplate=(
            "Tempo: %{x:.6f} s<br>"
            "Amplitude: %{y:.6f}<extra></extra>"
        ),
    )
)
fig_sinal.update_layout(
    title="Sinal selecionado",
    xaxis_title=coluna_tempo,
    yaxis_title=coluna_sinal,
    hovermode="x unified",
    template="plotly_white",
    height=500,
)
fig_sinal.update_xaxes(showgrid=True)
fig_sinal.update_yaxes(showgrid=True)

st.plotly_chart(fig_sinal, use_container_width=True)