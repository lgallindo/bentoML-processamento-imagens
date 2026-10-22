"""API canónica de histograma + CDF (copiar para a lição 001).

Funções públicas:
  - histogram_from_values
  - cdf_from_counts
  - histogram_with_cdf
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike

DEFAULT_BINS = 10


def histogram_from_values(
    values: ArrayLike,
    bins: int = DEFAULT_BINS,
    *,
    value_range: tuple[float, float] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Devolve ``(counts, bin_edges)`` via ``np.histogram``.

    Rejeita entrada vazia e valores fora de ``value_range`` (quando declarado
    ou inferido a partir dos dados).
    """
    if bins < 1:
        raise ValueError("bins deve ser um inteiro positivo")
    arr = np.asarray(values, dtype=float).ravel()
    if arr.size == 0:
        raise ValueError("a lista de valores não pode ser vazia")
    if not np.isfinite(arr).all():
        raise ValueError("os valores devem ser finitos")

    if value_range is None:
        lo = float(arr.min())
        hi = float(arr.max())
    else:
        lo, hi = float(value_range[0]), float(value_range[1])
        if lo > hi:
            raise ValueError("value_range inválido: lo > hi")

    outside = (arr < lo) | (arr > hi)
    if np.any(outside):
        bad = arr[outside][0]
        raise ValueError(f"valor fora do intervalo [{lo}, {hi}]: {bad}")

    counts, edges = np.histogram(arr, bins=bins, range=(lo, hi))
    return counts.astype(int), edges


def cdf_from_counts(counts: ArrayLike) -> np.ndarray:
    """CDF normalizada: ``cumsum(counts) / sum(counts)``."""
    c = np.asarray(counts, dtype=float).ravel()
    total = float(c.sum())
    if total == 0:
        raise ValueError("não é possível calcular CDF com contagens vazias ou nulas")
    return np.cumsum(c) / total


def histogram_with_cdf(
    values: ArrayLike,
    bins: int = DEFAULT_BINS,
    *,
    value_range: tuple[float, float] | None = None,
) -> dict:
    """Pacote didático: contagens, bordas, CDF e metadados."""
    arr = np.asarray(values, dtype=float).ravel()
    counts, edges = histogram_from_values(arr, bins, value_range=value_range)
    cdf = cdf_from_counts(counts)
    return {
        "n": int(arr.size),
        "bins": int(bins),
        "range": [float(edges[0]), float(edges[-1])],
        "counts": counts.tolist(),
        "edges": edges.tolist(),
        "cdf": cdf.tolist(),
    }
