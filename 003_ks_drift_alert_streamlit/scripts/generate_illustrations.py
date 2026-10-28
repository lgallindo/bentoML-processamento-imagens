#!/usr/bin/env python3
"""Gera illustrations/*.png usadas no README (e opcionalmente no Streamlit)."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from histogram import compute_histogram, cumulative_distribution  # noqa: E402
from ks_compare import ks_statistic  # noqa: E402
from plotting import plot_cdf_abs_diff, plot_dual_cdf, plot_histogram  # noqa: E402

OUT = ROOT / "illustrations"
REPO = ROOT.parent


def workflow() -> None:
    fig, ax = plt.subplots(figsize=(10, 2.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1)
    ax.axis("off")
    steps = [
        (0.6, "L\n(pixel)"),
        (2.3, "histograma\nh"),
        (4.0, "CDF\nF"),
        (5.7, "δ = |F−G|"),
        (7.4, "D = max δ"),
        (9.1, "alerta\nem D"),
    ]
    for i, (x, label) in enumerate(steps):
        ax.add_patch(
            mpatches.FancyBboxPatch(
                (x - 0.55, 0.25),
                1.1,
                0.5,
                boxstyle="round,pad=0.02,rounding_size=0.08",
                facecolor="#e3f2fd" if i < 5 else "#ffe0b2",
                edgecolor="#1565c0",
                linewidth=1.2,
            )
        )
        ax.text(x, 0.5, label, ha="center", va="center", fontsize=9)
        if i < len(steps) - 1:
            ax.annotate(
                "",
                xy=(steps[i + 1][0] - 0.6, 0.5),
                xytext=(x + 0.6, 0.5),
                arrowprops={"arrowstyle": "->", "color": "#455a64", "lw": 1.4},
            )
    ax.set_title("Fluxo: da luminância L ao alerta sobre D", fontsize=11, pad=8)
    fig.tight_layout()
    fig.savefig(OUT / "01_workflow_l_to_alert.png", dpi=140, bbox_inches="tight")
    plt.close(fig)


def workflow_single_boxes() -> None:
    """Uma PNG por caixa (não altera 01_workflow_l_to_alert.png)."""
    steps = [
        ("box_01_l_pixel.png", "L\n(pixel)", "#e3f2fd"),
        ("box_02_histograma_h.png", "histograma\nh", "#e3f2fd"),
        ("box_03_cdf_f.png", "CDF\nF", "#e3f2fd"),
        ("box_04_delta.png", "δ = |F−G|", "#e3f2fd"),
        ("box_05_d_max.png", "D = max δ", "#e3f2fd"),
        ("box_06_alerta_d.png", "alerta\nem D", "#ffe0b2"),
    ]
    for name, label, face in steps:
        fig, ax = plt.subplots(figsize=(2.4, 1.4))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.add_patch(
            mpatches.FancyBboxPatch(
                (0.08, 0.22),
                0.84,
                0.56,
                boxstyle="round,pad=0.02,rounding_size=0.08",
                facecolor=face,
                edgecolor="#1565c0",
                linewidth=1.4,
            )
        )
        ax.text(0.5, 0.5, label, ha="center", va="center", fontsize=11)
        fig.tight_layout(pad=0.1)
        fig.savefig(OUT / name, dpi=140, bbox_inches="tight")
        plt.close(fig)


def toy() -> None:
    h = np.array([2, 1, 3], dtype=float)
    cdf = np.cumsum(h) / h.sum()
    x = np.arange(3)
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.2))
    axes[0].bar(x, h, color="#455a64", width=0.7)
    axes[0].set_xticks(x)
    axes[0].set_xlabel("faixa de L")
    axes[0].set_ylabel("contagem")
    axes[0].set_title("Histograma (exemplo [2, 1, 3])")
    axes[1].step(x, cdf, where="post", color="#1565c0", linewidth=2)
    axes[1].scatter(x, cdf, color="#1565c0", zorder=3)
    axes[1].set_ylim(0, 1.05)
    axes[1].set_xticks(x)
    axes[1].set_xlabel("faixa de L")
    axes[1].set_ylabel("F")
    axes[1].set_title("CDF = acumulado / total")
    fig.suptitle("Do histograma à CDF — exemplo mínimo", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "02_hist_to_cdf_toy.png", dpi=140, bbox_inches="tight")
    plt.close(fig)


def pool(paths: list[Path]) -> list[int]:
    acc = [0] * 256
    for path in paths:
        for i, c in enumerate(compute_histogram(Image.open(path), channel="L", bins=256)):
            acc[i] += c
    return acc


def freeze_figs() -> None:
    beaches = sorted((REPO / "samples" / "beaches").glob("*.jpg"))[:50]
    forests = sorted((REPO / "samples" / "forests").glob("*.jpg"))[:50]
    ht, hp = pool(beaches), pool(forests)
    ft, fp = cumulative_distribution(ht), cumulative_distribution(hp)
    d = ks_statistic(ft, fp)
    plot_histogram(
        ht, title="Histograma de L — referência (praias)", series_label="treino", color="#1565c0"
    ).savefig(OUT / "03_hist_beaches.png", dpi=120, bbox_inches="tight")
    plt.close("all")
    plot_histogram(
        hp, title="Histograma de L — lote (florestas)", series_label="lote", color="#ef6c00"
    ).savefig(OUT / "04_hist_forests.png", dpi=120, bbox_inches="tight")
    plt.close("all")
    plot_dual_cdf(
        ft,
        fp,
        title=f"CDFs de L — D ≈ {d:.3f}",
        label_referencia="praias (treino)",
        label_lote="florestas",
    ).savefig(OUT / "05_dual_cdf.png", dpi=120, bbox_inches="tight")
    plt.close("all")
    plot_cdf_abs_diff(ft, fp, title="δ(L) = |F_ref − F_lote|").savefig(
        OUT / "06_delta_d.png", dpi=120, bbox_inches="tight"
    )
    plt.close("all")
    print(f"freeze D≈{d:.4f}")


def main() -> int:
    OUT.mkdir(exist_ok=True)
    workflow()
    workflow_single_boxes()
    toy()
    freeze_figs()
    print(f"ok → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
