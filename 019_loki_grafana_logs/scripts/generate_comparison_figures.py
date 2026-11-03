#!/usr/bin/env python3
"""Figuras didácticas: pipeline de logs e comparação de instrumentos."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "illustrations"
OUT.mkdir(parents=True, exist_ok=True)


def _box(ax, xy, w, h, title: str, body: str, fc: str) -> None:
    ax.add_patch(
        FancyBboxPatch(
            xy,
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.02",
            linewidth=1.2,
            edgecolor="#222",
            facecolor=fc,
        )
    )
    ax.text(xy[0] + 0.02, xy[1] + h - 0.05, title, fontsize=10, fontweight="bold", va="top")
    ax.text(
        xy[0] + 0.02,
        xy[1] + h - 0.14,
        body,
        fontsize=8,
        va="top",
        linespacing=1.35,
    )


def figure_pipeline() -> None:
    fig, ax = plt.subplots(figsize=(11, 2.8))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 2)
    ax.axis("off")
    ax.set_title("Do ficheiro de log ao Explore — caminho desta aula", fontsize=12)
    steps = [
        (0.2, "JSONL\npedido"),
        (2.4, "Promtail\ntail"),
        (4.6, "Loki\n:3100"),
        (6.8, "Grafana\nExplore"),
        (9.0, "Correlação\n↔ Prom"),
    ]
    for x, label in steps:
        ax.add_patch(
            FancyBboxPatch(
                (x, 0.5),
                1.8,
                1.1,
                boxstyle="round,pad=0.05,rounding_size=0.05",
                facecolor="#f7f7f7",
                edgecolor="#333",
            )
        )
        ax.text(x + 0.9, 1.05, label, ha="center", va="center", fontsize=9)
    for x0 in (2.0, 4.2, 6.4, 8.6):
        ax.annotate(
            "",
            xy=(x0 + 0.35, 1.05),
            xytext=(x0, 1.05),
            arrowprops=dict(arrowstyle="->", color="#444"),
        )
    fig.tight_layout()
    path = OUT / "00_pipeline_logs.png"
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


def figure_roles() -> None:
    fig, ax = plt.subplots(figsize=(11, 5.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Métricas versus logs — quem responde a quê", fontsize=13, pad=10)
    _box(
        ax,
        (0.02, 0.15),
        0.22,
        0.7,
        "Prometheus\n(séries)",
        "Taxa, p95, up\naggregações\n\n«Quanto?»\n(aulas 010/016)",
        "#fff3e0",
    )
    _box(
        ax,
        (0.27, 0.15),
        0.22,
        0.7,
        "Loki\n(eventos)",
        "Linhas JSONL\nLogQL\nlabels job/…\n\n«O quê / quando?»\n(esta aula 019)",
        "#e3f2fd",
    )
    _box(
        ax,
        (0.52, 0.15),
        0.22,
        0.7,
        "Grafana\nExplore",
        "Mesma UI :4000\nProm + Loki\nmesma janela\n\nCorrelação\nvisual",
        "#e8f5e9",
    )
    _box(
        ax,
        (0.77, 0.15),
        0.21,
        0.7,
        "Elasticsearch\n018 (stub)",
        "Busca rica\naggregações\n\nOutro eixo\nde logs",
        "#fce4ec",
    )
    fig.tight_layout()
    path = OUT / "08_metrics_vs_logs.png"
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


def figure_correlation_story() -> None:
    import numpy as np

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5.2), sharex=True)
    t = np.arange(40)
    lat = np.where((t >= 20) & (t <= 24), 420 + (t - 20) * 40, 180 + (t % 5) * 3)
    ax1.plot(t, lat, color="#c62828", marker="o", ms=3)
    ax1.axvspan(20, 24, color="#ffcdd2", alpha=0.5, label="janela suspeita")
    ax1.set_ylabel("latency_ms (fixture)")
    ax1.set_title("Pico no registo (logs) — mesma história que um p95 alto")
    ax1.legend(fontsize=8)

    # fake log density
    dens = np.where((t >= 20) & (t <= 24), 5, 1)
    ax2.bar(t, dens, color="#1565c0", width=0.8)
    ax2.set_ylabel("linhas «slow»")
    ax2.set_xlabel("índice do evento no JSONL")
    ax2.set_title("Contagem de linhas com phase=slow (LogQL conceitual)")
    fig.tight_layout()
    path = OUT / "07_correlation_story.png"
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


def main() -> None:
    figure_pipeline()
    figure_roles()
    figure_correlation_story()


if __name__ == "__main__":
    main()
