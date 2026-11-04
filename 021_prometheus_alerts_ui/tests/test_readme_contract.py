"""Contrato textual da aula 021 (página Alerts)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
ILLUSTRATIONS = ROOT / "illustrations"

REQUIRED_FIGS = (
    "00_alert_state_flow.png",
    "01_alerts_pending.png",
    "02_alerts_firing.png",
)


def test_concept_and_alerts_path() -> None:
    assert "**Conceito desta aula:**" in README
    assert "/alerts" in README
    assert "9090" in README
    assert "BentoMLResponseTimeAnomaly" in README
    assert "bentoml.rules.yml" in README


def test_states_and_distinction() -> None:
    assert "pending" in README
    assert "firing" in README
    assert "ALERTS" in README
    assert "Graph" in README or "Table" in README


def test_links_neighbors_not_prereq_force() -> None:
    assert "022_prometheus_rules_ui" in README
    assert "015_prometheus_histcdf_streamlit" in README
    prereq = README.split("## Pré-requisitos", 1)[1].split("## ", 1)[0]
    assert "015_prometheus_histcdf_streamlit" not in prereq
    assert "022_prometheus_rules_ui" not in prereq


def test_no_grafana_or_streamlit_course_urls() -> None:
    assert "Streamlit" not in README
    assert "Grafana@3000" not in README
    assert "http://127.0.0.1:3000" not in README or "/metrics" in README
    # Grafana must not appear as a port this lesson operates
    assert "4000" not in README


def test_wrong_prometheus_documented() -> None:
    assert "bentoml-imagens" in README
    assert "outro" in README.lower() or "outra" in README.lower()


def test_self_checkable_conclusion() -> None:
    assert "Conclusão (autoavaliação)" in README
    assert "Sim / Não" in README
    assert "colega" not in README.lower()
    assert "instrutor" not in README.lower()


def test_illustrations_and_fixtures() -> None:
    for name in REQUIRED_FIGS:
        path = ILLUSTRATIONS / name
        assert path.is_file(), f"missing {path}"
        assert path.stat().st_size > 1000, f"too small: {path}"
    assert (ROOT / "fixtures" / "alerts_pending_example.json").is_file()
    assert (ROOT / "fixtures" / "alerts_firing_example.json").is_file()
