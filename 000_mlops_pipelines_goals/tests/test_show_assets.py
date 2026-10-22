from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ILLUSTRATIONS = ROOT / "illustrations"
README = ROOT / "README.md"
MAX_BYTES = 2 * 1024 * 1024

PIPELINES = ILLUSTRATIONS / "pipelines-mlops.webp"
TARGET = ILLUSTRATIONS / "bentoml-prometheus-grafana.webp"

GOAL_LABELS = (
    "Saúde do servidor",
    "Drift de dados",
    "Detecção de anomalias",
)


def test_pipeline_figure_exists_and_under_budget() -> None:
    assert PIPELINES.is_file(), f"missing {PIPELINES}"
    assert PIPELINES.stat().st_size <= MAX_BYTES


def test_target_figure_exists_and_under_budget() -> None:
    assert TARGET.is_file(), f"missing {TARGET}"
    assert TARGET.stat().st_size <= MAX_BYTES


def test_readme_has_three_goals_and_target_path() -> None:
    text = README.read_text(encoding="utf-8")
    for label in GOAL_LABELS:
        assert label in text, f"missing goal label: {label}"
    assert "BentoML" in text and "Prometheus" in text and "Grafana" in text
    assert "gerida pelo BentoML" in text or "gerido pelo BentoML" in text


def test_no_streamlit_dependency() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "streamlit" not in pyproject.lower()
