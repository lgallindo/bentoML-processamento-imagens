from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ILLUSTRATIONS = ROOT / "illustrations"
LOGOS = ILLUSTRATIONS / "logos"
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

GOAL_WATCH_PHRASES = (
    "taxa de erro e latência",
    "corpus de referência",
    "média ± k desvios-padrão",
)

INDEX_FOLDERS = (
    "001_histogram_cdf_cli",
    "002_histogram_cdf_streamlit",
    "003_ks_drift_alert_streamlit",
    "004_prometheus_histcdf_streamlit",
    "005_ks_anomaly_detection_streamlit",
    "010_corpus_histograms_model",
    "020_grayscale_request_logging",
    "030_request_log_histograms",
    "040_ks_production_vs_corpus",
)

LOGO_FILES = (
    "mundo.png",
    "cientista.png",
    "modelo.png",
    "bentoml.png",
    "oci.png",
    "prometheus.png",
    "grafana.png",
)


def _load_builder():
    path = ROOT / "scripts" / "build_illustrations.py"
    spec = importlib.util.spec_from_file_location("build_illustrations", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["build_illustrations"] = mod
    spec.loader.exec_module(mod)
    return mod


def _mermaid_block(text: str) -> str:
    return text.split("```mermaid", 1)[1].split("```", 1)[0]


def test_three_figures_exist_and_under_budget() -> None:
    for path in (PIPELINES, TARGET, GOALS_MAP):
        assert path.is_file(), f"missing {path}"
        assert path.stat().st_size <= MAX_BYTES


def test_logos_exist() -> None:
    for name in LOGO_FILES:
        path = LOGOS / name
        assert path.is_file(), f"missing {path}"
        assert path.stat().st_size <= MAX_BYTES


def test_readme_goals_path_and_runtime_label() -> None:
    text = README.read_text(encoding="utf-8")
    for label in GOAL_LABELS:
        assert label in text, f"missing goal label: {label}"
    for phrase in GOAL_WATCH_PHRASES:
        assert phrase in text, f"missing goal watch phrase: {phrase}"
    assert "BentoML" in text and "Prometheus" in text and "Grafana" in text
    assert "Runtime (BentoML)" in text
    assert "## Comparação com a base" not in text
    assert "## Por que esta aula existe" not in text
    assert "../docs/prometheus.md" in text
    assert "../docs/grafana.md" in text


def test_readme_mermaid_architecture() -> None:
    text = README.read_text(encoding="utf-8")
    assert "```mermaid" in text
    mermaid = _mermaid_block(text)
    assert "Runtime (BentoML)" in mermaid
    assert "papel: DB de séries" in mermaid
    assert "papel: dashboard" in mermaid
    assert "Mundo" in mermaid
    assert "L001" not in mermaid
    assert "001–002" not in mermaid
    assert "040 KS" not in mermaid
    for name in LOGO_FILES:
        assert name in mermaid, f"mermaid missing logo ref: {name}"


def test_readme_index() -> None:
    text = README.read_text(encoding="utf-8")
    for name in INDEX_FOLDERS:
        assert name in text, f"missing index folder: {name}"


def test_readme_commands_section() -> None:
    text = README.read_text(encoding="utf-8")
    assert "## Figuras e comandos" in text
    section = text.split("## Figuras e comandos", 1)[1]
    for recipe in (
        "just sync",
        "just open-diagram",
        "just open-target",
        "just open-goals-map",
        "just test",
    ):
        assert recipe in section, f"missing recipe: {recipe}"


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
