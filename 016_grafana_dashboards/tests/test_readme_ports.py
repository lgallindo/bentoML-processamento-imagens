"""Contrato textual da aula 016 (Grafana)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")


def test_grafana_on_4000() -> None:
    assert "4000" in README
    assert "docs/grafana.md" in README
    assert "010_prometheus_promql" in README or "../010_prometheus_promql" in README


def test_no_grafana_course_url_on_3000() -> None:
    assert "http://127.0.0.1:3000" not in README or "Grafana" not in README.split("3000")[0][-80:]
    assert "nunca 3000" in README.lower() or "nunca **3000**" in README or "nunca 3000" in README


def test_exercise_without_streamlit_delivery() -> None:
    assert "sem Streamlit" in README or "Não use o painel Streamlit" in README
    assert "taxa de erro" in README.lower() or "Taxa de erro" in README
