#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "illustrations"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    fig, ax = plt.subplots(figsize=(11, 2.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2)
    ax.axis("off")
    ax.set_title("Do /metrics local ao vendor — caminho conceptual da 017", fontsize=12)
    for x, label in (
        (0.3, "BentoML\n:3000/metrics"),
        (2.5, "Agent /\nOpenMetrics"),
        (4.7, "Datadog\nSaaS"),
        (6.9, "Dashboard\ntags"),
        (8.8, "Contraste\n↔ Prom"),
    ):
        ax.add_patch(
            FancyBboxPatch(
                (x, 0.45), 1.7, 1.1,
                boxstyle="round,pad=0.05,rounding_size=0.05",
                facecolor="#f7f7f7", edgecolor="#333",
            )
        )
        ax.text(x + 0.85, 1.0, label, ha="center", va="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "00_pipeline_datadog.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    # schematic "dashboard"
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0))
    t = np.linspace(0, 15, 80)
    axes[0].plot(t, 1.2 + 0.2 * np.sin(t / 2), label="req/s (tag endpoint)")
    axes[0].set_title("Esquema — taxa no Datadog")
    axes[0].legend(fontsize=8)
    axes[1].plot(t, 0.07 + 0.01 * np.sin(t / 3), color="#c62828", label="p95")
    axes[1].axhline(0.1, ls="--", color="#666", label="monitor threshold")
    axes[1].set_title("Esquema — latência + monitor")
    axes[1].legend(fontsize=8)
    fig.suptitle(
        "Figuras esquemáticas (lab SaaS opcional — DEGRADE-001)",
        fontsize=12,
    )
    fig.tight_layout()
    fig.savefig(OUT / "06_datadog_dashboard_schematic.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    rows = [
        ("Prometheus label", "Datadog tag", "job=\"bentoml-imagens\"", "job:bentoml-imagens"),
        ("endpoint=\"/inference-…\"", "endpoint:/inference-…", "PromQL rate()", "metric + tag filter"),
        ("Recording rule", "Monitor / notebook", "Local :9090", "SaaS us1/eu1/…"),
    ]
    ax.text(0.02, 0.92, "Label ≠ tag — mesmo conceito, outro dialecto", fontsize=13, fontweight="bold")
    y = 0.75
    for a, b, c, d in rows:
        ax.text(0.02, y, f"• Prom: {a}  →  DD: {b}", fontsize=10)
        ax.text(0.06, y - 0.08, f"{c}   |   {d}", fontsize=9, color="#444")
        y -= 0.22
    fig.tight_layout()
    fig.savefig(OUT / "08_labels_vs_tags.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Quando saltar o lab SaaS (DEGRADE-001)", fontsize=13, pad=8)
    texts = [
        (0.05, "#e8f5e9", "DD_API_KEY\ndefinida", "Pode seguir o\nlab OpenMetrics\n+ dashboard"),
        (0.38, "#fff8e1", "chave omitida\nou em branco", "Saltar SaaS;\n010/016/019\ncontinuam válidas"),
        (0.71, "#ffebee", "chave inválida\n/ rede bloqueada", "Falhar fechado\nno modo SaaS;\nnão inventar híbrido"),
    ]
    for x, fc, title, body in texts:
        ax.add_patch(
            FancyBboxPatch(
                (x, 0.2), 0.26, 0.55,
                boxstyle="round,pad=0.02,rounding_size=0.02",
                facecolor=fc, edgecolor="#333",
            )
        )
        ax.text(x + 0.13, 0.62, title, ha="center", fontsize=10, fontweight="bold")
        ax.text(x + 0.13, 0.42, body, ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "03_degrade001_gate.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
