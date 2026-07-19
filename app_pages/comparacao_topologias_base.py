from pathlib import Path

import numpy as np
import plotly.graph_objects as go

from app_pages.otimizacao_base import (
    COLUNA_CHAVE,
    COLUNA_CORRENTE,
    COLUNA_TENSAO,
    CORRENTE_MAXIMA_PICO,
    TENSAO_MAXIMA_PICO,
    carregar_dados,
    misturar_cores,
    preparar_dados,
)


def carregar_dados_da_pasta(pasta_dados):
    """Carrega automaticamente todos os TXT válidos de uma topologia."""
    pasta_dados = Path(pasta_dados)
    if not pasta_dados.is_dir():
        raise FileNotFoundError(f"Pasta de dados não encontrada: {pasta_dados}")

    arquivos_txt = tuple(
        arquivo
        for arquivo in sorted(pasta_dados.glob("*.txt"))
        if arquivo.stat().st_size > 0
    )
    if not arquivos_txt:
        raise FileNotFoundError(f"Nenhum arquivo TXT encontrado em: {pasta_dados}")

    dados_brutos = carregar_dados(
        tuple(str(arquivo) for arquivo in arquivos_txt),
        tuple(arquivo.stat().st_mtime_ns for arquivo in arquivos_txt),
        tuple(),
    )
    dados_analise = preparar_dados(dados_brutos)
    if dados_analise.empty:
        raise ValueError("Nenhum dado foi encontrado nas regiões de tempo configuradas.")

    return dados_analise


def calcular_escalas_compartilhadas(
    conjuntos_dados,
    limite_tensao_ideal=TENSAO_MAXIMA_PICO,
    limite_corrente_ideal=CORRENTE_MAXIMA_PICO,
):
    """Calcula os mesmos limites de eixos para um conjunto de topologias."""
    dados_disponiveis = [dados for dados in conjuntos_dados if not dados.empty]
    if not dados_disponiveis:
        return None, None

    minimo_x = min(
        0.0,
        min(float(dados[COLUNA_TENSAO].min()) for dados in dados_disponiveis),
    )
    maximo_x = max(
        limite_tensao_ideal,
        max(float(dados[COLUNA_TENSAO].max()) for dados in dados_disponiveis),
    )
    minimo_y = min(
        0.0,
        min(float(dados[COLUNA_CORRENTE].min()) for dados in dados_disponiveis),
    )
    maximo_y = max(
        limite_corrente_ideal,
        max(float(dados[COLUNA_CORRENTE].max()) for dados in dados_disponiveis),
    )

    amplitude_x = max(maximo_x - minimo_x, 1.0)
    amplitude_y = max(maximo_y - minimo_y, 1.0)
    return (
        [minimo_x, maximo_x + amplitude_x * 0.08],
        [minimo_y, maximo_y + amplitude_y * 0.12],
    )


def criar_grafico_comparacao(
    dados_analise,
    titulo,
    range_x,
    range_y,
    limite_tensao_ideal=TENSAO_MAXIMA_PICO,
    limite_corrente_ideal=CORRENTE_MAXIMA_PICO,
    mostrar_curva_aproximada=True,
    grau_polinomio=10,
    destacar_valor=False,
    destaques=(),
):
    """Monta o gráfico padronizado usado na comparação de topologias."""
    dados_plot = dados_analise.copy()
    escala_tensao = max(limite_tensao_ideal, 1.0)
    escala_corrente = max(limite_corrente_ideal, 1.0)
    tensao_na_regiao = np.clip(
        dados_plot[COLUNA_TENSAO], 0, limite_tensao_ideal
    )
    corrente_na_regiao = np.clip(
        dados_plot[COLUNA_CORRENTE], 0, limite_corrente_ideal
    )
    dados_plot["Distância até a região ideal"] = np.hypot(
        (dados_plot[COLUNA_TENSAO] - tensao_na_regiao) / escala_tensao,
        (dados_plot[COLUNA_CORRENTE] - corrente_na_regiao) / escala_corrente,
    )

    figura = go.Figure()
    figura.add_shape(
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
    cores_pontos = ["#0B4DDB"] * len(dados_plot)
    if destacar_valor:
        cores_por_ponto = [[] for _ in range(len(dados_plot))]
        for destaque in destaques:
            mascara = np.isclose(
                dados_plot[destaque["parametro"]].astype(float),
                float(destaque["valor"]),
            )
            for indice, ponto_destacado in enumerate(mascara):
                if ponto_destacado:
                    cores_por_ponto[indice].append(destaque["cor"])
        cores_pontos = [
            misturar_cores(cores) if cores else "#0B4DDB"
            for cores in cores_por_ponto
        ]
    figura.add_trace(
        go.Scatter(
            x=dados_plot[COLUNA_TENSAO],
            y=dados_plot[COLUNA_CORRENTE],
            mode="markers",
            name="Simulado",
            customdata=dados_plot[
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
                size=11,
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
                "Queda de tensão: %{x:.2f} V<br>"
                "Corrente de curto: %{y:.2f} A<br>"
                "Distância até a região ideal: %{customdata[5]:.4f}"
                "<extra></extra>"
            ),
        )
    )

    x_tendencia = dados_plot[COLUNA_TENSAO].to_numpy()
    y_tendencia = dados_plot[COLUNA_CORRENTE].to_numpy()
    valores_x_distintos = len(np.unique(x_tendencia))
    if (
        mostrar_curva_aproximada
        and len(x_tendencia) >= 3
        and valores_x_distintos >= 2
    ):
        ordem = np.argsort(x_tendencia)
        grau = min(int(grau_polinomio), valores_x_distintos - 1)
        polinomio = np.poly1d(
            np.polyfit(x_tendencia[ordem], y_tendencia[ordem], grau)
        )
        x_curva = np.linspace(x_tendencia.min(), x_tendencia.max(), 300)
        figura.add_trace(
            go.Scatter(
                x=x_curva,
                y=polinomio(x_curva),
                mode="lines",
                name="Tendência",
                showlegend=False,
                line=dict(color="#003CFF", width=3, dash="dot"),
                hoverinfo="skip",
            )
        )

    figura.update_layout(
        title=dict(text=titulo, x=0.5, xanchor="center", font=dict(size=24, color="black")),
        xaxis=dict(
            title="Queda de Tensão (V)", range=range_x, fixedrange=False, dtick=5,
            showgrid=True, gridcolor="rgba(0,0,0,0.12)", zeroline=True,
            zerolinecolor="rgba(0,0,0,0.35)",
        ),
        yaxis=dict(
            title="Curto Circuito (A)", range=range_y, fixedrange=False, dtick=5,
            showgrid=True, gridcolor="rgba(0,0,0,0.12)", zeroline=True,
            zerolinecolor="rgba(0,0,0,0.35)",
        ),
        template="plotly_white",
        height=560,
        hovermode="closest",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01, xanchor="center", x=0.5,
            itemsizing="constant",
        ),
        margin=dict(t=100, r=25, b=65, l=70),
    )
    return figura
