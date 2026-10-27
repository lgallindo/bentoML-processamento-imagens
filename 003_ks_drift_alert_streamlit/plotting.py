"""Gráficos Seaborn do ritual L → histograma → CDF → δ → D.

Pré-condições: contagens/CDFs com o mesmo comprimento quando dual.

Fluxo::

    counts/CDF ──► plot_histogram / plot_cdf / plot_dual_cdf / plot_cdf_abs_diff

Saídas principais: Figure matplotlib; load_thumbnails para amostras.
"""

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


def abs_diff_cdfs(
    cdf_a: Sequence[float],
    cdf_b: Sequence[float],
) -> tuple[np.ndarray, float, int]:
    """δ(i) = |F_a(i) − F_b(i)|; devolve (δ, D, índice do máximo)."""
    a = np.asarray(cdf_a, dtype=float)
    b = np.asarray(cdf_b, dtype=float)
    delta = np.abs(a - b)
    idx = int(np.argmax(delta))
    return delta, float(delta[idx]), idx


def plot_dual_cdf(
    cdf_referencia: Sequence[float],
    cdf_lote: Sequence[float],
    *,
    title: str = "Duas CDFs da variável L",
    label_referencia: str = "referência",
    label_lote: str = "lote",
    mark_ks: bool = True,
) -> Figure:
    ref = np.asarray(cdf_referencia, dtype=float)
    lote = np.asarray(cdf_lote, dtype=float)
    x = _series_x(len(ref))
    _, d_ks, idx = abs_diff_cdfs(ref, lote)
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.lineplot(x=x, y=ref, ax=ax, label=label_referencia)
    sns.lineplot(x=x, y=lote, ax=ax, label=label_lote)
    if mark_ks:
        ax.vlines(
            idx,
            ymin=min(ref[idx], lote[idx]),
            ymax=max(ref[idx], lote[idx]),
            colors="#c62828",
            linewidths=2.5,
            label=f"D = {d_ks:.4f}",
        )
    ax.set_xlabel("valor de L do pixel (0 … 255)")
    ax.set_ylabel("F(L)")
    ax.set_ylim(0.0, 1.05)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_cdf_abs_diff(
    cdf_referencia: Sequence[float],
    cdf_lote: Sequence[float],
    *,
    title: str = "Diferença absoluta entre as CDFs",
) -> Figure:
    """Gráfico de δ(L) = |F_ref(L) − F_lote(L)| com D = max δ."""
    delta, d_ks, idx = abs_diff_cdfs(cdf_referencia, cdf_lote)
    x = _series_x(len(delta))
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8, 4.0))
    sns.lineplot(x=x, y=delta, ax=ax, color="#6a1b9a", label="δ(L) = |F_ref − F_lote|")
    ax.axhline(d_ks, color="#c62828", linestyle="--", linewidth=1.5, label=f"D = {d_ks:.4f}")
    ax.scatter([idx], [d_ks], color="#c62828", zorder=5, s=40)
    ax.set_xlabel("valor de L do pixel (0 … 255)")
    ax.set_ylabel("δ(L)")
    ax.set_ylim(0.0, max(1.05 * d_ks, 0.05))
    ax.set_title(title)
    ax.legend(loc="upper right")
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
