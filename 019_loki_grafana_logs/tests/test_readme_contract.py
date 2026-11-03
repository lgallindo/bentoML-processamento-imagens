"""Contrato textual e artefactos da aula 019."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
ILLUSTRATIONS = ROOT / "illustrations"

REQUIRED_FIGS = (
    "00_pipeline_logs.png",
    "01_loki_ready.png",
    "03_grafana_login.png",
    "04_grafana_datasources.png",
    "05_explore_logql_inference.png",
    "06_explore_phase_slow.png",
    "07_correlation_story.png",
    "08_metrics_vs_logs.png",
    "09_jsonl_sample.png",
)


def test_ports_and_prereqs() -> None:
    assert "3100" in README
    assert "4000" in README
    assert "016_grafana_dashboards" in README
    assert "LogQL" in README


def test_comparisons() -> None:
    assert "Prometheus" in README
    assert "Elasticsearch" in README
    assert "Datadog" in README


def test_never_grafana_on_3000_as_course_url() -> None:
    assert "3000" in README
    assert "Grafana" in README
    assert ":3000" in README  # warning text


def test_fixture_and_configs() -> None:
    assert (ROOT / "fixtures" / "bentoml_requests.jsonl").is_file()
    assert (ROOT / "monitoring" / "loki-config.yaml").is_file()
    assert (ROOT / "monitoring" / "promtail-config.yaml").is_file()
    assert (ROOT / "scripts" / "capture_screenshots.sh").is_file()


def test_illustrations() -> None:
    for name in REQUIRED_FIGS:
        path = ILLUSTRATIONS / name
        assert path.is_file(), f"missing {path}"
        assert path.stat().st_size > 800, f"too small: {path}"
