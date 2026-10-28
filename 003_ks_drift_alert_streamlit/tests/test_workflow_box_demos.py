"""Executa cada script de caixa do fluxo como processo isolado."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOX_DIR = ROOT / "scripts" / "workflow_boxes"

SCRIPTS = [
    "box_01_luminancia.py",
    "box_02_histograma.py",
    "box_03_cdf.py",
    "box_04_delta.py",
    "box_05_d_max.py",
    "box_06_alerta.py",
]


def test_each_workflow_box_script_exits_zero() -> None:
    for name in SCRIPTS:
        path = BOX_DIR / name
        assert path.is_file(), path
        proc = subprocess.run(
            [sys.executable, str(path)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, f"{name}: {proc.stdout}\n{proc.stderr}"


def test_box_pngs_exist() -> None:
    illus = ROOT / "illustrations"
    for name in [
        "box_01_l_pixel.png",
        "box_02_histograma_h.png",
        "box_03_cdf_f.png",
        "box_04_delta.png",
        "box_05_d_max.png",
        "box_06_alerta_d.png",
    ]:
        assert (illus / name).is_file(), f"gere com scripts/generate_illustrations.py: {name}"
