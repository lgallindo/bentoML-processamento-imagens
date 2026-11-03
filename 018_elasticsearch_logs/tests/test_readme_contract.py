"""Contrato textual e artefactos da aula 018."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
ILLUSTRATIONS = ROOT / "illustrations"

REQUIRED_FIGS = (
    "00_pipeline_es.png",
    "01_es_root.png",
    "02_cluster_health.png",
    "05_search_phase_slow.png",
    "06_agg_by_phase.png",
    "08_roles_comparison.png",
    "09_jsonl_sample.png",
)


def test_ports_and_prereqs() -> None:
    assert "9200" in README
    assert "019_loki_grafana_logs" in README
    assert "_bulk" in README
    assert "_search" in README


def test_comparisons() -> None:
    assert "Prometheus" in README
    assert "Loki" in README
    assert "Datadog" in README


def test_no_kibana_required() -> None:
    assert "não" in README.lower() or "nao" in README.lower()
    assert "Kibana" in README


def test_fixture_and_scripts() -> None:
    assert (ROOT / "fixtures" / "generate_sample_log.py").is_file()
    assert (ROOT / "scripts" / "bulk_index_fixture.py").is_file()
    assert (ROOT / "scripts" / "capture_screenshots.sh").is_file()
    assert (ROOT / "fixtures" / "bentoml_requests.jsonl").is_file()
    assert (ROOT / "fixtures" / "search_phase_slow.json").is_file()
    assert (ROOT / "fixtures" / "agg_by_phase.json").is_file()


def test_illustrations() -> None:
    for name in REQUIRED_FIGS:
        path = ILLUSTRATIONS / name
        assert path.is_file(), f"missing {path}"
        assert path.stat().st_size > 800, f"too small: {path}"
