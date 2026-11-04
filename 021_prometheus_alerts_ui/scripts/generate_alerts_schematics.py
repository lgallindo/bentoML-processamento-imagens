#!/usr/bin/env python3
"""Gera esquemas didáticos da página Alerts (pending / firing)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

OUT = Path(__file__).resolve().parents[1] / "illustrations"
OUT.mkdir(parents=True, exist_ok=True)


def _chrome(ax, title: str, state: str, state_color: str) -> None:
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.2, 0.3), 9.6, 6.4, boxstyle="round,pad=0.05",
                                facecolor="#f4f4f5", edgecolor="#27272a", linewidth=1.5))
    ax.add_patch(Rectangle((0.2, 6.0), 9.6, 0.7, facecolor="#18181b", edgecolor="none"))
    ax.text(0.5, 6.35, "Prometheus  ·  Alerts", color="white", fontsize=11, va="center",
            fontfamily="sans-serif")
    ax.text(5.0, 5.5, title, ha="center", fontsize=12, fontweight="bold")
    # rule card
    ax.add_patch(FancyBboxPatch((0.8, 2.2), 8.4, 2.8, boxstyle="round,pad=0.08",
                                facecolor="white", edgecolor="#a1a1aa", linewidth=1.2))
    ax.text(1.1, 4.5, "BentoMLResponseTimeAnomaly", fontsize=11, fontweight="bold")
    ax.text(1.1, 4.0, "severity=warning   ·   for: 1m", fontsize=9, color="#52525b")
    ax.add_patch(FancyBboxPatch((7.2, 4.2), 1.7, 0.55, boxstyle="round,pad=0.05",
                                facecolor=state_color, edgecolor="none"))
    ax.text(8.05, 4.45, state, ha="center", va="center", color="white",
            fontsize=9, fontweight="bold")
    ax.text(1.1, 3.3, "expr: p95_1m  >  avg_over_time(...[30m]) + 3 × stddev_over_time(...)",
            fontsize=8, color="#3f3f46")
    ax.text(1.1, 2.6, "Labels: endpoint=/inference-grayscale", fontsize=9, color="#52525b")


def save_pending() -> Path:
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=140)
    _chrome(ax, "Página /alerts — regra verdadeira, for: ainda contando", "pending", "#ca8a04")
    ax.text(5.0, 1.2,
            "A expressão já é verdadeira; o Prometheus espera o intervalo for: 1m.",
            ha="center", fontsize=9, color="#27272a")
    path = OUT / "01_alerts_pending.png"
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def save_firing() -> Path:
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=140)
    _chrome(ax, "Página /alerts — for: cumprido", "firing", "#dc2626")
    ax.text(5.0, 1.2,
            "A expressão permaneceu verdadeira pelo for: 1m. Isto ainda não envia e-mail sozinho.",
            ha="center", fontsize=9, color="#27272a")
    path = OUT / "02_alerts_firing.png"
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def save_flow() -> Path:
    fig, ax = plt.subplots(figsize=(9, 3.2), dpi=140)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 3)
    ax.axis("off")
    boxes = [
        (0.3, "inactive\n(expressão falsa)", "#a1a1aa"),
        (4.1, "pending\n(verdadeira, for:…)", "#ca8a04"),
        (7.9, "firing\n(for: cumprido)", "#dc2626"),
    ]
    for x, label, color in boxes:
        ax.add_patch(FancyBboxPatch((x, 0.7), 3.2, 1.6, boxstyle="round,pad=0.08",
                                    facecolor=color, edgecolor="#18181b", linewidth=1))
        ax.text(x + 1.6, 1.5, label, ha="center", va="center", color="white",
                fontsize=10, fontweight="bold")
    ax.annotate("", xy=(4.0, 1.5), xytext=(3.5, 1.5),
                arrowprops=dict(arrowstyle="->", color="#18181b", lw=1.5))
    ax.annotate("", xy=(7.8, 1.5), xytext=(7.3, 1.5),
                arrowprops=dict(arrowstyle="->", color="#18181b", lw=1.5))
    ax.set_title("Estados na página Alerts (e na série ALERTS)", fontsize=11)
    path = OUT / "00_alert_state_flow.png"
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def main() -> None:
    paths = [save_flow(), save_pending(), save_firing()]
    for p in paths:
        print(p, p.stat().st_size)


if __name__ == "__main__":
    main()
