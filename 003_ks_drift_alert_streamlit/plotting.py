"""Gráficos Seaborn: histograma, CDF e comparação lado a lado."""

from __future__ import annotations

from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.figure import Figure
from PIL import Image


def _series_x(n: int) -> np.ndarray:
    return np.arange(n)


def plot_histogram(
    counts: Sequence[int | float],
    *,
    title: str,
    series_label: str,
    color: str | None = None,
) -> Figure:
    """Barras das contagens por faixa de luminância."""
    y = np.asarray(counts, dtype=float)
    x = _series_x(len(y))
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.bar(x, y, width=1.0, color=color or "#455a64", align="edge")
    ax.set_xlabel("valor de L do pixel (0 = preto … 255 = branco)")
    ax.set_ylabel("contagem de pixels")
    ax.set_title(title)
    ax.set_xticks([])
    ax.text(
        0.98,
        0.95,
        series_label,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=10,
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8},
    )
    fig.tight_layout()
    return fig


def plot_cdf(
    cdf: Sequence[float],
    *,
    title: str,
    series_label: str,
    color: str | None = None,
) -> Figure:
    """Curva da distribuição acumulada a partir do histograma de L."""
    y = np.asarray(cdf, dtype=float)
    x = _series_x(len(y))
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(7, 3.6))
    sns.lineplot(x=x, y=y, ax=ax, color=color or "#1565c0", label=series_label)
    ax.set_xlabel("valor de L do pixel (0 … 255)")
    ax.set_ylabel("F(L) — fração acumulada de pixels")
    ax.set_ylim(0.0, 1.05)
    ax.set_title(title)
    ax.legend(loc="lower right")
    fig.tight_layout()
    return fig


def plot_dual_cdf(
    cdf_referencia: Sequence[float],
    cdf_lote: Sequence[float],
    *,
    title: str = "Duas CDFs da variável L",
    label_referencia: str = "referência",
    label_lote: str = "lote",
) -> Figure:
    x = _series_x(len(cdf_referencia))
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.lineplot(
        x=x,
        y=np.asarray(cdf_referencia, dtype=float),
        ax=ax,
        label=label_referencia,
    )
    sns.lineplot(
        x=x,
        y=np.asarray(cdf_lote, dtype=float),
        ax=ax,
        label=label_lote,
    )
    ax.set_xlabel("valor de L do pixel (0 … 255)")
    ax.set_ylabel("F(L)")
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
