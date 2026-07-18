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
st.title("Análise de Harmônicos - FFT")

st.markdown(
    r"""
    O objetivo principal desta página e calcular os harmônicos de corrente durante
    o curto-circuito por meio da FFT. A forma geral da serie de Fourier pode ser
    escrita como:

    $$
    x(t) = \frac{a_0}{2} + \sum_{n=1}^{\infty}
    \left[a_n\cos(n\omega_0 t) + b_n\sin(n\omega_0 t)\right]
    $$

    A amplitude RMS de cada harmônico senoidal e dada por:

    $$
    X_{n,RMS} = \frac{X_{n,pico}}{\sqrt{2}}
    $$

    Assim, o dashboard destaca a amplitude RMS de cada ordem harmônica e o percentual
    em relação a fundamental.
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
COLUNA_TEMPO = "Time (s)"
EXEMPLOS = {
    "Sinal senoidal 60 Hz": Path("Dataset/harmonics/exemplo_sinal_60hz_senoidal.txt"),
    "Sinal com harmonicos 3, 5 e 7": Path("Dataset/harmonics/exemplo_sinal_60hz_com_harmonicos_3_5_7.txt"),
    "Sinal quadrado 60 Hz": Path("Dataset/harmonics/exemplo_sinal_60hz_quadrado.txt"),
    "Sinal triangular 60 Hz": Path("Dataset/harmonics/exemplo_sinal_60hz_triangular.txt"),
    "Sinal retificado 60 Hz": Path("Dataset/harmonics/exemplo_sinal_60hz_retificado.txt"),
}


def nome_sinal_sintetico(nome_arquivo):
    nome = nome_arquivo.lower().removesuffix(".txt")
    if nome.startswith("exemplo_sinal_60hz_"):
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

def selecionar_arquivo():
    with st.sidebar:
        st.header("Arquivo")
        arquivo_enviado = st.file_uploader(
            "Selecione um arquivo TXT do COMSOL",
            type=["txt"],
            key="upload_harmonicos",
        )

        if arquivo_enviado is not None:
            return arquivo_enviado.getvalue(), arquivo_enviado.name

        if EXEMPLOS:
            nome_exemplo = st.selectbox(
                "Arquivo de exemplo",
                list(EXEMPLOS.keys()),
                key="exemplo_harmonicos",
            )
            caminho_exemplo = EXEMPLOS[nome_exemplo]
            return caminho_exemplo.read_bytes(), caminho_exemplo.name

    st.info("Selecione um arquivo TXT para calcular os harm?nicos.")
    st.stop()



conteudo_arquivo, nome_arquivo = selecionar_arquivo()

try:
    sinal = carregar_txt(conteudo_arquivo, nome_arquivo)
except Exception as erro:
    st.error(f"Erro ao ler o arquivo TXT: {erro}")
    st.stop()

if sinal.empty:
    st.warning("O arquivo selecionado nao possui dados validos.")
    st.stop()

chaves = sorted(sinal[COLUNA_CHAVE].unique())
if len(chaves) == 1:
    chave_selecionada = chaves[0]
else:
    with st.sidebar:
        st.subheader("Selecao dos dados")
        chave_selecionada = st.selectbox("Combinacao", chaves)

with st.sidebar:
    colunas_numericas = COLUNAS_TXT.copy()
    coluna_tempo = COLUNA_TEMPO
    coluna_sinal = st.selectbox(
        "Coluna do sinal",
        colunas_numericas,
        index=colunas_numericas.index("Corrente de Curto (A)"),
    )

    st.subheader("FFT")
    limite_freq = st.number_input(
        "Limite de frequencia exibida [Hz]",
        min_value=1,
        max_value=10000,
        value=1600,
        step=100,
    )
    amplitude_minima = st.number_input(
        "Amplitude minima para destacar picos [RMS]",
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
    st.error("A combinacao precisa ter pelo menos dois pontos validos.")
    st.stop()

ordem = np.argsort(tempo)
tempo = tempo[ordem]
vout = vout[ordem]

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
vout = vout[mascara_tempo]

if len(tempo) < 2:
    st.error("O intervalo de tempo selecionado precisa ter pelo menos dois pontos validos.")
    st.stop()

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

mascara_fundamental = freq_positiva > 0
if not np.any(mascara_fundamental):
    st.error("Nao foi possivel estimar a frequencia fundamental do sinal.")
    st.stop()
frequencia_fundamental_estimada = float(
    freq_positiva[mascara_fundamental][
        np.argmax(rms_positiva[mascara_fundamental])
    ]
)
frequencia_maxima_fundamental = max(float(np.max(freq_positiva)), 1e-6)
frequencia_fundamental_padrao = min(
    max(frequencia_fundamental_estimada, 1e-6),
    frequencia_maxima_fundamental,
)

with st.sidebar:
    frequencia_fundamental = st.number_input(
        "Frequencia fundamental [Hz]",
        min_value=1e-6,
        max_value=frequencia_maxima_fundamental,
        value=frequencia_fundamental_padrao,
        step=1.0,
        format="%.6f",
        help="Use a frequencia estimada ou informe manualmente a fundamental para calcular as ordens harmonicas.",
    )

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

st.success(f"Arquivo carregado: {nome_arquivo} | Combinacao: {chave_selecionada}")

col1, col2, col3 = st.columns(3)
col1.metric("Pontos analisados", N)
col2.metric("Amostragem estimada", f"{fs:.2f} Hz")
col3.metric("Fundamental usada", f"{frequencia_fundamental:.2f} Hz", delta=f"Estimada: {frequencia_fundamental_estimada:.2f} Hz")

fig_fft = go.Figure()
fig_fft.add_trace(
    go.Bar(
        x=freq_harmonicas,
        y=rms_harmonicas,
        name="Harmonicos RMS",
        width=frequencia_fundamental * 0.35,
        hovertemplate=(
            "Harmonico: %{customdata}<br>"
            "Frequencia: %{x:.2f} Hz<br>"
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
        name=f"Componentes >= {amplitude_minima:.4f} RMS",
        text=[
            f"n={int(h)}<br>{f:.0f} Hz<br>{a:.4f} RMS<br>{p:.2f}%"
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
            "Frequencia: %{x:.2f} Hz<br>"
            "Amplitude RMS: %{y:.6f}<br>"
            "Percentual: %{customdata:.2f}%<extra></extra>"
        ),
        customdata=percentual_picos,
    )
)
fig_fft.update_layout(
    title="Transformada Rapida de Fourier - Harmonicos em RMS",
    xaxis_title="Frequencia harmonica [Hz]",
    yaxis_title="Amplitude RMS",
    hovermode="closest",
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

st.plotly_chart(fig_fft, width="stretch")

dados_fft = pd.DataFrame({
    "Harmonico": harmonicos,
    "Frequencia [Hz]": freq_harmonicas,
    "Amplitude RMS": rms_harmonicas,
    "Percentual em relacao ao n=1 [%]": percentual_harmonicas,
})

st.dataframe(
    dados_fft.style.format({
        "Frequencia [Hz]": "{:.2f}",
        "Amplitude RMS": "{:.6f}",
        "Percentual em relacao ao n=1 [%]": "{:.2f}",
    }),
    width="stretch",
    hide_index=True,
)

st.subheader("Sinal selecionado no dominio do tempo")

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
    hovermode="closest",
    template="plotly_white",
    height=500,
)
fig_sinal.update_xaxes(showgrid=True)
fig_sinal.update_yaxes(showgrid=True)

st.plotly_chart(fig_sinal, width="stretch")