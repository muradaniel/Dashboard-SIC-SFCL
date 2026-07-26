from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app_pages.otimizacao_base import BASE_DIR, render_pagina_otimizacao

render_pagina_otimizacao(
    "Topologia A - 1 Núcleo & 1 Bobina DC & 1 Bobina AC",
    BASE_DIR / "Dataset" / "Topologia_A",
    "otimizacao_1_core_1_coil",
)
