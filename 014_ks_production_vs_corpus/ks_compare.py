"""Kolmogorov–Smirnov entre histogramas agregados (corpus × production).

Compara as CDFs empíricas derivadas das contagens de um canal. A forma da
distribuição vem dos pixéis agregados; o tamanho efectivo da amostra para o
p-valor é o número de **imagens** de cada conjunto (ficção MLOps de drift
entre datasets).
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from corpus_stats import CHANNEL_KEYS, load_default_corpus_stats
from histogram import DEFAULT_BINS, cumulative_distribution, rebin_counts
from request_stats import load_default_request_stats


def ks_statistic(cdf_a: Sequence[float], cdf_b: Sequence[float]) -> float:
    """D = max |F_a − F_b| ao longo dos mesmos bins."""
    if len(cdf_a) != len(cdf_b):
        raise ValueError("as CDFs devem ter o mesmo número de bins")
    return max(abs(float(a) - float(b)) for a, b in zip(cdf_a, cdf_b))


def ks_p_value(statistic: float, n_eff: float) -> float:
    """Aproximação assintótica clássica de Kolmogorov–Smirnov (dois conjuntos)."""
    if n_eff <= 0.0 or statistic <= 0.0:
        return 1.0
    lam = (math.sqrt(n_eff) + 0.12 + 0.11 / math.sqrt(n_eff)) * statistic
    total = 0.0
    for k in range(1, 101):
        term = ((-1) ** (k - 1)) * math.exp(-2.0 * (k * lam) ** 2)
        total += term
        if abs(term) < 1e-12:
            break
    return max(0.0, min(1.0, 2.0 * total))


def compare_production_to_corpus(
    channel: str = "L",
    bins: int = DEFAULT_BINS,
    *,
    corpus_stats: dict | None = None,
    production_stats: dict | None = None,
) -> dict:
    """KS de production (pedidos) contra corpus (treino) no canal pedido."""
    corpus = corpus_stats if corpus_stats is not None else load_default_corpus_stats()
    production = (
        production_stats
        if production_stats is not None
        else load_default_request_stats()
    )
    key = CHANNEL_KEYS[channel]
    corpus_counts = rebin_counts(corpus["histograms"][key]["counts"], bins)
    production_counts = rebin_counts(production["histograms"][key]["counts"], bins)
    cdf_corpus = cumulative_distribution(corpus_counts)
    cdf_production = cumulative_distribution(production_counts)
    statistic = ks_statistic(cdf_corpus, cdf_production)
    n_images_corpus = int(corpus["n_images"])
    n_images_production = int(production["n_images"])
    n_eff = (n_images_corpus * n_images_production) / (
        n_images_corpus + n_images_production
    )
    return {
        "pipeline": "ks",
        "reference_dataset": "corpus",
        "compared_dataset": "production",
        "channel": channel,
        "bins": bins,
        "statistic": statistic,
        "p_value": ks_p_value(statistic, n_eff),
        "n_eff": n_eff,
        "n_pixels_corpus": int(sum(corpus_counts)),
        "n_pixels_production": int(sum(production_counts)),
        "n_images_corpus": n_images_corpus,
        "n_images_production": n_images_production,
    }
