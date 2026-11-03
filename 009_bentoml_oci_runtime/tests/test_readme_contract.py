"""Contrato textual da aula 009 (ponte OCI)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")


def test_ports_and_metrics() -> None:
    assert "3000" in README
    assert "/metrics" in README
    assert "OCI" in README or "oci" in README.lower()


def test_build_and_next_lesson() -> None:
    assert "bentoml build" in README or "just build" in README
    assert "010_prometheus_promql" in README
    assert "002_histogram_cdf_streamlit" in README


def test_no_grafana_on_3000_as_course_url() -> None:
    assert "Grafana@3000" not in README
    assert "http://127.0.0.1:3000" in README  # BentoML metrics OK
    assert "Grafana" in README
    assert "usa 3000" in README  # «não usa 3000 neste curso»
