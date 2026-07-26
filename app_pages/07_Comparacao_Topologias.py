from pathlib import Path
import sys

import numpy as np
import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app_pages.comparacao_topologias_base import (
    calcular_escalas_compartilhadas,
    carregar_dados_da_pasta,
    criar_grafico_comparacao,
)
from app_pages.otimizacao_base import (
    BASE_DIR,
    COLUNA_CORRENTE,
    COLUNA_TENSAO,
    COLUNAS_PARAMETROS,
    CORRENTE_MAXIMA_PICO,
    TENSAO_MAXIMA_PICO,
    filtro_intervalo_resultado,
    formatar_valor_destaque,
)
from dashboard_footer import mostrar_rodape


TOPOLOGIAS = (
    ("Topologia A", BASE_DIR / "Dataset" / "Topologia_A"),
    ("Topologia B", BASE_DIR / "Dataset" / "Topologia_B"),
    ("Topologia C", BASE_DIR / "Dataset" / "Topologia_C"),
    ("Topologia D", BASE_DIR / "Dataset" / "Topologia_D"),
)


mostrar_rodape()
st.title("Comparação entre Topologias")
st.caption("Relação entre queda de tensão e corrente de curto-circuito")

resultados_brutos = []
for nome, pasta_dados in TOPOLOGIAS:
    try:
        resultados_brutos.append(
            (nome, carregar_dados_da_pasta(pasta_dados), None)
        )
    except Exception as erro:
        resultados_brutos.append((nome, None, str(erro)))

dados_disponiveis = [
    dados for _, dados, _ in resultados_brutos if dados is not None
]

if dados_disponiveis:
    dados_conjuntos = pd.concat(dados_disponiveis, ignore_index=True)

    with st.sidebar:
        st.header("Filtros")
        st.subheader("Resultados")
        filtro_tensao = filtro_intervalo_resultado(
            "Queda de tensão (V)",
            float(dados_conjuntos[COLUNA_TENSAO].min()),
            float(dados_conjuntos[COLUNA_TENSAO].max()),
            "comparacao_filtro_tensao",
        )
        filtro_corrente = filtro_intervalo_resultado(
            "Corrente de curto (A)",
            float(dados_conjuntos[COLUNA_CORRENTE].min()),
            float(dados_conjuntos[COLUNA_CORRENTE].max()),
            "comparacao_filtro_corrente",
        )

        st.divider()
        st.subheader("Parâmetros")
        filtros_parametros = {}
        for parametro in COLUNAS_PARAMETROS:
            valores = sorted(dados_conjuntos[parametro].dropna().unique())
            filtros_parametros[parametro] = st.multiselect(
                parametro,
                valores,
                default=valores,
                key=f"comparacao_filtro_{parametro}",
            )

        st.divider()
        st.subheader("Destaque")
        destacar_valor = st.checkbox(
            "Destacar valores específicos",
            value=False,
            key="comparacao_destacar_valor",
        )
        rotulos_parametros = {
            "H (cm)": "Altura H",
            "W (cm)": "Largura W",
            "N_DC": "Espiras DC",
            "N_AC": "Espiras AC",
        }
        cores_padrao = [
            "#16A34A",
            "#FACC15",
            "#2563EB",
            "#DC2626",
            "#9333EA",
            "#F97316",
        ]
        estado_quantidade = "comparacao_quantidade_destaques"
        if estado_quantidade not in st.session_state:
            st.session_state[estado_quantidade] = 1

        coluna_adicionar, coluna_remover = st.columns(2)
        if coluna_adicionar.button(
            "+ Adicionar",
            key="comparacao_adicionar_destaque",
            width="stretch",
        ):
            st.session_state[estado_quantidade] += 1
        if coluna_remover.button(
            "- Remover",
            key="comparacao_remover_destaque",
            width="stretch",
        ):
            st.session_state[estado_quantidade] = max(
                1, st.session_state[estado_quantidade] - 1
            )

        destaques = []
        for indice in range(st.session_state[estado_quantidade]):
            with st.expander(f"Destaque {indice + 1}", expanded=False):
                parametro = st.selectbox(
                    "Parâmetro",
                    COLUNAS_PARAMETROS,
                    index=COLUNAS_PARAMETROS.index("N_DC"),
                    format_func=lambda coluna: rotulos_parametros.get(
                        coluna, coluna
                    ),
                    key=f"comparacao_parametro_destaque_{indice}",
                )
                valores = sorted(
                    dados_conjuntos[parametro].dropna().unique()
                )
                indice_padrao = next(
                    (
                        posicao
                        for posicao, valor in enumerate(valores)
                        if np.isclose(float(valor), 300.0)
                    ),
                    0,
                )
                valor = st.selectbox(
                    "Valor",
                    valores,
                    index=indice_padrao,
                    format_func=formatar_valor_destaque,
                    key=f"comparacao_valor_destaque_{indice}",
                )
                cor = st.color_picker(
                    "Cor",
                    cores_padrao[indice % len(cores_padrao)],
                    key=f"comparacao_cor_destaque_{indice}",
                )
                destaques.append(
                    {"parametro": parametro, "valor": valor, "cor": cor}
                )

        st.divider()
        st.subheader("Região Ideal")
        limite_tensao_ideal = st.number_input(
            "Queda de tensão máxima (V)",
            min_value=0.0,
            value=TENSAO_MAXIMA_PICO,
            step=0.1,
            key="comparacao_limite_tensao_ideal",
        )
        limite_corrente_ideal = st.number_input(
            "Corrente de curto máxima (A)",
            min_value=0.0,
            value=CORRENTE_MAXIMA_PICO,
            step=0.1,
            key="comparacao_limite_corrente_ideal",
        )

        st.divider()
        st.subheader("Curva de Aproximação")
        mostrar_curva_aproximada = st.checkbox(
            "Mostrar curva aproximada",
            value=True,
            key="comparacao_mostrar_curva",
        )
        grau_polinomio = st.number_input(
            "Grau do polinômio",
            min_value=1,
            max_value=10,
            value=10,
            step=1,
            key="comparacao_grau_polinomio",
        )
else:
    filtro_tensao = (0.0, 0.0)
    filtro_corrente = (0.0, 0.0)
    filtros_parametros = {parametro: [] for parametro in COLUNAS_PARAMETROS}
    destacar_valor = False
    destaques = []
    limite_tensao_ideal = TENSAO_MAXIMA_PICO
    limite_corrente_ideal = CORRENTE_MAXIMA_PICO
    mostrar_curva_aproximada = True
    grau_polinomio = 10

resultados = []
for nome, dados, erro in resultados_brutos:
    if dados is None:
        resultados.append((nome, None, erro))
        continue

    mascara = (
        dados[COLUNA_TENSAO].between(*filtro_tensao)
        & dados[COLUNA_CORRENTE].between(*filtro_corrente)
    )
    for parametro, valores in filtros_parametros.items():
        mascara &= dados[parametro].isin(valores)

    dados_filtrados = dados[mascara].copy()
    if dados_filtrados.empty:
        resultados.append(
            (nome, None, "Nenhuma combinação atende aos filtros selecionados.")
        )
    else:
        resultados.append((nome, dados_filtrados, None))

range_x, range_y = calcular_escalas_compartilhadas(
    dados_disponiveis,
    limite_tensao_ideal,
    limite_corrente_ideal,
)

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

for coluna, (nome, dados, erro) in zip((col1, col2, col3, col4), resultados):
    with coluna:
        if dados is None:
            st.subheader(nome)
            st.warning(erro)
        else:
            try:
                figura = criar_grafico_comparacao(
                    dados,
                    nome,
                    range_x,
                    range_y,
                    limite_tensao_ideal=limite_tensao_ideal,
                    limite_corrente_ideal=limite_corrente_ideal,
                    mostrar_curva_aproximada=mostrar_curva_aproximada,
                    grau_polinomio=grau_polinomio,
                    destacar_valor=destacar_valor,
                    destaques=destaques,
                )
                st.plotly_chart(figura, width="stretch")
            except Exception as erro_grafico:
                st.subheader(nome)
                st.warning(f"Não foi possível gerar o gráfico: {erro_grafico}")
