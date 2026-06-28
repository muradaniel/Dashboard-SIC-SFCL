import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Análise de Harmônicos", layout="wide")

# =========================
# INICIALIZAÇÃO DA MEMÓRIA
# =========================

if "sinal" not in st.session_state:
    st.session_state.sinal = None

if "nome_arquivo" not in st.session_state:
    st.session_state.nome_arquivo = None


# =========================
# TÍTULO + SELETOR DE ARQUIVO
# =========================

col_titulo, col_arquivo = st.columns([2, 1])

with col_titulo:
    st.title("Análise de Harmônicos - FFT")

with col_arquivo:
    arquivo_csv = st.file_uploader(
        "Escolha o arquivo CSV",
        type=["csv"]
    )


# =========================
# LEITURA E ARMAZENAMENTO DO CSV
# =========================

if arquivo_csv is not None:
    sinal_lido = pd.read_csv(arquivo_csv, sep=";")

    st.session_state.sinal = sinal_lido
    st.session_state.nome_arquivo = arquivo_csv.name

if st.session_state.sinal is None:
    st.warning("Selecione um arquivo CSV para iniciar a análise.")
    st.stop()

sinal = st.session_state.sinal

st.success(f"Arquivo carregado: {st.session_state.nome_arquivo}")


# =========================
# SELEÇÃO DAS COLUNAS
# =========================

colunas = sinal.columns.tolist()

col_tempo, col_sinal = st.columns(2)

with col_tempo:
    coluna_tempo = st.selectbox(
        "Selecione a coluna de tempo",
        colunas,
        index=colunas.index("tempo_s") if "tempo_s" in colunas else 0
    )

with col_sinal:
    coluna_vout = st.selectbox(
        "Selecione a coluna do sinal",
        colunas,
        index=colunas.index("senoide") if "senoide" in colunas else 1
    )


# =========================
# TRATAMENTO DOS DADOS
# =========================

tempo = np.array(sinal[coluna_tempo], dtype=float)
vout = np.array(sinal[coluna_vout], dtype=float)

# Remove valores inválidos
mascara_valida = np.isfinite(tempo) & np.isfinite(vout)
tempo = tempo[mascara_valida]
vout = vout[mascara_valida]

if len(tempo) < 2:
    st.error("O arquivo precisa ter pelo menos dois pontos válidos.")
    st.stop()

# Ordena pelo tempo
ordem = np.argsort(tempo)
tempo = tempo[ordem]
vout = vout[ordem]


# =========================
# ENTRADAS INTERATIVAS
# =========================

col1, col2, col3 = st.columns(3)

with col1:
    limite_freq = st.number_input(
        "Limite de frequência exibida [Hz]",
        min_value=1,
        max_value=10000,
        value=1600,
        step=100
    )

with col2:
    frequencia_fundamental = st.number_input(
        "Frequência fundamental [Hz]",
        min_value=1.0,
        max_value=1000.0,
        value=60.0,
        step=1.0,
        format="%.2f"
    )

with col3:
    amplitude_minima = st.number_input(
        "Amplitude mínima para destacar picos [RMS]",
        min_value=0.0,
        value=0.10,
        step=0.01,
        format="%.4f"
    )


# =========================
# CÁLCULO DA FFT
# =========================

dt = np.mean(np.diff(tempo))
fs = 1 / dt
N = len(vout)

fft = np.fft.fft(vout)
fft_freq = np.fft.fftfreq(N, d=dt)

fft_mag = np.abs(fft) / N

# Espectro unilateral em valor de pico
fft_mag[1:N // 2] = 2 * fft_mag[1:N // 2]

# Conversão para RMS
fft_rms = fft_mag.copy()

# A componente DC não é dividida por raiz de 2
fft_rms[1:N // 2] = fft_rms[1:N // 2] / np.sqrt(2)


# =========================
# FREQUÊNCIAS POSITIVAS
# =========================

mascara_positiva = fft_freq >= 0

freq_positiva = fft_freq[mascara_positiva]
rms_positiva = fft_rms[mascara_positiva]


# =========================
# APENAS MÚLTIPLOS INTEIROS DA FUNDAMENTAL
# =========================

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


# =========================
# FILTRO DE AMPLITUDE MÍNIMA
# =========================

mascara_picos = rms_harmonicas >= amplitude_minima

freq_picos = freq_harmonicas[mascara_picos]
rms_picos = rms_harmonicas[mascara_picos]
harmonicos_picos = harmonicos[mascara_picos]
percentual_picos = percentual_harmonicas[mascara_picos]


# =========================
# GRÁFICO 1 - FFT RMS SOMENTE EM HARMÔNICOS
# =========================

fig_fft = go.Figure()

fig_fft.add_trace(
    go.Bar(
        x=freq_harmonicas,
        y=rms_harmonicas,
        name="Harmônicos RMS",
        width=frequencia_fundamental * 0.35,
        hovertemplate=
        "Harmônico: %{customdata}ª<br>"
        "Frequência: %{x:.2f} Hz<br>"
        "Amplitude RMS: %{y:.6f}<br>"
        "Percentual: %{text:.2f}%<extra></extra>",
        customdata=harmonicos,
        text=percentual_harmonicas
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
            for h, f, a, p in zip(harmonicos_picos, freq_picos, rms_picos, percentual_picos)
        ],
        textposition="top center",
        marker=dict(size=9),
        hovertemplate=
        "Frequência: %{x:.2f} Hz<br>"
        "Amplitude RMS: %{y:.6f}<br>"
        "Percentual: %{customdata:.2f}%<extra></extra>",
        customdata=percentual_picos
    )
)

fig_fft.update_layout(
    title="Transformada Rápida de Fourier - Harmônicos em RMS",
    xaxis_title="Frequência harmônica [Hz]",
    yaxis_title="Amplitude RMS",
    hovermode="x unified",
    template="plotly_white",
    height=600
)

fig_fft.update_xaxes(
    showgrid=True,
    tickmode="array",
    tickvals=freq_harmonicas,
    ticktext=[f"{int(f)}" for f in freq_harmonicas]
)

fig_fft.update_yaxes(showgrid=True)

st.plotly_chart(fig_fft, use_container_width=True)

dados_fft = pd.DataFrame({
    "Harmônico": harmonicos,
    "Frequência [Hz]": freq_harmonicas,
    "Amplitude RMS": rms_harmonicas,
    "Percentual em relação ao n=1 [%]": percentual_harmonicas
})

st.dataframe(
    dados_fft.style.format({
        "Frequência [Hz]": "{:.2f}",
        "Amplitude RMS": "{:.6f}",
        "Percentual em relação ao n=1 [%]": "{:.2f}"
    }),
    use_container_width=True,
    hide_index=True
)


# =========================
# GRÁFICO 2 - SINAL PURO
# =========================

st.subheader("Sinal puro no domínio do tempo")

fig_sinal = go.Figure()

fig_sinal.add_trace(
    go.Scatter(
        x=tempo,
        y=vout,
        mode="lines",
        name="Sinal puro",
        line=dict(width=2),
        hovertemplate=
        "Tempo: %{x:.6f} s<br>"
        "Amplitude: %{y:.6f}<extra></extra>"
    )
)

fig_sinal.update_layout(
    title="Sinal puro",
    xaxis_title="Tempo [s]",
    yaxis_title="Amplitude",
    hovermode="x unified",
    template="plotly_white",
    height=500
)

fig_sinal.update_xaxes(showgrid=True)
fig_sinal.update_yaxes(showgrid=True)

st.plotly_chart(fig_sinal, use_container_width=True)
