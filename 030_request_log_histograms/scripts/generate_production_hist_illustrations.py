"""Gera ilustrações didácticas corpus vs production → illustrations/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "illustrations"


def main() -> int:
    import matplotlib.pyplot as plt
    import numpy as np

    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 12,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )

    # --- 1) Dois pipelines ---
    fig, ax = plt.subplots(figsize=(10.5, 4.0), constrained_layout=True)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    # corpus row
    for x, y, w, h, text, color in [
        (0.3, 2.6, 2.0, 1.0, "samples/\ntrain_*", "#dbeafe"),
        (2.8, 2.6, 2.2, 1.0, "features/ +\ncorpus_stats.json", "#fef3c7"),
        (5.5, 2.6, 4.0, 1.0, "/monitor-histogram-corpus-{json,csv,image}", "#dcfce7"),
        (0.3, 0.6, 2.0, 1.0, "exerciser\nexer_*", "#dbeafe"),
        (2.8, 0.6, 2.2, 1.0, "request_features/ +\nrequest_stats.json", "#fce7f3"),
        (5.5, 0.6, 4.0, 1.0, "/monitor-histogram-production-{json,csv,image}", "#ede9fe"),
    ]:
        ax.add_patch(
            plt.Rectangle(
                (x, y), w, h, facecolor=color, edgecolor="#334155", linewidth=1.5, zorder=2
            )
        )
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=10, zorder=3)
    for y in (3.1, 1.1):
        for x0, x1 in [(2.3, 2.8), (5.0, 5.5)]:
            ax.annotate(
                "",
                xy=(x1, y),
                xytext=(x0, y),
                arrowprops=dict(arrowstyle="->", color="#334155", lw=1.4),
            )
    ax.text(0.3, 3.9, "Corpus (treino)", fontsize=11, fontweight="bold")
    ax.text(0.3, 1.9, "Production (log de pedidos)", fontsize=11, fontweight="bold")
    ax.set_title("Mesmo formato de relatório; conjuntos separados")
    fig.savefig(OUT / "01_two_pipelines.png", dpi=160)
    plt.close(fig)

    # --- 2) Overlay esquemático corpus vs production ---
    rng = np.random.default_rng(42)
    x = np.linspace(0, 255, 256)
    corpus = np.exp(-0.5 * ((x - 120) / 35) ** 2)
    production = np.exp(-0.5 * ((x - 160) / 40) ** 2)
    corpus = corpus / corpus.sum()
    production = production / production.sum()
    fig, ax = plt.subplots(figsize=(9.0, 4.2), constrained_layout=True)
    ax.plot(x, corpus, label="corpus (treino)", color="#4c72b0", linewidth=2)
    ax.plot(x, production, label="production (pedidos)", color="#c44e52", linewidth=2)
    ax.fill_between(x, corpus, alpha=0.15, color="#4c72b0")
    ax.fill_between(x, production, alpha=0.15, color="#c44e52")
    ax.set_xlabel("nível do canal L")
    ax.set_ylabel("densidade (esquemática)")
    ax.set_title("Pergunta de monitoramento: as curvas ainda se parecem?")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    fig.savefig(OUT / "02_corpus_vs_production_hist.png", dpi=160)
    plt.close(fig)

    # --- 3) Fluxo do exercitador ---
    fig, ax = plt.subplots(figsize=(10.5, 3.2), constrained_layout=True)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    boxes = [
        (0.2, 1.0, 2.2, 1.2, "download-\nexerciser-samples", "#dbeafe"),
        (2.8, 1.0, 2.2, 1.2, "exercise-\ngrayscale\nPOST", "#fef3c7"),
        (5.4, 1.0, 2.0, 1.2, "build-\nrequest-stats", "#dcfce7"),
        (7.8, 1.0, 1.9, 1.2, "curl monitor\nproduction-*", "#ede9fe"),
    ]
    for x, y, w, h, text, color in boxes:
        ax.add_patch(
            plt.Rectangle(
                (x, y), w, h, facecolor=color, edgecolor="#334155", linewidth=1.5, zorder=2
            )
        )
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=10, zorder=3)
    for x0, x1 in [(2.4, 2.8), (5.0, 5.4), (7.4, 7.8)]:
        ax.annotate(
            "",
            xy=(x1, 1.6),
            xytext=(x0, 1.6),
            arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5),
        )
    ax.set_title("Receitas just: do download ao relatório de production")
    fig.savefig(OUT / "03_exerciser_flow.png", dpi=160)
    plt.close(fig)

    print(f"wrote illustrations under {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
