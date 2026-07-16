from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app_pages.otimizacao_base import BASE_DIR, render_pagina_otimizacao

render_pagina_otimizacao(
    "Otimização - 2 Núcleos & 2 Bobinas DC & 2 Bobinas AC",
    BASE_DIR / "Dataset" / "2 Cores & 2 DC Coils & 2 AC Coils",
    "otimizacao_2_core_2_coil",
)