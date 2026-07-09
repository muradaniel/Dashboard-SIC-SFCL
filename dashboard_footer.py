from datetime import datetime
from pathlib import Path
import subprocess

import streamlit as st


def obter_ultima_atualizacao():
    base_dir = Path(__file__).resolve().parent
    referencia_commit = "HEAD"

    try:
        upstream = subprocess.check_output(
            [
                "git",
                "-C",
                str(base_dir),
                "rev-parse",
                "--abbrev-ref",
                "--symbolic-full-name",
                "@{u}",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if upstream:
            referencia_commit = upstream
    except Exception:
        pass

    try:
        data_commit = subprocess.check_output(
            [
                "git",
                "-C",
                str(base_dir),
                "log",
                "-1",
                "--format=%cd",
                "--date=format:%d/%m/%Y %H:%M",
                referencia_commit,
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if data_commit:
            return data_commit
    except Exception:
        pass

    arquivos = [base_dir / "app.py", *sorted((base_dir / "app_pages").glob("*.py"))]
    datas = [arquivo.stat().st_mtime for arquivo in arquivos if arquivo.exists()]
    if not datas:
        return datetime.now().strftime("%d/%m/%Y %H:%M")
    return datetime.fromtimestamp(max(datas)).strftime("%d/%m/%Y %H:%M")


def mostrar_rodape():
    data = obter_ultima_atualizacao()
    st.markdown(
        f"""
        <style>
        .block-container {{
            padding-bottom: 4.5rem;
        }}
        .dashboard-footer {{
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 999;
            padding: 0.55rem 1.5rem;
            border-top: 1px solid rgba(15, 23, 42, 0.12);
            background: rgba(255, 255, 255, 0.94);
            color: #64748b;
            font-size: 0.82rem;
            text-align: center;
            backdrop-filter: blur(8px);
        }}
        </style>
        <div class="dashboard-footer">Ultimo commit do GitHub: {data}</div>
        """,
        unsafe_allow_html=True,
    )
