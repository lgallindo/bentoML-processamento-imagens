#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "illustrations"
OUT.mkdir(parents=True, exist_ok=True)


def _box(ax, xy, w, h, title, body, fc):
    ax.add_patch(
        FancyBboxPatch(
            xy, w, h, boxstyle="round,pad=0.02,rounding_size=0.02",
            linewidth=1.2, edgecolor="#222", facecolor=fc,
        )
    )
    ax.text(xy[0] + 0.02, xy[1] + h - 0.05, title, fontsize=10, fontweight="bold", va="top")
    ax.text(xy[0] + 0.02, xy[1] + h - 0.14, body, fontsize=8, va="top", linespacing=1.35)


def main() -> None:
    fig, ax = plt.subplots(figsize=(11, 2.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2)
    ax.axis("off")
    ax.set_title("Do JSONL ao _search — caminho da aula 018", fontsize=12)
    for x, label in ((0.3, "JSONL\npedidos"), (2.5, "POST\n_bulk"), (4.7, "ES\n:9200"), (6.9, "_search\nDev Tools"), (8.8, "Contagens\npor phase")):
        ax.add_patch(FancyBboxPatch((x, 0.45), 1.7, 1.1, boxstyle="round,pad=0.05,rounding_size=0.05", facecolor="#f7f7f7", edgecolor="#333"))
        ax.text(x + 0.85, 1.0, label, ha="center", va="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "00_pipeline_es.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Onde o Elasticsearch se encaixa", fontsize=13, pad=8)
    _box(ax, (0.02, 0.2), 0.22, 0.6, "Prometheus", "Séries / PromQL\n«Quanto?»", "#fff3e0")
    _box(ax, (0.27, 0.2), 0.22, 0.6, "Loki 019", "Linhas + LogQL\nleve, OSS+Grafana", "#e3f2fd")
    _box(ax, (0.52, 0.2), 0.22, 0.6, "Elasticsearch\n018", "Documentos\nfiltros + agg\nbusca rica", "#e8f5e9")
    _box(ax, (0.77, 0.2), 0.21, 0.6, "Datadog 017", "Vendor SaaS\nmétricas+logs", "#fce4ec")
    fig.tight_layout()
    fig.savefig(OUT / "08_roles_comparison.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    print("wrote figures in", OUT)


if __name__ == "__main__":
    main()
