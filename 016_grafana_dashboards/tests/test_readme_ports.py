"""Contrato textual da aula 016 (Grafana) — alinhado à profundidade da 010."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
ILLUSTRATIONS = ROOT / "illustrations"

REQUIRED_FIGS = (
    "00_pipeline_to_panel.png",
    "01_prometheus_graph_up.png",
    "02_prometheus_graph_rate.png",
    "03_grafana_login.png",
    "04_grafana_home.png",
    "05_grafana_datasources.png",
    "06_grafana_dashboard_health.png",
    "06_dashboard_health_schematic.png",
    "07_grafana_explore_up.png",
    "08_roles_comparison.png",
    "09_metrics_raw_text.png",
)


def test_grafana_on_4000() -> None:
    assert "4000" in README
    assert "docs/grafana.md" in README
    assert "010_prometheus_promql" in README


def test_never_grafana_course_default_3000() -> None:
    assert "nunca 3000" in README.lower() or "nunca **3000**" in README


def test_comparisons_and_storytelling_hooks() -> None:
    assert "Streamlit" in README
    assert "Datadog" in README
    assert "Explore" in README
    assert "caderno de bordo" in README or "história" in README.lower()


def test_exercise_without_streamlit_delivery() -> None:
    assert "sem Streamlit" in README or "sem** Streamlit" in README or "**sem** Streamlit" in README
    assert "Taxa de erro" in README or "taxa de erro" in README


def test_illustrations_present() -> None:
    for name in REQUIRED_FIGS:
        path = ILLUSTRATIONS / name
        assert path.is_file(), f"missing {path}"
        assert path.stat().st_size > 1000, f"too small: {path}"


def test_harness_script_exists() -> None:
    assert (ROOT / "scripts" / "capture_screenshots.sh").is_file()
    assert (ROOT / "fixtures" / "metrics_sample_head.txt").is_file()
