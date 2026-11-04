"""Contrato textual e artefatos da aula 017 (DEGRADE-001)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
ILLUSTRATIONS = ROOT / "illustrations"
GATE = ROOT / "scripts" / "check_datadog_gate.py"

REQUIRED_FIGS = (
    "00_pipeline_datadog.png",
    "03_degrade001_gate.png",
    "06_datadog_dashboard_schematic.png",
    "08_labels_vs_tags.png",
)


def test_ports_and_prereqs() -> None:
    assert "8125" in README
    assert "8126" in README
    assert "3000" in README
    assert "OpenMetrics" in README


def test_self_contained_concept() -> None:
    assert "**Conceito desta aula:**" in README
    prereq = README.split("## Pré-requisitos", 1)[1].split("## ", 1)[0]
    assert "conclua" not in prereq.lower()
    assert "010_prometheus_promql" not in prereq
    assert "`010`" not in prereq


def test_readme_brazilian_portuguese_not_european() -> None:
    assert "dialeto" in README
    assert "dialecto" not in README
    assert "## Objetivos" in README
    assert "Objectivos" not in README
    assert "canónico" not in README
    assert "arquivos" in README
    assert "ficheiros" not in README
    assert "esqueleto" not in README.lower()


def test_degrade001_documented() -> None:
    assert "DEGRADE-001" in README
    assert "DD_API_KEY" in README
    assert "SKIP" in README
    assert "RUN" in README


def test_comparisons() -> None:
    assert "Prometheus" in README
    assert "label" in README.lower()
    assert "tag" in README.lower()


def test_never_commit_api_key_instruction() -> None:
    assert "nunca" in README.lower()
    assert ".env" in README
    assert "Git" in README or "commit" in README.lower()


def test_gate_skip_without_key(monkeypatch) -> None:
    env = os.environ.copy()
    env.pop("DD_API_KEY", None)
    env["DD_API_KEY"] = "   "
    out = subprocess.check_output(
        [sys.executable, str(GATE)],
        env=env,
        text=True,
    )
    assert "DATADOG_LAB=SKIP" in out


def test_gate_run_with_key() -> None:
    env = os.environ.copy()
    env["DD_API_KEY"] = "lab-not-a-real-key"
    out = subprocess.check_output(
        [sys.executable, str(GATE)],
        env=env,
        text=True,
    )
    assert "DATADOG_LAB=RUN" in out
    assert "lab-not-a-real-key" not in out


def test_openmetrics_example_is_complete_yaml() -> None:
    path = ROOT / "monitoring" / "openmetrics.example.yaml"
    text = path.read_text(encoding="utf-8")
    assert "openmetrics_endpoint:" in text
    assert "http://127.0.0.1:3000/metrics" in text
    assert "bentoml_service_request_total" in text
    # Não pode permanecer só como bloco comentado («esqueleto»).
    active = [
        line
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert any("openmetrics_endpoint:" in line for line in active)
    assert (ROOT / "scripts" / "check_datadog_gate.py").is_file()


def test_skip_fixtures_and_mapper() -> None:
    assert (ROOT / "SAMPLE_DATA.md").is_file()
    assert (ROOT / "fixtures" / "sample_metrics_snippet.txt").is_file()
    assert (ROOT / "fixtures" / "label_tag_pairs.example.json").is_file()
    assert (ROOT / "fixtures" / "gate_skip.example.txt").is_file()
    mapper = ROOT / "scripts" / "map_labels_from_fixture.py"
    assert mapper.is_file()
    out = subprocess.check_output([sys.executable, str(mapper)], text=True)
    payload = json.loads(out)
    assert len(payload["pairs"]) >= 3


def test_exit_checklist_not_stamp() -> None:
    assert "## Checklist de saída" in README
    assert "Conclusão (autoavaliação)" not in README
    assert "Marque **Sim** ou **Não** sozinho" not in README


def test_illustrations() -> None:
    for name in REQUIRED_FIGS:
        path = ILLUSTRATIONS / name
        assert path.is_file(), f"missing {path}"
        assert path.stat().st_size > 800, f"too small: {path}"
