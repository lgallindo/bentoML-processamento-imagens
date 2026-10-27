"""Kolmogorov–Smirnov entre histogramas agregados (corpus × production).

Transforma dois histogramas (referência e lote) na estatística D e no valor-p
assintótico usados pelo painel Streamlit e pelos testes. A forma da distribuição
vem dos pixels agregados; o tamanho efetivo da amostra para o valor-p é o
número de **imagens** de cada conjunto.

Pré-condições:
  - corpus_stats e production_stats trazem histograms[<canal>].counts e n_images;
  - após rebin, ambos os lados têm o mesmo número de bins.

Fluxo::

    counts_ref ──► rebin ──► CDF_ref ──┐
                                       ├──► D = max|ΔF| ──► (opcional) p-valor
    counts_lote ─► rebin ──► CDF_lote ─┘

Saídas principais: dict de compare_stats (statistic, p_value, cdf_*, counts_*).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from pathlib import Path

from corpus_stats import CHANNEL_KEYS, load_default_corpus_stats
from histogram import DEFAULT_BINS, cumulative_distribution, rebin_counts
from request_stats import load_request_stats


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


def compare_stats(
    corpus_stats: dict,
    production_stats: dict,
    *,
    channel: str = "L",
    bins: int = DEFAULT_BINS,
) -> dict:
    """KS de um lote de produção contra o corpus no canal pedido."""
    key = CHANNEL_KEYS[channel]
    corpus_counts = rebin_counts(corpus_stats["histograms"][key]["counts"], bins)
    production_counts = rebin_counts(
        production_stats["histograms"][key]["counts"], bins
    )
    cdf_corpus = cumulative_distribution(corpus_counts)
    cdf_production = cumulative_distribution(production_counts)
    statistic = ks_statistic(cdf_corpus, cdf_production)
    n_images_corpus = int(corpus_stats["n_images"])
    n_images_production = int(production_stats["n_images"])
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
        "counts_corpus": corpus_counts,
        "counts_production": production_counts,
        "cdf_corpus": cdf_corpus,
        "cdf_production": cdf_production,
    }


def compare_production_to_corpus(
    channel: str = "L",
    bins: int = DEFAULT_BINS,
    *,
    corpus_stats: dict | None = None,
    production_stats: dict | None = None,
    production_stats_path: str | Path | None = None,
) -> dict:
    """Compatível com testes: corpus default + production dict ou arquivo."""
    corpus = corpus_stats if corpus_stats is not None else load_default_corpus_stats()
    if production_stats is None:
        if production_stats_path is None:
            raise ValueError("indique production_stats ou production_stats_path")
        production_stats = load_request_stats(Path(production_stats_path))
    return compare_stats(
        corpus, production_stats, channel=channel, bins=bins
    )
