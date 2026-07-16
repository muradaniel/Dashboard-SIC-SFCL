import html

import pandas as pd
import streamlit as st


def mostrar_tabela_html(dados, formatos=None, altura=480, **_opcoes_ignoradas):
    """Renderiza uma tabela sem usar a serializacao nativa do PyArrow."""
    quadro = dados.copy()
    for coluna, formato in (formatos or {}).items():
        if coluna not in quadro.columns:
            continue

        def formatar(valor, padrao=formato):
            if pd.isna(valor):
                return ""
            try:
                return padrao.format(valor)
            except (TypeError, ValueError):
                return str(valor)

        quadro[coluna] = quadro[coluna].map(formatar)

    tabela = quadro.to_html(index=False, escape=True, border=0)
    altura_css = "none" if altura is None else f"{int(altura)}px"
    st.markdown(
        f"""
        <style>
        .tabela-segura {{
            max-height: {html.escape(altura_css)};
            overflow: auto;
            border: 1px solid rgba(15, 23, 42, 0.12);
            border-radius: 8px;
        }}
        .tabela-segura table {{ width: 100%; border-collapse: collapse; }}
        .tabela-segura th {{
            position: sticky; top: 0; z-index: 1;
            background: #f8fafc; color: #0f172a;
        }}
        .tabela-segura th, .tabela-segura td {{
            padding: 0.45rem 0.65rem;
            border-bottom: 1px solid rgba(15, 23, 42, 0.08);
            text-align: right; white-space: nowrap;
        }}
        .tabela-segura tbody tr:nth-child(even) {{ background: #f8fafc; }}
        </style>
        <div class="tabela-segura">{tabela}</div>
        """,
        unsafe_allow_html=True,
    )
