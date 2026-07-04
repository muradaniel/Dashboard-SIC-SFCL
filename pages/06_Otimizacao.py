from pathlib import Path

import colorsys
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


st.set_page_config(
    page_title="Análise de Otimização",
    layout="wide"
)

st.title("Análise de Otimização")
st.caption("Relação entre queda de tensão e corrente de curto-circuito")


BASE_DIR = Path(__file__).resolve().parents[1]
PASTA_DADOS = BASE_DIR / "Dataset" / "optimization"

COLUNA_TEMPO = "Time (s)"
COLUNA_CORRENTE = "Corrente de Curto (A)"
COLUNA_TENSAO = "Queda de Tensao (V)"
COLUNA_CHAVE = "Chave"
COLUNAS_PARAMETROS = ["H (cm)", "W (cm)", "N_DC", "N_AC"]

REGIAO_ANALISE_TEMPO_TENSAO = (0.01, 0.03)
REGIAO_ANALISE_TEMPO_CORRENTE = (0.0437, 0.0525)


def hex_para_rgb(cor):
    cor = cor.lstrip("#")
    return tuple(int(cor[indice:indice + 2], 16) for indice in (0, 2, 4))


def rgb_para_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def misturar_cores(cores):
    if len(cores) == 1:
        return cores[0]

    hsvs = []
    for cor in cores:
        r, g, b = hex_para_rgb(cor)
        hsvs.append(colorsys.rgb_to_hsv(r / 255, g / 255, b / 255))

    matizes = [h * 360 for h, _, _ in hsvs]
    if len(matizes) == 2:
        diferenca = abs(matizes[0] - matizes[1])
        if diferenca > 180:
            matiz = ((matizes[0] + matizes[1] + 360) / 2) % 360
        else:
            matiz = (matizes[0] + matizes[1]) / 2
    else:
        seno = sum(np.sin(np.deg2rad(matiz)) for matiz in matizes)
        cosseno = sum(np.cos(np.deg2rad(matiz)) for matiz in matizes)
        matiz = np.rad2deg(np.arctan2(seno, cosseno)) % 360

    saturacao = min(1.0, sum(s for _, s, _ in hsvs) / len(hsvs) + 0.08)
    valor = sum(v for _, _, v in hsvs) / len(hsvs)
    r, g, b = colorsys.hsv_to_rgb(matiz / 360, saturacao, valor)
    return rgb_para_hex((round(r * 255), round(g * 255), round(b * 255)))


def formatar_valor_destaque(valor):
    try:
        return f"{float(valor):g}"
    except (TypeError, ValueError):
        return str(valor)

@st.cache_data(show_spinner="Carregando dados de otimização...")
def carregar_dados(caminhos, datas_modificacao):
    nomes_colunas = [
        "H (cm)",
        "W (cm)",
        "N_DC",
        "N_AC",
        COLUNA_TEMPO,
        COLUNA_CORRENTE,
        COLUNA_TENSAO,
    ]
    quadros = []

    for caminho in caminhos:
        quadro = pd.read_csv(
            caminho,
            sep=r"\s{2,}",
            engine="python",
            comment="%",
            header=None,
            names=nomes_colunas,
        )
        quadros.append(quadro)

    dados = pd.concat(quadros, ignore_index=True)
    dados[COLUNA_CHAVE] = (
        dados["H (cm)"].map(lambda valor: f"{valor:g}")
        + " "
        + dados["W (cm)"].map(
            lambda valor: f"{valor:g}".replace(".", ",")
        )
        + " "
        + dados["N_DC"].map(lambda valor: f"{valor:g}")
        + " "
        + dados["N_AC"].map(lambda valor: f"{valor:g}")
    )

    return dados
def preparar_dados(dados):
    colunas_obrigatorias = {
        COLUNA_TEMPO,
        COLUNA_CORRENTE,
        COLUNA_TENSAO,
        COLUNA_CHAVE,
        *COLUNAS_PARAMETROS,
    }

    colunas_ausentes = colunas_obrigatorias.difference(dados.columns)
    if colunas_ausentes:
        nomes = ", ".join(sorted(colunas_ausentes))
        raise ValueError(f"Colunas ausentes no arquivo: {nomes}")

    dados = dados[list(colunas_obrigatorias)].copy()

    colunas_numericas = [
        COLUNA_TEMPO,
        COLUNA_CORRENTE,
        COLUNA_TENSAO,
        *COLUNAS_PARAMETROS,
    ]

    for coluna in colunas_numericas:
        dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce")

    dados[COLUNA_CHAVE] = dados[COLUNA_CHAVE].astype("string").str.strip()
    dados = dados.dropna(subset=[COLUNA_CHAVE, *colunas_numericas])

    dados_tensao = dados[
        dados[COLUNA_TEMPO].between(*REGIAO_ANALISE_TEMPO_TENSAO)
    ]
    dados_corrente = dados[
        dados[COLUNA_TEMPO].between(*REGIAO_ANALISE_TEMPO_CORRENTE)
    ]

    maximos_tensao = (
        dados_tensao
        .groupby(COLUNA_CHAVE, as_index=False)
        .agg({
            COLUNA_TENSAO: "max",
            "H (cm)": "first",
            "W (cm)": "first",
            "N_DC": "first",
            "N_AC": "first",
        })
    )

    maximos_corrente = (
        dados_corrente
        .groupby(COLUNA_CHAVE, as_index=False)[COLUNA_CORRENTE]
        .max()
    )

    dados_consolidados = pd.merge(
        maximos_tensao,
        maximos_corrente,
        on=COLUNA_CHAVE,
        how="inner"
    )

    return dados_consolidados[
        dados_consolidados[COLUNA_TENSAO] >= 0
    ].copy()


if not PASTA_DADOS.exists():
    st.error(f"Pasta de dados não encontrada: {PASTA_DADOS}")
    st.stop()

arquivos_txt = tuple(sorted(PASTA_DADOS.glob("*.txt")))

if not arquivos_txt:
    st.error(f"Nenhum arquivo TXT encontrado em: {PASTA_DADOS}")
    st.stop()

nomes_arquivos = [arquivo.name for arquivo in arquivos_txt]
arquivos_por_nome = dict(zip(nomes_arquivos, arquivos_txt))

if "arquivos_lidos" not in st.session_state:
    st.session_state.arquivos_lidos = nomes_arquivos

nomes_arquivos_selecionados = [
    nome for nome in st.session_state.arquivos_lidos
    if nome in arquivos_por_nome
]

if not nomes_arquivos_selecionados:
    st.session_state.arquivos_lidos = nomes_arquivos
    nomes_arquivos_selecionados = nomes_arquivos

arquivos_selecionados = tuple(
    arquivos_por_nome[nome] for nome in nomes_arquivos_selecionados
)

try:
    dados_brutos = carregar_dados(
        arquivos_selecionados,
        tuple(arquivo.stat().st_mtime_ns for arquivo in arquivos_selecionados),
    )
    dados_analise = preparar_dados(dados_brutos)
except Exception as erro:
    st.error(f"Não foi possível processar o arquivo: {erro}")
    st.stop()

if dados_analise.empty:
    st.warning("Nenhum dado foi encontrado nas regiões de tempo configuradas.")
    st.stop()


with st.sidebar:
    st.header("Filtros")
    st.subheader("Resultados")
    minimo_tensao_filtro = float(dados_analise[COLUNA_TENSAO].min())
    maximo_tensao_filtro = float(dados_analise[COLUNA_TENSAO].max())
    minimo_corrente_filtro = float(dados_analise[COLUNA_CORRENTE].min())
    maximo_corrente_filtro = float(dados_analise[COLUNA_CORRENTE].max())

    filtro_tensao = st.slider(
        "Queda de tensão (V)",
        min_value=round(minimo_tensao_filtro, 1),
        max_value=round(maximo_tensao_filtro, 1),
        value=(
            round(minimo_tensao_filtro, 1),
            round(maximo_tensao_filtro, 1),
        ),
        step=0.1,
    )
    filtro_corrente = st.slider(
        "Corrente de curto (A)",
        min_value=round(minimo_corrente_filtro, 1),
        max_value=round(maximo_corrente_filtro, 1),
        value=(
            round(minimo_corrente_filtro, 1),
            round(maximo_corrente_filtro, 1),
        ),
        step=0.1,
    )

    st.divider()
    st.subheader("Parâmetros")

    valores_h = sorted(dados_analise["H (cm)"].unique())
    valores_w = sorted(dados_analise["W (cm)"].unique())
    valores_n_dc = sorted(dados_analise["N_DC"].unique())
    valores_n_ac = sorted(dados_analise["N_AC"].unique())

    filtro_h = st.multiselect("H (cm)", valores_h, default=valores_h)
    filtro_w = st.multiselect("W (cm)", valores_w, default=valores_w)
    filtro_n_dc = st.multiselect("N_DC", valores_n_dc, default=valores_n_dc)
    filtro_n_ac = st.multiselect("N_AC", valores_n_ac, default=valores_n_ac)

    st.divider()
    st.subheader("Destaques")
    destacar_valor = st.checkbox("Destacar valores específicos", value=False)
    rotulos_parametros = {
        "H (cm)": "Altura H",
        "W (cm)": "Largura W",
        "N_DC": "Espiras DC",
        "N_AC": "Espiras AC",
    }
    cores_padrao_destaque = [
        "#16A34A",
        "#FACC15",
        "#2563EB",
        "#DC2626",
        "#9333EA",
        "#F97316",
    ]
    if "quantidade_destaques" not in st.session_state:
        st.session_state.quantidade_destaques = 1

    coluna_adicionar, coluna_remover = st.columns(2)
    if coluna_adicionar.button("+ Adicionar", key="adicionar_destaque", use_container_width=True):
        st.session_state.quantidade_destaques += 1
    if coluna_remover.button("- Remover", key="remover_destaque", use_container_width=True):
        st.session_state.quantidade_destaques = max(
            1,
            st.session_state.quantidade_destaques - 1,
        )

    destaques = []
    for indice_destaque in range(st.session_state.quantidade_destaques):
        with st.expander(f"Destaque {indice_destaque + 1}", expanded=True):
            parametro_destaque = st.selectbox(
                "Parâmetro",
                COLUNAS_PARAMETROS,
                index=COLUNAS_PARAMETROS.index("N_DC"),
                format_func=lambda coluna: rotulos_parametros.get(coluna, coluna),
                key=f"parametro_destaque_{indice_destaque}",
            )
            valores_destaque = sorted(
                dados_analise[parametro_destaque].dropna().unique()
            )
            indice_valor_destaque = 0
            for indice_valor, valor in enumerate(valores_destaque):
                if np.isclose(float(valor), 300.0):
                    indice_valor_destaque = indice_valor
                    break
            valor_destaque = st.selectbox(
                "Valor",
                valores_destaque,
                index=indice_valor_destaque,
                format_func=formatar_valor_destaque,
                key=f"valor_destaque_{indice_destaque}",
            )
            cor_destaque = st.color_picker(
                "Cor",
                cores_padrao_destaque[
                    indice_destaque % len(cores_padrao_destaque)
                ],
                key=f"cor_destaque_{indice_destaque}",
            )
            destaques.append({
                "parametro": parametro_destaque,
                "valor": valor_destaque,
                "cor": cor_destaque,
            })

    st.divider()
    st.subheader("Região ideal")
    limite_tensao_ideal = st.number_input(
        "Queda de tensão máxima (V)",
        min_value=0.0,
        value=17.96,
        step=0.1,
    )
    limite_corrente_ideal = st.number_input(
        "Corrente de curto máxima (A)",
        min_value=0.0,
        value=14.2,
        step=0.1,
    )

    st.divider()
    st.subheader("Curva de aproximação")
    mostrar_curva_aproximada = st.checkbox(
        "Mostrar curva aproximada",
        value=True,
    )
    grau_polinomio = st.number_input(
        "Grau do polinômio",
        min_value=1,
        max_value=10,
        value=10,
        step=1,
    )

    st.divider()
    st.caption(
        f"Queda de tensão: {REGIAO_ANALISE_TEMPO_TENSAO[0]:.4f} a "
        f"{REGIAO_ANALISE_TEMPO_TENSAO[1]:.4f} s"
    )
    st.caption(
        f"Corrente de curto: {REGIAO_ANALISE_TEMPO_CORRENTE[0]:.4f} a "
        f"{REGIAO_ANALISE_TEMPO_CORRENTE[1]:.4f} s"
    )

    st.divider()
    st.subheader("Arquivos de dados")
    nomes_arquivos_selecionados = st.multiselect(
        "Arquivos lidos",
        nomes_arquivos,
        key="arquivos_lidos",
    )
    st.caption(
        f"{len(nomes_arquivos_selecionados)} de {len(nomes_arquivos)} "
        "arquivo(s) selecionado(s)."
    )


dados_filtrados = dados_analise[
    dados_analise["H (cm)"].isin(filtro_h)
    & dados_analise["W (cm)"].isin(filtro_w)
    & dados_analise["N_DC"].isin(filtro_n_dc)
    & dados_analise["N_AC"].isin(filtro_n_ac)
    & dados_analise[COLUNA_TENSAO].between(*filtro_tensao)
    & dados_analise[COLUNA_CORRENTE].between(*filtro_corrente)
].copy()

if dados_filtrados.empty:
    st.warning("Nenhuma combinação atende aos filtros selecionados.")
    st.stop()


cor_base_pontos = "#0B4DDB"
cores_pontos = [cor_base_pontos] * len(dados_filtrados)
if destacar_valor:
    cores_por_ponto = [[] for _ in range(len(dados_filtrados))]
    for destaque in destaques:
        mascara_destaque = np.isclose(
            dados_filtrados[destaque["parametro"]].astype(float),
            float(destaque["valor"]),
        )
        for indice_ponto, ponto_destacado in enumerate(mascara_destaque):
            if ponto_destacado:
                cores_por_ponto[indice_ponto].append(destaque["cor"])

    cores_pontos = [
        misturar_cores(cores) if cores else cor_base_pontos
        for cores in cores_por_ponto
    ]


col1, col2, col3 = st.columns(3)

col1.metric("Combinações", len(dados_filtrados))
combinacoes_ideais = dados_filtrados[
    (dados_filtrados[COLUNA_TENSAO] <= limite_tensao_ideal)
    & (dados_filtrados[COLUNA_CORRENTE] <= limite_corrente_ideal)
]

escala_tensao = max(limite_tensao_ideal, 1.0)
escala_corrente = max(limite_corrente_ideal, 1.0)

queda_mais_proxima_na_regiao = np.clip(
    dados_filtrados[COLUNA_TENSAO],
    0,
    limite_tensao_ideal,
)
corrente_mais_proxima_na_regiao = np.clip(
    dados_filtrados[COLUNA_CORRENTE],
    0,
    limite_corrente_ideal,
)

distancia_regiao_ideal = np.hypot(
    (
        dados_filtrados[COLUNA_TENSAO]
        - queda_mais_proxima_na_regiao
    ) / escala_tensao,
    (
        dados_filtrados[COLUNA_CORRENTE]
        - corrente_mais_proxima_na_regiao
    ) / escala_corrente,
)
dados_filtrados["Distância até a região ideal"] = distancia_regiao_ideal

indices_ranking = dados_filtrados.sort_values(
    [
        "Distância até a região ideal",
        COLUNA_CORRENTE,
        COLUNA_TENSAO,
    ]
).index
dados_filtrados.loc[indices_ranking, "Posição no ranking"] = np.arange(
    1,
    len(indices_ranking) + 1,
)
dados_filtrados["Posição no ranking"] = (
    dados_filtrados["Posição no ranking"].astype(int)
)

indice_mais_proximo = distancia_regiao_ideal.idxmin()
combinacao_mais_proxima = dados_filtrados.loc[indice_mais_proximo]

col2.metric("Combinações na região ideal", len(combinacoes_ideais))
col3.metric(
    "Combinação mais próxima da região ideal",
    str(combinacao_mais_proxima[COLUNA_CHAVE]),
    delta=(
        f"Curto: {combinacao_mais_proxima[COLUNA_CORRENTE]:.2f} A | "
        f"Queda: {combinacao_mais_proxima[COLUNA_TENSAO]:.2f} V"
    ),
    delta_color="off",
)


fig = go.Figure()

fig.add_shape(
    type="rect",
    x0=0,
    x1=limite_tensao_ideal,
    y0=0,
    y1=limite_corrente_ideal,
    fillcolor="rgba(255, 80, 80, 0.45)",
    line=dict(width=0),
    layer="below",
    name="Região ideal",
    showlegend=True,
)

fig.add_trace(
    go.Scatter(
        x=dados_filtrados[COLUNA_TENSAO],
        y=dados_filtrados[COLUNA_CORRENTE],
        mode="markers",
        name="Simulado",
        customdata=dados_filtrados[
            [
                COLUNA_CHAVE,
                "H (cm)",
                "W (cm)",
                "N_DC",
                "N_AC",
                "Distância até a região ideal",
                "Posição no ranking",
            ]
        ],
        marker=dict(
            size=13,
            color=cores_pontos,
            line=dict(color="rgba(255,255,255,0.7)", width=0.6),
            opacity=0.78,
        ),
        hovertemplate=(
            "Chave: %{customdata[0]}<br>"
            "H: %{customdata[1]:.0f} cm<br>"
            "W: %{customdata[2]:.2f} cm<br>"
            "N_DC: %{customdata[3]:.0f}<br>"
            "N_AC: %{customdata[4]:.0f}<br>"
            "Posição no ranking: %{customdata[6]:.0f}º<br>"
            "Queda de tensão: %{x:.2f} V<br>"
            "Corrente de curto: %{y:.2f} A<br>"
            "Distância até a região ideal: %{customdata[5]:.4f}"
            "<extra></extra>"
        ),
    )
)

if mostrar_curva_aproximada:
    x_tendencia = dados_analise[COLUNA_TENSAO].to_numpy()
    y_tendencia = dados_analise[COLUNA_CORRENTE].to_numpy()
    ordem = np.argsort(x_tendencia)
    x_ordenado = x_tendencia[ordem]
    y_ordenado = y_tendencia[ordem]

if mostrar_curva_aproximada and len(x_ordenado) >= 3:
    grau_aplicado = min(
        int(grau_polinomio),
        len(np.unique(x_ordenado)) - 1,
    )
    polinomio = np.poly1d(
        np.polyfit(x_ordenado, y_ordenado, grau_aplicado)
    )
    x_curva = np.linspace(x_ordenado.min(), x_ordenado.max(), 300)
    y_curva = polinomio(x_curva)

    fig.add_trace(
        go.Scatter(
            x=x_curva,
            y=y_curva,
            mode="lines",
            name="Tendência",
            showlegend=False,
            line=dict(color="#003CFF", width=4, dash="dot"),
            hoverinfo="skip",
        )
    )

    if grau_aplicado != grau_polinomio:
        st.info(
            f"O grau foi limitado a {grau_aplicado} devido à quantidade "
            "de valores distintos no eixo X."
        )

minimo_x_global = min(0.0, float(dados_analise[COLUNA_TENSAO].min()))
maximo_x_global = max(
    float(dados_analise[COLUNA_TENSAO].max()),
    limite_tensao_ideal,
)
minimo_y_global = min(0.0, float(dados_analise[COLUNA_CORRENTE].min()))
maximo_y_global = max(
    float(dados_analise[COLUNA_CORRENTE].max()),
    limite_corrente_ideal,
)
amplitude_x_global = max(maximo_x_global - minimo_x_global, 1.0)
amplitude_y_global = max(maximo_y_global - minimo_y_global, 1.0)
range_x_global = [
    minimo_x_global,
    maximo_x_global + amplitude_x_global * 0.08,
]
range_y_global = [
    minimo_y_global,
    maximo_y_global + amplitude_y_global * 0.12,
]
fig.update_layout(
    title=dict(
        text="Análise de Viabilidade",
        x=0.5,
        xanchor="center",
        font=dict(size=34, color="black"),
    ),
    xaxis=dict(
        title="Queda de Tensão (V)",
        range=range_x_global,
        fixedrange=False,
        dtick=5,
        showgrid=True,
        gridcolor="rgba(0,0,0,0.12)",
        zeroline=True,
        zerolinecolor="rgba(0,0,0,0.35)",
    ),
    yaxis=dict(
        title="Curto Circuito (A)",
        range=range_y_global,
        fixedrange=False,
        dtick=5,
        showgrid=True,
        gridcolor="rgba(0,0,0,0.12)",
        zeroline=True,
        zerolinecolor="rgba(0,0,0,0.35)",
    ),
    template="plotly_white",
    height=760,
    hovermode="closest",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.01,
        xanchor="center",
        x=0.5,
        font=dict(size=20),
        itemsizing="constant",
    ),
    margin=dict(t=120, r=40, b=70, l=80),
)

st.plotly_chart(fig, use_container_width=True)


ranking_proximidade = dados_filtrados[
    [
        COLUNA_CHAVE,
        "H (cm)",
        "W (cm)",
        "N_DC",
        "N_AC",
        COLUNA_TENSAO,
        COLUNA_CORRENTE,
        "Distância até a região ideal",
    ]
].sort_values(
    [
        "Distância até a região ideal",
        COLUNA_CORRENTE,
        COLUNA_TENSAO,
    ]
).reset_index(drop=True)

ranking_proximidade.insert(
    0,
    "Posição",
    np.arange(1, len(ranking_proximidade) + 1),
)
ranking_proximidade["Situação"] = np.where(
    ranking_proximidade["Distância até a região ideal"] == 0,
    "Dentro da região ideal",
    "Fora da região ideal",
)

mostrar_tabela = st.checkbox("Mostrar ranking por proximidade")

if mostrar_tabela:
    st.subheader("Ranking de proximidade com a região ideal")
    st.dataframe(
        ranking_proximidade.style.format({
            "H (cm)": "{:.0f}",
            "W (cm)": "{:.2f}",
            "N_DC": "{:.0f}",
            "N_AC": "{:.0f}",
            COLUNA_TENSAO: "{:.2f}",
            COLUNA_CORRENTE: "{:.2f}",
            "Distância até a região ideal": "{:.4f}",
        }),
        use_container_width=True,
        hide_index=True,
    )
mostrar_small_multiples = st.checkbox("Mostrar small multiples", value=False)

if mostrar_small_multiples:
    st.subheader("Small multiples por parâmetro")

    rotulos_parametros = {
        "H (cm)": "H",
        "W (cm)": "W",
        "N_DC": "N_DC",
        "N_AC": "N_AC",
    }
    colunas_small_multiples = st.columns(2)
    parametro_separacao = colunas_small_multiples[0].selectbox(
        "Separar gráficos por",
        COLUNAS_PARAMETROS,
        index=COLUNAS_PARAMETROS.index("N_DC"),
        format_func=lambda coluna: rotulos_parametros.get(coluna, coluna),
        key="parametro_separacao_small_multiples",
    )
    parametros_cor = [
        coluna for coluna in COLUNAS_PARAMETROS
        if coluna != parametro_separacao
    ]
    parametro_cor_small = colunas_small_multiples[1].selectbox(
        "Colorir pontos por",
        parametros_cor,
        index=0,
        format_func=lambda coluna: rotulos_parametros.get(coluna, coluna),
        key="parametro_cor_small_multiples",
    )

    valores_separacao = sorted(dados_filtrados[parametro_separacao].unique())
    cols_por_linha = 2
    for inicio in range(0, len(valores_separacao), cols_por_linha):
        colunas_graficos = st.columns(cols_por_linha)
        for deslocamento, valor in enumerate(
            valores_separacao[inicio:inicio + cols_por_linha]
        ):
            dados_painel = dados_filtrados[
                dados_filtrados[parametro_separacao] == valor
            ]
            figura_small = go.Figure()
            figura_small.add_shape(
                type="rect",
                x0=0,
                x1=limite_tensao_ideal,
                y0=0,
                y1=limite_corrente_ideal,
                fillcolor="rgba(255, 80, 80, 0.30)",
                line=dict(width=0),
                layer="below",
            )
            figura_small.add_trace(
                go.Scatter(
                    x=dados_painel[COLUNA_TENSAO],
                    y=dados_painel[COLUNA_CORRENTE],
                    mode="markers",
                    name="Simulado",
                    customdata=dados_painel[
                        [
                            COLUNA_CHAVE,
                            "H (cm)",
                            "W (cm)",
                            "N_DC",
                            "N_AC",
                            "Distância até a região ideal",
                        ]
                    ],
                    marker=dict(
                        size=10,
                        color=dados_painel[parametro_cor_small],
                        colorscale="Turbo",
                        showscale=True,
                        colorbar=dict(
                            title=rotulos_parametros[parametro_cor_small],
                            thickness=12,
                        ),
                        opacity=0.78,
                        line=dict(
                            color="rgba(255,255,255,0.75)",
                            width=0.6,
                        ),
                    ),
                    hovertemplate=(
                        "Chave: %{customdata[0]}<br>"
                        "H: %{customdata[1]:.0f} cm<br>"
                        "W: %{customdata[2]:.2f} cm<br>"
                        "N_DC: %{customdata[3]:.0f}<br>"
                        "N_AC: %{customdata[4]:.0f}<br>"
                        "Queda: %{x:.2f} V<br>"
                        "Corrente: %{y:.2f} A<br>"
                        "Distância: %{customdata[5]:.4f}"
                        "<extra></extra>"
                    ),
                )
            )
            figura_small.update_layout(
                title=(
                    f"{rotulos_parametros[parametro_separacao]} = "
                    f"{formatar_valor_destaque(valor)}"
                ),
                template="plotly_white",
                height=430,
                margin=dict(t=60, r=35, b=55, l=65),
                xaxis=dict(
                    title="Queda de tensão (V)",
                    range=range_x_global,
                    dtick=5,
                    gridcolor="rgba(0,0,0,0.12)",
                    zeroline=True,
                    zerolinecolor="rgba(0,0,0,0.35)",
                ),
                yaxis=dict(
                    title="Corrente de curto (A)",
                    range=range_y_global,
                    dtick=5,
                    gridcolor="rgba(0,0,0,0.12)",
                    zeroline=True,
                    zerolinecolor="rgba(0,0,0,0.35)",
                ),
                showlegend=False,
            )
            colunas_graficos[deslocamento].plotly_chart(
                figura_small,
                use_container_width=True,
            )
st.divider()
mostrar_sensibilidade_modelo = st.checkbox(
    "Mostrar nova analise de sensibilidade por modelo",
    value=False,
)

if mostrar_sensibilidade_modelo:
    st.subheader("Analise de sensibilidade por modelo")
    st.caption(
        "O modelo Ridge e treinado com todas as simulacoes carregadas. "
        "A tabela por simulacao abaixo respeita os filtros atuais do dashboard."
    )

    dados_modelo = dados_analise[
        [*COLUNAS_PARAMETROS, COLUNA_CORRENTE, COLUNA_TENSAO, COLUNA_CHAVE]
    ].dropna().copy()

    if len(dados_modelo) < 8:
        st.warning(
            "A analise precisa de pelo menos 8 simulacoes validas para treinar "
            "um modelo com sensibilidade minimamente util."
        )
    else:
        X_modelo = dados_modelo[COLUNAS_PARAMETROS].astype(float)
        y_corrente = dados_modelo[COLUNA_CORRENTE].astype(float)
        y_tensao = dados_modelo[COLUNA_TENSAO].astype(float)

        def treinar_modelo_alvo(X, y):
            modelo_final = make_pipeline(
                StandardScaler(),
                Ridge(alpha=1.0),
            )
            modelo_final.fit(X, y)

            if len(X) >= 20:
                X_treino, X_teste, y_treino, y_teste = train_test_split(
                    X,
                    y,
                    test_size=0.25,
                    random_state=42,
                )
                modelo_validacao = make_pipeline(
                    StandardScaler(),
                    Ridge(alpha=1.0),
                )
                modelo_validacao.fit(X_treino, y_treino)
                r2 = r2_score(y_teste, modelo_validacao.predict(X_teste))
                tipo_r2 = "R2 validacao"
            else:
                r2 = r2_score(y, modelo_final.predict(X))
                tipo_r2 = "R2 treino"

            coeficientes = modelo_final.named_steps["ridge"].coef_
            valores_importancia = np.abs(coeficientes)
            soma_importancia = valores_importancia.sum()
            if soma_importancia > 0:
                importancia_percentual = valores_importancia / soma_importancia * 100
            else:
                importancia_percentual = np.zeros_like(valores_importancia)

            return modelo_final, r2, tipo_r2, coeficientes, importancia_percentual

        modelo_corrente, r2_corrente, tipo_r2_corrente, coef_corrente, imp_corrente = treinar_modelo_alvo(
            X_modelo,
            y_corrente,
        )
        modelo_tensao, r2_tensao, tipo_r2_tensao, coef_tensao, imp_tensao = treinar_modelo_alvo(
            X_modelo,
            y_tensao,
        )

        sensibilidade_global = pd.DataFrame({
            "Parametro": COLUNAS_PARAMETROS,
            "Influencia na corrente [%]": imp_corrente,
            "Influencia na queda [%]": imp_tensao,
            "Coeficiente corrente [A/std]": coef_corrente,
            "Coeficiente queda [V/std]": coef_tensao,
        })
        sensibilidade_global["Influencia media [%]"] = (
            sensibilidade_global["Influencia na corrente [%]"]
            + sensibilidade_global["Influencia na queda [%]"]
        ) / 2
        sensibilidade_global = sensibilidade_global.sort_values(
            "Influencia media [%]",
            ascending=False,
        )

        parametro_corrente = sensibilidade_global.sort_values(
            "Influencia na corrente [%]",
            ascending=False,
        ).iloc[0]
        parametro_tensao = sensibilidade_global.sort_values(
            "Influencia na queda [%]",
            ascending=False,
        ).iloc[0]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Simulacoes no treino", len(dados_modelo))
        c2.metric(tipo_r2_corrente, f"{r2_corrente:.3f}")
        c3.metric(tipo_r2_tensao, f"{r2_tensao:.3f}")
        c4.metric(
            "Parametro mais influente",
            str(sensibilidade_global.iloc[0]["Parametro"]),
        )

        c5, c6 = st.columns(2)
        c5.metric(
            "Mais influencia a corrente",
            str(parametro_corrente["Parametro"]),
            f"{parametro_corrente['Influencia na corrente [%]']:.1f}%",
            delta_color="off",
        )
        c6.metric(
            "Mais influencia a queda",
            str(parametro_tensao["Parametro"]),
            f"{parametro_tensao['Influencia na queda [%]']:.1f}%",
            delta_color="off",
        )

        fig_sensibilidade = go.Figure()
        fig_sensibilidade.add_trace(
            go.Bar(
                y=sensibilidade_global["Parametro"],
                x=sensibilidade_global["Influencia na corrente [%]"],
                name="Corrente de curto",
                orientation="h",
                marker_color="#0B4DDB",
            )
        )
        fig_sensibilidade.add_trace(
            go.Bar(
                y=sensibilidade_global["Parametro"],
                x=sensibilidade_global["Influencia na queda [%]"],
                name="Queda de tensao",
                orientation="h",
                marker_color="#DC2626",
            )
        )
        fig_sensibilidade.update_layout(
            title="Sensibilidade geral dos parametros",
            xaxis_title="Influencia relativa dos coeficientes [%]",
            yaxis_title="Parametro",
            barmode="group",
            template="plotly_white",
            height=430,
            legend=dict(orientation="h", y=1.08),
            margin=dict(t=80, r=30, b=55, l=90),
        )
        fig_sensibilidade.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.10)")
        fig_sensibilidade.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_sensibilidade, use_container_width=True)

        st.subheader("Tabela de sensibilidade geral")
        st.dataframe(
            sensibilidade_global.round({
                "Influencia na corrente [%]": 2,
                "Influencia na queda [%]": 2,
                "Coeficiente corrente [A/std]": 4,
                "Coeficiente queda [V/std]": 4,
                "Influencia media [%]": 2,
            }),
            use_container_width=True,
            hide_index=True,
        )

        dados_casos = dados_filtrados[
            [COLUNA_CHAVE, *COLUNAS_PARAMETROS, COLUNA_CORRENTE, COLUNA_TENSAO]
        ].dropna().copy()
        X_casos = dados_casos[COLUNAS_PARAMETROS].astype(float)
        X_casos_padronizado = modelo_corrente.named_steps["standardscaler"].transform(X_casos)

        escala_corrente_sens = max(float(y_corrente.max() - y_corrente.min()), 1.0)
        escala_tensao_sens = max(float(y_tensao.max() - y_tensao.min()), 1.0)
        contrib_corrente = X_casos_padronizado * coef_corrente
        contrib_tensao = X_casos_padronizado * coef_tensao
        contrib_combinada = (
            np.abs(contrib_corrente) / escala_corrente_sens
            + np.abs(contrib_tensao) / escala_tensao_sens
        )

        linhas_casos = []
        for indice, (_, caso) in enumerate(dados_casos.iterrows()):
            ordem_impacto = np.argsort(contrib_combinada[indice])[::-1]
            indice_corrente = int(np.argmax(np.abs(contrib_corrente[indice])))
            indice_tensao = int(np.argmax(np.abs(contrib_tensao[indice])))
            indice_dominante = int(ordem_impacto[0])

            linhas_casos.append({
                "Chave": caso[COLUNA_CHAVE],
                "H (cm)": caso["H (cm)"],
                "W (cm)": caso["W (cm)"],
                "N_DC": caso["N_DC"],
                "N_AC": caso["N_AC"],
                "Corrente real [A]": caso[COLUNA_CORRENTE],
                "Queda real [V]": caso[COLUNA_TENSAO],
                "Variavel dominante": COLUNAS_PARAMETROS[indice_dominante],
                "Ranking de influencia": " > ".join(
                    COLUNAS_PARAMETROS[i] for i in ordem_impacto
                ),
                "Mais afeta corrente": COLUNAS_PARAMETROS[indice_corrente],
                "Contribuicao corrente [A]": contrib_corrente[indice, indice_corrente],
                "Mais afeta queda": COLUNAS_PARAMETROS[indice_tensao],
                "Contribuicao queda [V]": contrib_tensao[indice, indice_tensao],
                "Impacto combinado": contrib_combinada[indice, indice_dominante],
            })

        sensibilidade_casos = pd.DataFrame(linhas_casos).sort_values(
            "Impacto combinado",
            ascending=False,
        )

        st.subheader("Sensibilidade especifica por simulacao")
        sensibilidade_casos_exibicao = sensibilidade_casos.copy()
        sensibilidade_casos_exibicao["H (cm)"] = sensibilidade_casos_exibicao["H (cm)"].round(0)
        sensibilidade_casos_exibicao["W (cm)"] = sensibilidade_casos_exibicao["W (cm)"].round(2)
        sensibilidade_casos_exibicao["N_DC"] = sensibilidade_casos_exibicao["N_DC"].round(0)
        sensibilidade_casos_exibicao["N_AC"] = sensibilidade_casos_exibicao["N_AC"].round(0)
        sensibilidade_casos_exibicao["Corrente real [A]"] = sensibilidade_casos_exibicao["Corrente real [A]"].round(2)
        sensibilidade_casos_exibicao["Queda real [V]"] = sensibilidade_casos_exibicao["Queda real [V]"].round(2)
        sensibilidade_casos_exibicao["Contribuicao corrente [A]"] = sensibilidade_casos_exibicao["Contribuicao corrente [A]"].round(3)
        sensibilidade_casos_exibicao["Contribuicao queda [V]"] = sensibilidade_casos_exibicao["Contribuicao queda [V]"].round(3)
        sensibilidade_casos_exibicao["Impacto combinado"] = sensibilidade_casos_exibicao["Impacto combinado"].round(4)
        st.dataframe(
            sensibilidade_casos_exibicao,
            use_container_width=True,
            hide_index=True,
        )

        st.info(
            "Leitura da tabela: o modelo padroniza os parametros e estima a "
            "contribuicao de cada variavel para corrente e queda em cada simulacao. "
            "O ranking mostra quais parametros mais pesaram naquele caso filtrado."
        )
