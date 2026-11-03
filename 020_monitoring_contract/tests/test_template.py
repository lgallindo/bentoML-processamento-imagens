"""Contrato textual da aula 020."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
TEMPLATE = (ROOT / "CONTRACT_TEMPLATE.md").read_text(encoding="utf-8")


def test_three_goals_in_template() -> None:
    assert "Saúde do servidor" in TEMPLATE
    assert "Drift de dados" in TEMPLATE
    assert "Detecção de anomalias" in TEMPLATE


def test_readme_points_to_008_and_000() -> None:
    assert "008_psi_drift_alert_streamlit" in README
    assert "000_mlops_pipelines_goals" in README
    assert "CONTRACT_TEMPLATE.md" in README
