"""Contrato textual da aula 009 (ponte OCI)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
ILLUSTRATIONS = ROOT / "illustrations"

REQUIRED_FIGS = (
    "00_bento_to_runtime.png",
    "01_containerize_backends.png",
    "02_metrics_smoke.png",
    "03_cloud_deploy_map.png",
)


def test_concept_ports_metrics() -> None:
    assert "**Conceito desta aula:**" in README
    assert "3000" in README
    assert "/metrics" in README
    assert "OCI" in README


def test_build_containerize_backends() -> None:
    assert "just build" in README or "bentoml build" in README
    assert "containerize" in README
    assert "podman" in README.lower()
    assert "OCI_RUNTIME" in README
    assert "--backend" in README or "backend" in README.lower()


def test_cloud_map_only() -> None:
    assert "BentoCloud" in README or "bentoml deploy" in README
    assert "mapa" in README.lower()
    # conta não é pré-requisito
    prereq = README.split("## Pré-requisitos", 1)[1].split("## ", 1)[0]
    assert "não" in prereq.lower()
    assert "BentoCloud" in prereq or "conta" in prereq.lower()


def test_ci_build_only_honesty() -> None:
    assert "bentoml-oci.yml" in README
    assert "containerize" in README.lower()
    assert "build" in README.lower()


def test_roteiro_neighbors_not_prereq() -> None:
    assert "010_prometheus_promql" in README
    assert "002_histogram_cdf_streamlit" in README
    prereq = README.split("## Pré-requisitos", 1)[1].split("## ", 1)[0]
    assert "010_prometheus_promql" not in prereq
    assert "002_histogram_cdf_streamlit" not in prereq


def test_no_grafana_on_3000_as_course_url() -> None:
    assert "Grafana@3000" not in README
    assert "http://127.0.0.1:3000" in README
    assert "Grafana" in README
    assert "usa" in README and "3000" in README


def test_self_checkable_exit_checklist() -> None:
    assert "## Checklist de saída" in README
    assert "Sim / Não" in README
    assert "colega" not in README.lower()
    assert "instrutor" not in README.lower()


def test_illustrations_present() -> None:
    for name in REQUIRED_FIGS:
        path = ILLUSTRATIONS / name
        assert path.is_file(), f"missing {path}"
        assert path.stat().st_size > 1000, f"too small: {path}"
