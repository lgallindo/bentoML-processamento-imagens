"""Contrato textual e artefactos da aula 022 (LESSON-001)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
ILLUSTRATIONS = ROOT / "illustrations"
FIXTURES = ROOT / "fixtures"

REQUIRED_FIGS = (
    "00_yaml_to_rules_workflow.png",
    "01_targets_bentoml_imagens.png",
    "02_rules_page.png",
    "03_alerts_page.png",
    "04_graph_recording_series.png",
    "05_graph_alerts_series.png",
    "06_rules_vs_graph_vs_alerts.png",
)


def test_concept_and_title() -> None:
    assert README.startswith("# Aula 022 — ")
    title = README.splitlines()[0]
    assert title.count(":") == 0
    assert "**Conceito desta aula:**" in README
    assert "/rules" in README


def test_ports_table_course_only() -> None:
    assert "Portas que esta aula espera" in README
    assert "3000" in README
    assert "9090" in README
    ports = README.split("## Portas que esta aula espera no Host", 1)[1].split("## ", 1)[0]
    assert "Grafana" not in ports
    assert "Streamlit" not in ports
    assert "8516" not in ports


def test_self_contained_prereqs() -> None:
    prereq = README.split("## Pré-requisitos", 1)[1].split("## ", 1)[0]
    assert "conclua" not in prereq.lower() or "Se ainda não" in prereq
    # Não listar pastas irmãs como «você já concluiu»
    assert "você já" not in prereq.lower()


def test_neighbors_only_anterior_seguinte() -> None:
    assert "010_prometheus_promql" in README
    assert "021_prometheus_alerts_ui" in README
    roteiro = README.split("## Roteiro", 1)[1]
    assert "Anterior" in roteiro
    assert "Seguinte" in roteiro
    assert "015_prometheus_histcdf_streamlit" not in roteiro


def test_yaml_and_ui_ritual() -> None:
    assert "bentoml.rules.yml" in README
    assert "bentoml-response-time" in README
    assert "BentoMLResponseTimeAnomaly" in README
    assert "recording" in README.lower()
    assert "alerting" in README.lower() or "alert:" in README
    assert "/alerts" in README
    assert "Graph" in README or "Table" in README
    assert "bentoml-imagens" in README


def test_escopo_negativo_tables() -> None:
    assert "Escopo Negativo" in README
    assert "Fora desta aula" in README


def test_self_checkable_conclusion() -> None:
    assert "Conclusão (autoavaliação)" in README
    assert "Sim / Não" in README
    assert "colega" not in README.lower()
    assert "instrutor" not in README.lower()
    assert "professor" not in README.lower()


def test_no_bloom_or_sausage() -> None:
    low = README.lower()
    assert "bloom(" not in low
    assert "taxonomia de bloom" not in low
    assert "contrato canônico passa" not in low
    assert "mapa que faltava" not in low
    assert "agente" not in low


def test_pipeline_vocabulary() -> None:
    assert "tubulação" not in README.lower()


def test_fixtures_and_scripts() -> None:
    assert (FIXTURES / "bentoml.rules.yml").is_file()
    assert (FIXTURES / "rules_api_response.json").is_file()
    assert (FIXTURES / "targets_api_response.json").is_file()
    assert (ROOT / "SAMPLE_DATA.md").is_file()
    assert (ROOT / "scripts" / "capture_screenshots.sh").is_file()
    rules = (FIXTURES / "bentoml.rules.yml").read_text(encoding="utf-8")
    assert "bentoml-response-time" in rules
    assert "BentoMLResponseTimeAnomaly" in rules


def test_illustrations() -> None:
    for name in REQUIRED_FIGS:
        path = ILLUSTRATIONS / name
        assert path.is_file(), f"missing {path}"
        assert path.stat().st_size > 800, f"too small: {path}"
