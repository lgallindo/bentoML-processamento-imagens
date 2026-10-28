#!/usr/bin/env python3
"""Gera illustrations/*.png usadas no README e no Streamlit da aula 008."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from plotting import plot_histogram, plot_mass_bars  # noqa: E402
from psi import compare_psi_means, counts_to_masses  # noqa: E402
from corpus_stats import load_default_corpus_stats  # noqa: E402
from request_stats import load_request_stats  # noqa: E402

OUT = ROOT / "illustrations"


def workflow() -> None:
    fig, ax = plt.subplots(figsize=(9.5, 2.2))
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 1)
    ax.axis("off")
    steps = [
        (0.8, "hist\ncontagens"),
        (2.8, "massas\np_b"),
        (4.8, "termo\nKL"),
        (6.8, "PSI\n= Σ"),
        (8.5, "faixa\nalerta"),
    ]
    for i, (x, label) in enumerate(steps):
        ax.add_patch(
            mpatches.FancyBboxPatch(
                (x - 0.55, 0.25),
                1.1,
                0.5,
                boxstyle="round,pad=0.02,rounding_size=0.08",
                facecolor="#e3f2fd" if i < 4 else "#ffe0b2",
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
    ax.set_title("Fluxo: do histograma ao alerta sobre PSI", fontsize=11, pad=8)
    fig.tight_layout()
    fig.savefig(OUT / "01_workflow_hist_to_psi.png", dpi=140, bbox_inches="tight")
    plt.close(fig)


def workflow_single_boxes() -> None:
    steps = [
        ("box_01_massas.png", "massas\np_b", "#e3f2fd"),
        ("box_02_termo_kl.png", "termo\nKL", "#e3f2fd"),
        ("box_03_psi_soma.png", "PSI\n= Σ", "#e3f2fd"),
        ("box_04_faixa.png", "faixa\nalerta", "#ffe0b2"),
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


def toy_masses() -> None:
    """Exemplo mínimo: contagens → massas → termos → PSI."""
    c_ref = np.array([5, 3, 2], dtype=float)
    c_lote = np.array([2, 3, 5], dtype=float)
    p_ref = counts_to_masses(c_ref.tolist())
    p_lote = counts_to_masses(c_lote.tolist())
    eps = 1e-6
    terms = [
        (max(pl, eps) - max(pr, eps))
        * math.log(max(pl, eps) / max(pr, eps))
        for pr, pl in zip(p_ref, p_lote)
    ]
    psi = sum(terms)
    x = np.arange(3)
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.2))
    axes[0].bar(x - 0.15, c_ref, width=0.3, color="#1565c0", label="ref")
    axes[0].bar(x + 0.15, c_lote, width=0.3, color="#ef6c00", label="lote")
    axes[0].set_xticks(x)
    axes[0].set_title("Contagens")
    axes[0].legend(fontsize=8)
    axes[1].bar(x - 0.15, p_ref, width=0.3, color="#1565c0")
    axes[1].bar(x + 0.15, p_lote, width=0.3, color="#ef6c00")
    axes[1].set_xticks(x)
    axes[1].set_ylim(0, 1)
    axes[1].set_title("Massas p_b")
    axes[2].bar(x, terms, color="#6a1b9a", width=0.6)
    axes[2].axhline(0, color="#455a64", lw=0.8)
    axes[2].set_xticks(x)
    axes[2].set_title(f"Termos KL → PSI ≈ {psi:.3f}")
    fig.suptitle("Do histograma ao PSI — exemplo mínimo", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "02_hist_to_psi_toy.png", dpi=140, bbox_inches="tight")
    plt.close(fig)


def freeze_figs() -> None:
    corpus = load_default_corpus_stats()
    forests = load_request_stats(ROOT / "batch_stats" / "forests.json")
    p2 = compare_psi_means(corpus, forests, n_bins=10)
    plot_mass_bars(
        p2["p_ref"],
        p2["p_lote"],
        title="Massas P2 — referência vs florestas",
        label_ref="praias (treino)",
        label_lote="florestas",
        xlabel="faixa (quantil da referência)",
    ).savefig(OUT / "03_massas_p2_forests.png", dpi=120, bbox_inches="tight")
    plt.close("all")
    # histograma de médias (contagens por faixa)
    plot_histogram(
        p2["counts_ref"],
        title="Contagens P2 — referência (médias de L)",
        series_label="treino",
        color="#1565c0",
    ).savefig(OUT / "04_counts_p2_ref.png", dpi=120, bbox_inches="tight")
    plt.close("all")
    plot_histogram(
        p2["counts_lote"],
        title="Contagens P2 — lote florestas",
        series_label="lote",
        color="#ef6c00",
    ).savefig(OUT / "05_counts_p2_forests.png", dpi=120, bbox_inches="tight")
    plt.close("all")
    print(f"freeze PSI_P2(forests)≈{p2['psi']:.4f}")


def main() -> int:
    OUT.mkdir(exist_ok=True)
    workflow()
    workflow_single_boxes()
    toy_masses()
    freeze_figs()
    print(f"ok → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
