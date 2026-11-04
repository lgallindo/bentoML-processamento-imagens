#!/usr/bin/env python3
"""Audita o contrato de portas locais (docs/ports.md / aula 000)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FALHAS: list[str] = []


def falhar(msg: str) -> None:
    FALHAS.append(msg)


def check_prometheus_yml() -> None:
    path = RAIZ / "monitoring" / "prometheus.yml"
    text = path.read_text(encoding="utf-8")
    if "127.0.0.1:3000" not in text:
        falhar(f"{path.relative_to(RAIZ)}: target canônico 127.0.0.1:3000 ausente")


def check_grafana_datasource() -> None:
    path = RAIZ / "monitoring" / "grafana" / "datasources" / "bentoml-prometheus.yml"
    text = path.read_text(encoding="utf-8")
    if "http://127.0.0.1:9090" not in text:
        falhar(f"{path.relative_to(RAIZ)}: datasource deve apontar a http://127.0.0.1:9090")


def check_streamlit_justfiles() -> None:
    pat = re.compile(r"^(?P<n>\d{3})_.+")
    for pasta in sorted(RAIZ.iterdir()):
        if not pasta.is_dir():
            continue
        m = pat.match(pasta.name)
        if not m:
            continue
        n = int(m.group("n"))
        just = pasta / "justfile"
        if not just.is_file():
            continue
        text = just.read_text(encoding="utf-8")
        if "streamlit run" not in text and "streamlit" not in text.lower():
            # pastas sem painel Streamlit (ex. 001 CLI, 010+)
            if f'port="{8501 + n}"' not in text and "streamlit" not in text:
                continue
        expect = 8501 + n
        # recipes app/streamlit with default port=
        found = re.findall(
            r"(?:^|\n)(?:app|streamlit)\s+port=\"(\d+)\"",
            text,
        )
        if not found:
            # some files only mention streamlit in comments
            if "streamlit run" in text:
                falhar(
                    f"{pasta.name}/justfile: streamlit sem default port=\"{expect}\""
                )
            continue
        for port in found:
            if int(port) != expect:
                falhar(
                    f"{pasta.name}/justfile: Streamlit default {port}, "
                    f"esperado {expect} (8501+{n:03d})"
                )


def check_docs_grafana_not_course_default_3000() -> None:
    """Falha se a prosa apresentar Grafana@3000 como URL/padrão do curso."""
    ruins = (
        re.compile(r"Grafana[^\n]{0,40}https?://127\.0\.0\.1:3000", re.I),
        re.compile(r"Acesse\s+<http://127\.0\.0\.1:3000>", re.I),
        # Só falha se o curso documentar Grafana escutando em 3000 (não o sed
        # que *substitui* ;http_port = 3000 → 4000).
        re.compile(
            r"(?i)grafana[^\n]{0,80}(?:escuta|ouve|porta\s+padrão\s+do\s+curso)"
            r"[^\n]{0,40}3000"
        ),
    )
    for path in (RAIZ / "docs").rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for rx in ruins:
            if rx.search(text):
                falhar(
                    f"{path.relative_to(RAIZ)}: parece documentar Grafana na "
                    "porta 3000 como padrão do curso"
                )
                break


def check_ports_sot_exists() -> None:
    for rel in ("docs/ports.md", "000_mlops_pipelines_goals/README.md"):
        path = RAIZ / rel
        if not path.is_file():
            falhar(f"SoT ausente: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in ("3000", "9090", "4000"):
            if token not in text:
                falhar(f"{rel}: falta mencionar a porta {token}")


def main() -> int:
    check_ports_sot_exists()
    check_prometheus_yml()
    check_grafana_datasource()
    check_streamlit_justfiles()
    check_docs_grafana_not_course_default_3000()
    if FALHAS:
        print("check-ports: FALHOU", file=sys.stderr)
        for item in FALHAS:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print("check-ports: OK (trio 3000/9090/4000 + Streamlit 8501+N; 8501 livre)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
