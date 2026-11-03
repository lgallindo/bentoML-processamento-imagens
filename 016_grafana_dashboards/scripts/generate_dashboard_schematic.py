#!/usr/bin/env python3
"""Esquema dos quatro painéis exigidos (quando a UI ainda não está capturável)."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parents[1] / "illustrations"
OUT.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(16)
t = np.linspace(0, 15, 180)


def main() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(11, 6.2), sharex=True)
    fig.suptitle(
        "Esquema do dashboard «BentoML — saúde» (aula 016)",
        fontsize=13,
        fontweight="bold",
    )

    # taxa
    ax = axes[0, 0]
    for name, base in (("/inference-grayscale", 1.2), ("/inference-blur", 0.4), ("/inference-resize", 0.7)):
        y = base + 0.15 * np.sin(t / 2) + 0.05 * rng.normal(size=t.size)
        ax.plot(t, np.clip(y, 0, None), label=name)
    ax.set_title("Requisições / s")
    ax.set_ylabel("req/s")
    ax.legend(fontsize=7, loc="upper right")

    # erros (quase zero)
    ax = axes[0, 1]
    err = 0.02 * (t > 8) * np.exp(-(t - 8)) + 0.001 * rng.random(t.size)
    ax.plot(t, err, color="#c62828", label="5xx (agregado)")
    ax.set_title("Taxa de erro")
    ax.set_ylabel("req/s")
    ax.legend(fontsize=7)

    # p95 + baseline
    ax = axes[1, 0]
    p95 = 0.06 + 0.01 * np.sin(t / 3) + 0.004 * rng.normal(size=t.size)
    p95 = np.where(t > 9, p95 + 0.04 * np.exp(-(t - 9) / 2), p95)
    baseline = 0.06 + 3 * 0.008 * np.ones_like(t)
    ax.plot(t, p95, label="p95")
    ax.plot(t, baseline, "--", label="média + 3σ (janela)")
    ax.set_title("p95 versus linha de base")
    ax.set_ylabel("s")
    ax.set_xlabel("minutos (relativos)")
    ax.legend(fontsize=7)

    # Explore vs Graph note
    ax = axes[1, 1]
    ax.axis("off")
    ax.text(
        0.02,
        0.95,
        "Como ler este layout",
        fontsize=11,
        fontweight="bold",
        transform=ax.transAxes,
        va="top",
    )
    ax.text(
        0.02,
        0.78,
        "• Canto superior esquerdo: volume — há tráfego?\n"
        "• Canto superior direito: erros — o HTTP verde mente?\n"
        "• Inferior esquerdo: latência com orçamento estatístico.\n"
        "• A UI real (Grafana :4000) empilha estes painéis\n"
        "  sobre a mesma fonte Prometheus da aula 010.\n"
        "• Capture o dashboard vivo com\n"
        "  scripts/capture_screenshots.sh",
        fontsize=9,
        transform=ax.transAxes,
        va="top",
        family="DejaVu Sans",
    )

    fig.tight_layout()
    path = OUT / "06_dashboard_health_schematic.png"
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


if __name__ == "__main__":
    main()
