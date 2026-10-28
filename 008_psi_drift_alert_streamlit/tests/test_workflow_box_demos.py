"""Executa cada script de caixa do fluxo PSI como processo isolado."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOX_DIR = ROOT / "scripts" / "workflow_boxes"

SCRIPTS = [
    "box_01_massas.py",
    "box_02_termo_kl.py",
    "box_03_psi_soma.py",
    "box_04_faixa.py",
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
        "01_workflow_hist_to_psi.png",
        "box_01_massas.png",
        "box_02_termo_kl.png",
        "box_03_psi_soma.png",
        "box_04_faixa.png",
    ]:
        assert (illus / name).is_file(), (
            f"gere com scripts/generate_illustrations.py: {name}"
        )


def test_workflow_boxes_psi_wrappers() -> None:
    from workflow_boxes_psi import faixa_alerta_psi, massas_p, psi_soma, termo_kl

    assert massas_p([1, 1, 2]) == [0.25, 0.25, 0.5]
    assert abs(termo_kl(0.5, 0.5)) < 1e-12
    assert psi_soma([0.5, 0.5], [0.5, 0.5]) == 0.0
    assert faixa_alerta_psi(0.05, 50, 50) == "QUIET"
    assert faixa_alerta_psi(0.40, 50, 50) == "ALERT"
