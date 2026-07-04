from pathlib import Path

import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
GIF_CAMPO = BASE_DIR / "imagens" / "AnaliseDinamica.gif"

st.set_page_config(
    page_title="SIC-SFCL Dashboard",
    layout="wide",
)

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
    .gif-frame {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(15, 23, 42, 0.10);
        box-shadow: 0 18px 50px rgba(15, 23, 42, 0.10);
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
            Dashboard para visualizar sinais, avaliar o material magnetico e comparar
            geometrias que reduzem a corrente de falta sem impor queda de tensao excessiva.
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
            <strong>~10 A</strong>
            <span>Alvo para corrente durante a falta.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

col_visual, col_resumo = st.columns([1.35, 0.9], gap="large")

with col_visual:
    st.markdown('<div class="section-title">Campo magnetico no tempo</div>', unsafe_allow_html=True)
    st.markdown('<div class="gif-frame">', unsafe_allow_html=True)
    if GIF_CAMPO.exists():
        st.image(GIF_CAMPO, use_container_width=True)
    else:
        st.info("Imagem da simulacao nao encontrada em imagens/AnaliseDinamica.gif.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_resumo:
    st.markdown('<div class="section-title">Ideia central</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="tool-card">
            <strong>Nucleo saturado em regime permanente</strong>
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
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-title">Ferramentas do dashboard</div>', unsafe_allow_html=True)

cards = st.columns(5)
ferramentas = [
    ("Curva B-H", "Material e permeabilidade."),
    ("Visualizar sinal", "Corrente e tensao no tempo."),
    ("RMS", "Valor eficaz do sinal."),
    ("Harmonicos", "FFT e percentual por ordem."),
    ("Otimizacao", "Viabilidade e sensibilidade."),
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