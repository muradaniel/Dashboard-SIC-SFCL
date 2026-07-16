from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app_pages.otimizacao_base import BASE_DIR, render_pagina_otimizacao

render_pagina_otimizacao(
    "Otimização - 1 Núcleo & 1 Bobinas DC & 2 Bobinas AC",
    BASE_DIR / "Dataset" / "1 Core & 1 DC Coil & 2 AC Coils",
    "otimizacao_1_core_2_coil",
)
