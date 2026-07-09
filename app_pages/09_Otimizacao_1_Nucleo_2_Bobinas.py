from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app_pages.otimizacao_base import BASE_DIR, render_pagina_otimizacao

render_pagina_otimizacao(
    "Otimização - 1 Núcleo & 2 Bobinas",
    BASE_DIR / "Dataset" / "optimization_1_core_2_coil",
    "otimizacao_1_core_2_coil",
)
