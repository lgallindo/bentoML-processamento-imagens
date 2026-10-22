"""Gráfico Seaborn do histograma + CDF (copiar para a lição 001)."""

from __future__ import annotations

from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.figure import Figure


def plot_histogram_cdf(
    counts: Sequence[int],
    edges: Sequence[float],
    cdf: Sequence[float],
    *,
    title: str = "Histograma e CDF",
) -> Figure:
    """Barras (contagens) + linha da CDF no eixo direito."""
    counts_a = np.asarray(counts, dtype=float)
    edges_a = np.asarray(edges, dtype=float)
    cdf_a = np.asarray(cdf, dtype=float)
    centers = 0.5 * (edges_a[:-1] + edges_a[1:])
    widths = np.diff(edges_a)

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(centers, counts_a, width=widths * 0.9, color="#4c72b0", align="center")
    ax.set_xlabel("valor")
    ax.set_ylabel("contagem")
    ax.set_title(title)

    ax_cdf = ax.twinx()
    sns.lineplot(x=centers, y=cdf_a, ax=ax_cdf, color="#c44e52", marker="o")
    ax_cdf.set_ylabel("CDF")
    ax_cdf.set_ylim(0.0, 1.05)
    fig.tight_layout()
    return fig
