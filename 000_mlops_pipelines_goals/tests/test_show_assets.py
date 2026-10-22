from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ILLUSTRATIONS = ROOT / "illustrations"
README = ROOT / "README.md"
JUSTFILE = ROOT / "justfile"
MAX_BYTES = 2 * 1024 * 1024

PIPELINES = ILLUSTRATIONS / "pipelines-mlops.webp"
TARGET = ILLUSTRATIONS / "bentoml-prometheus-grafana.webp"
GOALS_MAP = ILLUSTRATIONS / "goals-lessons-map.webp"

GOAL_LABELS = (
    "Saúde do servidor",
    "Drift de dados",
    "Detecção de anomalias",
)

INDEX_FOLDERS = (
    "001_histogram_cdf_cli",
    "002_histogram_cdf_streamlit",
    "003_prometheus_histcdf_streamlit",
    "010_corpus_histograms_model",
    "020_grayscale_request_logging",
    "030_request_log_histograms",
    "040_ks_production_vs_corpus",
)

SHOW_BEATS = (
    "just open-diagram",
    "just open-target",
    "just open-goals-map",
)


def _load_builder():
    path = ROOT / "scripts" / "build_illustrations.py"
    spec = importlib.util.spec_from_file_location("build_illustrations", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["build_illustrations"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_three_figures_exist_and_under_budget() -> None:
    for path in (PIPELINES, TARGET, GOALS_MAP):
        assert path.is_file(), f"missing {path}"
        assert path.stat().st_size <= MAX_BYTES


def test_readme_goals_path_and_runtime_label() -> None:
    text = README.read_text(encoding="utf-8")
    for label in GOAL_LABELS:
        assert label in text, f"missing goal label: {label}"
    assert "BentoML" in text and "Prometheus" in text and "Grafana" in text
    assert "Runtime (BentoML)" in text
    assert "## Comparação com a base" not in text


def test_readme_mermaid_and_index() -> None:
    text = README.read_text(encoding="utf-8")
    assert "```mermaid" in text
    assert "Runtime (BentoML)" in text.split("```mermaid", 1)[1].split("```", 1)[0]
    for name in INDEX_FOLDERS:
        assert name in text, f"missing index folder: {name}"


def test_readme_show_beats_order() -> None:
    text = README.read_text(encoding="utf-8")
    section = text.split("## Como projetar", 1)[1]
    positions = [section.index(beat) for beat in SHOW_BEATS]
    assert positions == sorted(positions)


def test_justfile_has_open_goals_map() -> None:
    assert "open-goals-map" in JUSTFILE.read_text(encoding="utf-8")


def test_builder_constants() -> None:
    mod = _load_builder()
    assert mod.RUNTIME_LABEL == "Runtime (BentoML)"
    assert mod.ANOMALY_BACKLOG_CHIP == "detector: backlog"
    titles = [col[0] for col in mod.GOAL_COLUMNS]
    assert titles == list(GOAL_LABELS)
    assert mod.ANOMALY_BACKLOG_CHIP in mod.GOAL_COLUMNS[2][1]


def test_no_streamlit_dependency() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "streamlit" not in pyproject.lower()
