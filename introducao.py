from pathlib import Path
import base64
import sys

import streamlit as st
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from dashboard_footer import mostrar_rodape

TOPOLOGIAS_IMG = BASE_DIR / "imagens" / "topologias.png"
ICON_PATH = BASE_DIR / "imagens" / "coil.png"


def imagem_base64(caminho):
    return base64.b64encode(caminho.read_bytes()).decode("ascii")


mostrar_rodape()

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
        max-width: none;
    }
    .hero {
        border: 1px solid rgba(15, 23, 42, 0.10);
        border-radius: 14px;
        padding: 2.2rem 2.4rem;
        background:
            linear-gradient(135deg, rgba(248, 250, 252, 0.98), rgba(226, 232, 240, 0.72)),
            radial-gradient(circle at top right, rgba(220, 38, 38, 0.16), transparent 34%),
            radial-gradient(circle at bottom left, rgba(37, 99, 235, 0.16), transparent 36%);
        box-shadow: 0 18px 55px rgba(15, 23, 42, 0.08);
        margin-bottom: 1.35rem;
    }
    .eyebrow {
        color: #2563eb;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }
    .hero h1 {
        color: #0f172a;
        font-size: clamp(2rem, 4.5vw, 4rem);
        line-height: 1.02;
        margin: 0 0 0.85rem 0;
        letter-spacing: 0;
    }
    .hero p {
        color: #475569;
        font-size: 1.08rem;
        max-width: 780px;
        margin: 0;
    }
    .metric-card {
        border: 1px solid rgba(15, 23, 42, 0.10);
        border-radius: 10px;
        padding: 1rem 1.1rem;
        background: #ffffff;
        min-height: 116px;
    }
    .metric-card small {
        color: #64748b;
        font-weight: 650;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .metric-card strong {
        display: block;
        color: #0f172a;
        font-size: 1.75rem;
        margin-top: 0.35rem;
    }
    .metric-card span {
        color: #64748b;
        font-size: 0.92rem;
    }
    .section-title {
        color: #0f172a;
        font-size: 1.22rem;
        font-weight: 750;
        margin: 1rem 0 0.4rem 0;
    }
    .tool-card {
        border-left: 4px solid #2563eb;
        background: #ffffff;
        border-radius: 8px;
        padding: 0.95rem 1rem;
        border-top: 1px solid rgba(15, 23, 42, 0.08);
        border-right: 1px solid rgba(15, 23, 42, 0.08);
        border-bottom: 1px solid rgba(15, 23, 42, 0.08);
        min-height: 116px;
    }
    .tool-card strong {
        color: #0f172a;
        display: block;
        margin-bottom: 0.32rem;
    }
    .tool-card span {
        color: #64748b;
        font-size: 0.93rem;
    }
    .media-frame {
        height: 560px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 14px;
        overflow: hidden;
        border: 0;
        box-shadow: none;
        background: transparent;
    }
    .media-frame img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        display: block;
    }
    div[data-testid="stPlotlyChart"],
    .stPlotlyChart {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
        <div class="eyebrow">TCC | SIC-SFCL</div>
        <h1>Limitador de corrente de curto-circuito</h1>
        <p>
            Dashboard para analise de dados de um limitador de corrente de curto-circuito
            de núcleo saturado e aberto, com tecnologia de supercondutores.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(
        """
        <div class="metric-card">
            <small>Regime nominal</small>
            <strong>5 A RMS</strong>
            <span>Referencia de operacao antes da falta.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m2:
    st.markdown(
        """
        <div class="metric-card">
            <small>Curto prospectivo</small>
            <strong>50 A RMS</strong>
            <span>Cenario sem limitacao ativa.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m3:
    st.markdown(
        """
        <div class="metric-card">
            <small>Meta de projeto</small>
            <strong>&ge;60%</strong>
            <span>Reducao minima da corrente de curto-circuito.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

st.markdown('<div class="section-title" style="text-align:center;">Topologias utilizadas no projeto</div>', unsafe_allow_html=True)
if TOPOLOGIAS_IMG.exists():
    topologias_base64 = imagem_base64(TOPOLOGIAS_IMG)
    st.markdown(
        f'<div class="media-frame"><img src="data:image/png;base64,{topologias_base64}" alt="Topologias utilizadas no projeto"></div>',
        unsafe_allow_html=True,
    )
else:
    st.info("Imagem das topologias nao encontrada em imagens/topologias.png.")

st.markdown('<div class="section-title">Ideia central</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="tool-card">
        <strong>Núcleo saturado em regime permanente</strong>
        <span>Baixa permeabilidade, baixa impedancia inserida no sistema.</span>
    </div>
    <br>
    <div class="tool-card" style="border-left-color:#dc2626;">
        <strong>Falta eletrica</strong>
        <span>A mudanca magnetica aumenta a indutancia e limita a corrente.</span>
    </div>
    <br>
    <div class="tool-card" style="border-left-color:#16a34a;">
        <strong>Escolha da geometria</strong>
        <span>Comparacao entre H, W, N_DC e N_AC para encontrar regioes viaveis.</span>
    </div>
    <br>
    <div class="tool-card" style="border-left-color:#2563eb;">
        <strong>Uso do supercondutor</strong>
        <span>O enrolamento supercondutor permite conduzir correntes elevadas com menos espiras de saturacao, reduzindo volume e perdas.</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">Ferramentas do dashboard</div>', unsafe_allow_html=True)

cards = st.columns(5)
ferramentas = [
    ("Curva B-H", "Material e permeabilidade."),
    ("Otimizacao", "Escolha do ponto de projeto."),
    ("Visualizar sinal", "Corrente e tensao no tempo."),
    ("RMS", "Valor eficaz do sinal."),
    ("Harmonicos", "FFT e percentual por ordem."),
]

for coluna, (titulo, descricao) in zip(cards, ferramentas):
    with coluna:
        st.markdown(
            f"""
            <div class="tool-card">
                <strong>{titulo}</strong>
                <span>{descricao}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )



