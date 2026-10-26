"""Gráficos Seaborn: CDF corpus vs production + thumbnails auxiliares."""

from __future__ import annotations

from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.figure import Figure
from PIL import Image


def plot_dual_cdf(
    cdf_corpus: Sequence[float],
    cdf_production: Sequence[float],
    *,
    title: str = "CDF corpus vs production (L)",
) -> Figure:
    x = np.arange(len(cdf_corpus))
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.lineplot(x=x, y=np.asarray(cdf_corpus, dtype=float), ax=ax, label="corpus")
    sns.lineplot(
        x=x, y=np.asarray(cdf_production, dtype=float), ax=ax, label="production"
    )
    ax.set_xlabel("bin (L)")
    ax.set_ylabel("CDF")
    ax.set_ylim(0.0, 1.05)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    return fig


def load_thumbnails(paths: Sequence, *, max_n: int = 8, size: tuple[int, int] = (96, 96)):
    """Abre até max_n caminhos de imagem como PIL RGB redimensionado."""
    thumbs = []
    for path in list(paths)[:max_n]:
        with Image.open(path) as im:
            im = im.convert("RGB")
            im.thumbnail(size)
            thumbs.append(im.copy())
    return thumbs
