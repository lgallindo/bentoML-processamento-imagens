"""Histograma Prometheus: buckets cumulativos → contagens, CDF, quantis."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import ArrayLike


def cumulative_to_bins(
    les: ArrayLike,
    cumulative: ArrayLike,
) -> dict[str, Any]:
    """Diferença de contagens cumulativas ordenadas por ``le``.

    Bordas de plot: ``[0.0] + les_finitos``. Contagens de plot: deltas dos
    buckets com ``le`` finito. O delta de ``+Inf`` fica só na tabela completa
    (``per_bin``).
    """
    le_arr = np.asarray(list(les), dtype=float)
    cum = np.asarray(list(cumulative), dtype=float)
    if le_arr.size == 0:
        raise ValueError("lista de buckets vazia")
    if le_arr.size != cum.size:
        raise ValueError("les e cumulative devem ter o mesmo comprimento")

    order = np.argsort(le_arr)
    le_arr = le_arr[order]
    cum = cum[order]
    if np.any(np.diff(cum) < -1e-9):
        raise ValueError("contagens cumulativas não são monótonas")

    prev = 0.0
    per_bin: list[float] = []
    lowers: list[float] = []
    uppers: list[float] = []
    for i, c in enumerate(cum):
        per_bin.append(float(c - prev))
        lo = 0.0 if i == 0 else float(le_arr[i - 1])
        if not np.isfinite(lo):
            lo = 0.0
        lowers.append(lo)
        uppers.append(float(le_arr[i]))
        prev = float(c)

    per_bin_a = np.asarray(per_bin, dtype=float)
    finite_mask = np.isfinite(le_arr)
    finite_les = le_arr[finite_mask]
    counts_plot = per_bin_a[finite_mask]
    edges = np.concatenate(([0.0], finite_les)).astype(float)

    return {
        "les": le_arr.tolist(),
        "cumulative": cum.tolist(),
        "per_bin": per_bin_a.tolist(),
        "lowers": lowers,
        "uppers": uppers,
        "edges": edges.tolist(),
        "counts": counts_plot.astype(float).tolist(),
    }


def cdf_from_counts(counts: ArrayLike) -> np.ndarray:
    """CDF normalizada: ``cumsum(counts) / sum(counts)``."""
    c = np.asarray(counts, dtype=float).ravel()
    total = float(c.sum())
    if total == 0:
        raise ValueError("não é possível calcular CDF com contagens vazias ou nulas")
    return np.cumsum(c) / total


def histogram_quantile_from_cumulative(
    q: float,
    les: ArrayLike,
    cumulative: ArrayLike,
) -> dict[str, Any]:
    """Estima o quantil ``q`` caminhando a massa cumulativa e interpolando no bin.

    Algoritmo alinhado à ideia do ``histogram_quantile`` do Prometheus:
    encontra o primeiro ``le`` cuja massa acumulada cobre ``q * total`` e
    interpola linearmente entre o ``le`` anterior e o atual.
    """
    if not 0.0 < q <= 1.0:
        raise ValueError("q deve estar em (0, 1]")

    le_arr = np.asarray(list(les), dtype=float)
    cum = np.asarray(list(cumulative), dtype=float)
    if le_arr.size == 0:
        raise ValueError("lista de buckets vazia")
    order = np.argsort(le_arr)
    le_arr = le_arr[order]
    cum = cum[order]

    total = float(cum[-1])
    if total <= 0:
        raise ValueError("não é possível calcular quantil com massa nula")

    rank = q * total
    prev_le = 0.0
    prev_cum = 0.0
    for le, c in zip(le_arr, cum, strict=True):
        if c < rank:
            prev_le = float(le)
            prev_cum = float(c)
            continue
        if not np.isfinite(le):
            return {
                "q": q,
                "value": float(prev_le) if prev_le > 0 else None,
                "bounded": False,
                "bucket_lo": float(prev_le),
                "bucket_hi": None,
            }
        bucket_mass = float(c) - prev_cum
        if bucket_mass <= 0:
            return {
                "q": q,
                "value": float(le),
                "bounded": True,
                "bucket_lo": float(prev_le),
                "bucket_hi": float(le),
            }
        frac = (rank - prev_cum) / bucket_mass
        value = prev_le + (float(le) - prev_le) * frac
        return {
            "q": q,
            "value": float(value),
            "bounded": True,
            "bucket_lo": float(prev_le),
            "bucket_hi": float(le),
        }

    last = float(le_arr[-1])
    return {
        "q": q,
        "value": last if np.isfinite(last) else None,
        "bounded": bool(np.isfinite(last)),
        "bucket_lo": float(prev_le),
        "bucket_hi": last if np.isfinite(last) else None,
    }


def payload_from_samples(samples: list[dict[str, Any]]) -> dict[str, Any]:
    """A partir de amostras normalizadas, monta tabela + CDF + metadados."""
    from prom_client import aggregate_by_le

    pairs = aggregate_by_le(samples)
    if not pairs:
        raise ValueError("sem amostras")
    les = [p[0] for p in pairs]
    cum = [p[1] for p in pairs]
    bins = cumulative_to_bins(les, cum)
    counts_for_cdf = bins["counts"]
    cdf = cdf_from_counts(counts_for_cdf).tolist() if sum(counts_for_cdf) > 0 else []
    return {
        **bins,
        "cdf": cdf,
        "total": float(cum[-1]),
    }


def python_quantile_source() -> str:
    """Fonte estável do helper de quantil para o painel de complexidade."""
    import inspect

    return inspect.getsource(histogram_quantile_from_cumulative)
