"""Gera ilustrações didácticas do app histograma+CDF → illustrations/."""

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

    from histcdf import histogram_with_cdf
    from plotting import plot_histogram_cdf

    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 12,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )

    # --- 1) Layout conceptual do app ---
    fig, ax = plt.subplots(figsize=(10.5, 3.4), constrained_layout=True)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.2)
    ax.axis("off")
    boxes = [
        (0.3, 1.0, 2.0, 1.4, "Entrada\ntextarea / CSV\n/ amostra", "#dbeafe"),
        (2.8, 1.0, 2.2, 1.4, "Controles\nbins, [lo, hi]\nbarra lateral", "#fef3c7"),
        (5.5, 1.0, 2.0, 1.4, "histcdf.py\ncontagens + CDF", "#dcfce7"),
        (8.0, 1.0, 1.7, 1.4, "Saída\ntabela +\ngráfico", "#ede9fe"),
    ]
    for x, y, w, h, text, color in boxes:
        ax.add_patch(
            plt.Rectangle(
                (x, y), w, h, facecolor=color, edgecolor="#334155", linewidth=1.5, zorder=2
            )
        )
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=10, zorder=3)
    for x0, x1 in [(2.3, 2.8), (5.0, 5.5), (7.5, 8.0)]:
        ax.annotate(
            "",
            xy=(x1, 1.7),
            xytext=(x0, 1.7),
            arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5),
        )
    ax.set_title("App Streamlit: da entrada ao gráfico")
    fig.savefig(OUT / "01_app_layout.png", dpi=160)
    plt.close(fig)

    # --- 2) Histograma + CDF do exemplo 1,2,2,5 bins=4 ---
    values = np.array([1.0, 2.0, 2.0, 5.0])
    result = histogram_with_cdf(values, bins=4)
    fig = plot_histogram_cdf(
        result["counts"],
        result["edges"],
        result["cdf"],
        title="Exemplo: 1, 2, 2, 5 — bins=4",
    )
    fig.savefig(OUT / "02_hist_cdf_same_centers.png", dpi=160)
    plt.close(fig)

    # --- 3) Intervalo fixo [0, 4] ---
    values_fixed = np.array([0.0, 0.5, 1.0, 2.5, 4.0])
    result_fixed = histogram_with_cdf(values_fixed, bins=4, value_range=(0.0, 4.0))
    fig = plot_histogram_cdf(
        result_fixed["counts"],
        result_fixed["edges"],
        result_fixed["cdf"],
        title="Intervalo fixo [0, 4] — contagens [2, 1, 1, 1]",
    )
    fig.savefig(OUT / "03_fixed_range.png", dpi=160)
    plt.close(fig)

    print(f"wrote illustrations under {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
