"""Testes textuais da aula 020."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")

PRIMARY_BIB_URLS = (
    "https://sre.google/sre-book/monitoring-distributed-systems/",
    "https://prometheus.io/docs/practices/alerting/",
    "https://prometheus.io/docs/practices/the_zen/",
    "https://linuxczar.net/sysadmin/philosophy-on-alerting/",
    "https://docs.bentoml.org/en/latest/build-with-bentoml/observability/metrics.html",
)


def test_no_contract_template_file() -> None:
    assert not (ROOT / "CONTRACT_TEMPLATE.md").exists()
    assert "CONTRACT_TEMPLATE" not in README


def test_no_branded_contrato_de_monitoramento() -> None:
    assert "contrato de monitoramento" not in README.lower()
    assert "Contrato de monitoramento" not in README


def test_title_four_fields() -> None:
    assert README.lstrip().startswith("# Aula 020 — Sinal, limiar, ação e dono")


def test_parable_and_illustration() -> None:
    assert "## O que quebra sem dono" in README
    assert "**Cena 1 — latência.**" in README
    assert "**Cena 2 — dados.**" in README
    assert "illustrations/01_duas_cenas.png" in README
    assert (ROOT / "illustrations" / "01_duas_cenas.png").is_file()


def test_readme_conceito_and_neighbors() -> None:
    assert "**Conceito desta aula:**" in README
    assert "008_psi_drift_alert_streamlit" in README
    assert "000_mlops_pipelines_goals" in README
    assert "Saúde do servidor" in README
    assert "Drift de dados" in README
    assert "Detecção de anomalias" in README


def test_readme_brazilian_acao_spelling() -> None:
    assert "ação" in README.lower() or "Ação" in README
    assert "acção" not in README.lower()
    assert "Acção" not in README


def test_readme_escopo_negativo() -> None:
    assert "Escopo Negativo" in README


def test_readme_bibliografia_primary_urls() -> None:
    assert "## Bibliografia" in README
    for url in PRIMARY_BIB_URLS:
        assert url in README, f"missing primary bib URL: {url}"


def test_readme_no_grafana_on_bentoml_port() -> None:
    assert "grafana@3000" not in README.lower()
    for line in README.splitlines():
        if "grafana" in line.lower() and "3000" in line:
            raise AssertionError(f"Grafana must not share a line with 3000: {line}")


def test_readme_no_bloom_taxonomy() -> None:
    bloom_labels = (
        "Remember",
        "Understand",
        "Apply",
        "Analyze",
        "Evaluate",
        "Create",
        "Lembrar",
        "Compreender",
        "Aplicar",
        "Analisar",
        "Avaliar",
        "Criar",
        "taxonomia de Bloom",
        "Bloom's",
    )
    for label in bloom_labels:
        assert label not in README, f"Bloom label leaked into student README: {label}"


def test_ops_and_filosofia_in_readme() -> None:
    assert "Campos *Ops*" in README or "Campos Ops" in README
    assert "## Filosofia DevOps" in README
    for label in ("DevOps", "MLOps", "CVOps", "LLMOps", "AIOps"):
        assert label in README
    assert "CAMPOS_OPS.md" not in README
    assert "## Portas" not in README


def test_no_fecho_vocabulary() -> None:
    hits = re.findall(r"(?i)\bfecho\b", README)
    assert not hits, f"README still uses fecho: {hits}"


def test_no_european_guillemets_in_readme() -> None:
    assert "«" not in README and "»" not in README
