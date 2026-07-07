from pathlib import Path
import base64
import sys

import numpy as np
import plotly.graph_objects as go
import streamlit as st
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from dashboard_footer import mostrar_rodape

GIF_CAMPO = BASE_DIR / "imagens" / "AnaliseDinamica.gif"
ICON_PATH = BASE_DIR / "imagens" / "coil.png"


def imagem_base64(caminho):
    return base64.b64encode(caminho.read_bytes()).decode("ascii")


def adicionar_cubo(fig, nome, centro, tamanho, cor, opacidade=1.0):
    cx, cy, cz = centro
    sx, sy, sz = tamanho
    x0, x1 = cx - sx / 2, cx + sx / 2
    y0, y1 = cy - sy / 2, cy + sy / 2
    z0, z1 = cz - sz / 2, cz + sz / 2
    vertices = np.array([
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
    ])
    faces = np.array([
        [0, 1, 2], [0, 2, 3], [4, 6, 5], [4, 7, 6],
        [0, 4, 5], [0, 5, 1], [1, 5, 6], [1, 6, 2],
        [2, 6, 7], [2, 7, 3], [3, 7, 4], [3, 4, 0],
    ])
    fig.add_trace(go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=faces[:, 0],
        j=faces[:, 1],
        k=faces[:, 2],
        name=nome,
        color=cor,
        opacity=opacidade,
        flatshading=True,
        hovertemplate=f"{nome}<extra></extra>",
    ))


def criar_figura_limitador_3d():
    fig = go.Figure()

    adicionar_cubo(
        fig,
        "Núcleo de ferro",
        (0, 0, 0),
        (0.46, 0.46, 3.1),
        "#5B6472",
        0.96,
    )

    theta_fita = np.linspace(0, 16 * np.pi, 1400)
    z_fita = np.linspace(-1.42, 1.42, theta_fita.size)
    raio_fita = 0.38
    meia_largura_fita = 0.18
    theta_bordas = np.column_stack([
        theta_fita - meia_largura_fita,
        theta_fita + meia_largura_fita,
    ])
    z_bordas = np.column_stack([
        z_fita - meia_largura_fita * 0.34,
        z_fita + meia_largura_fita * 0.34,
    ])
    x_fita = (raio_fita * np.cos(theta_bordas)).ravel()
    y_fita = (raio_fita * np.sin(theta_bordas)).ravel()
    z_fita_malha = z_bordas.ravel()
    faces_i = []
    faces_j = []
    faces_k = []
    for indice in range(theta_fita.size - 1):
        a = 2 * indice
        b = a + 1
        c = a + 2
        d = a + 3
        faces_i.extend([a, b])
        faces_j.extend([c, d])
        faces_k.extend([b, c])
    fig.add_trace(go.Mesh3d(
        x=x_fita,
        y=y_fita,
        z=z_fita_malha,
        i=faces_i,
        j=faces_j,
        k=faces_k,
        name="Enrolamento DC",
        color="#2563EB",
        opacity=0.96,
        flatshading=True,
        showlegend=True,
        hovertemplate="Enrolamento DC<extra></extra>",
    ))

    theta_ac = np.linspace(0, 75 * np.pi, 3200)
    z_ac = np.linspace(-1.55, 1.55, theta_ac.size)
    raio_x_ac = 0.56
    raio_y_ac = 0.56
    x_ac = raio_x_ac * np.cos(theta_ac)
    y_ac = raio_y_ac * np.sin(theta_ac)
    fig.add_trace(go.Scatter3d(
        x=x_ac,
        y=y_ac,
        z=z_ac,
        mode="lines",
        name="Enrolamento CA",
        line=dict(color="#DC2626", width=5),
        hovertemplate="Enrolamento CA<extra></extra>",
    ))


    fig.add_trace(go.Scatter3d(
        x=[0, -0.72, 0.78],
        y=[-0.64, -0.7, -0.72],
        z=[1.68, 0.52, -0.25],
        mode="text",
        text=["Núcleo de ferro", "Enrolamento DC", "Enrolamento CA"],
        textfont=dict(size=12, color="#0F172A"),
        showlegend=False,
        hoverinfo="skip",
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(eye=dict(x=1.8, y=2.2, z=1.15)),
        ),
        legend=dict(orientation="h", y=0.02, x=0.5, xanchor="center"),
        margin=dict(l=0, r=0, t=8, b=0),
        height=560,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


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

try:
    col_visual, col_modelo = st.columns(2, gap="large", vertical_alignment="center")
except TypeError:
    col_visual, col_modelo = st.columns(2, gap="large")

with col_visual:
    st.markdown('<div class="section-title" style="text-align:center;">Campo magnetico no tempo</div>', unsafe_allow_html=True)
    if GIF_CAMPO.exists():
        gif_base64 = imagem_base64(GIF_CAMPO)
        st.markdown(
            f'<div class="media-frame"><img src="data:image/gif;base64,{gif_base64}" alt="Campo magnetico no tempo"></div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Imagem da simulacao nao encontrada em imagens/AnaliseDinamica.gif.")

with col_modelo:
    st.markdown('<div class="section-title" style="text-align:center;">Esboço 3D do limitador</div>', unsafe_allow_html=True)
    st.plotly_chart(
        criar_figura_limitador_3d(),
        use_container_width=True,
        config={"scrollZoom": True, "displaylogo": False},
    )

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
