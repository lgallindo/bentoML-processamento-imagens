#!/usr/bin/env python3
"""Figuras didácticas de comparação (complemento às capturas de UI)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "illustrations"
OUT.mkdir(parents=True, exist_ok=True)


def _box(ax, xy, w, h, title: str, body: str, fc: str) -> None:
    patch = FancyBboxPatch(
        xy,
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.02",
        linewidth=1.2,
        edgecolor="#222",
        facecolor=fc,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + 0.02,
        xy[1] + h - 0.04,
        title,
        fontsize=11,
        fontweight="bold",
        va="top",
        ha="left",
    )
    ax.text(
        xy[0] + 0.02,
        xy[1] + h - 0.12,
        body,
        fontsize=8.5,
        va="top",
        ha="left",
        linespacing=1.35,
    )


def figure_roles() -> None:
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(
        "Quem responde a quê — papéis na trilha de saúde",
        fontsize=13,
        pad=12,
    )
    _box(
        ax,
        (0.02, 0.12),
        0.22,
        0.75,
        "BentoML\n/metrics",
        "Texto tipado\nHELP / TYPE\nlabels\n\nFonte bruta\n(aula 010 §1)",
        "#e8f1ff",
    )
    _box(
        ax,
        (0.27, 0.12),
        0.22,
        0.75,
        "Prometheus\nUI",
        "Scrape + TSDB\nPromQL Table/Graph\nregras / ALERTS\n\nInvestigação\nad-hoc (aula 010)",
        "#fff3e0",
    )
    _box(
        ax,
        (0.52, 0.12),
        0.22,
        0.75,
        "Grafana\ndashboards",
        "Painéis partilháveis\nvárias queries\nlinhas de base\n\nNarrativa operacional\n(esta aula 016)",
        "#e8f5e9",
    )
    _box(
        ax,
        (0.77, 0.12),
        0.21,
        0.75,
        "Streamlit\n015",
        "Didáctica local\nhist/CDF/p95\nsem scrape real\n\nReforço visual\nnão substitui\nGrafana",
        "#f3e5f5",
    )
    fig.tight_layout()
    path = OUT / "08_roles_comparison.png"
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


def figure_pipeline() -> None:
    fig, ax = plt.subplots(figsize=(10, 2.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2)
    ax.axis("off")
    ax.set_title("Do pedido HTTP ao painel — caminho desta aula", fontsize=12)
    steps = [
        (0.3, "Cliente\nHTTP"),
        (2.3, "BentoML\n:3000"),
        (4.3, "Prometheus\n:9090"),
        (6.3, "Grafana\n:4000"),
        (8.3, "Operador\npergunta"),
    ]
    for x, label in steps:
        ax.add_patch(
            FancyBboxPatch(
                (x, 0.55),
                1.5,
                1.0,
                boxstyle="round,pad=0.05,rounding_size=0.05",
                facecolor="#f7f7f7",
                edgecolor="#333",
            )
        )
        ax.text(x + 0.75, 1.05, label, ha="center", va="center", fontsize=9)
    for x0 in (1.8, 3.8, 5.8, 7.8):
        ax.annotate(
            "",
            xy=(x0 + 0.45, 1.05),
            xytext=(x0, 1.05),
            arrowprops=dict(arrowstyle="->", color="#444"),
        )
    ax.text(3.3, 0.25, "/metrics  →  scrape  →  PromQL  →  painel", fontsize=9, ha="center")
    fig.tight_layout()
    path = OUT / "00_pipeline_to_panel.png"
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


def main() -> None:
    figure_pipeline()
    figure_roles()


if __name__ == "__main__":
    main()
