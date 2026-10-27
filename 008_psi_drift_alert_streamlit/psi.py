"""Population Stability Index (PSI) entre massas de referência e lote.

P2 (primário): média de L por imagem, faixas por quantis da referência.
P1 (espelho): histograma de L por pixel, mesmas faixas da aula KS.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from pathlib import Path

from corpus_stats import CHANNEL_KEYS, load_default_corpus_stats
from histogram import DEFAULT_BINS, rebin_counts
from request_stats import load_request_stats

EPS_DEFAULT = 1e-6
MEAN_BINS_DEFAULT = 10


def counts_to_masses(counts: Sequence[int | float], *, eps: float = 0.0) -> list[float]:
    """Massas relativas (soma = 1). Se total zero, devolve zeros."""
    total = float(sum(counts))
    if total <= 0.0:
        return [0.0] * len(counts)
    masses = [float(c) / total for c in counts]
    if eps <= 0.0:
        return masses
    smoothed = [max(m, eps) for m in masses]
    s = sum(smoothed)
    return [m / s for m in smoothed]


def compute_psi(
    p_ref: Sequence[float],
    p_lote: Sequence[float],
    *,
    eps: float = EPS_DEFAULT,
) -> float:
    """PSI = Σ_b (p_lote[b] − p_ref[b]) · ln(p_lote[b] / p_ref[b]) com eps."""
    if len(p_ref) != len(p_lote):
        raise ValueError("p_ref e p_lote devem ter o mesmo número de faixas")
    total = 0.0
    for pr_raw, pl_raw in zip(p_ref, p_lote):
        pr = max(float(pr_raw), eps)
        pl = max(float(pl_raw), eps)
        total += (pl - pr) * math.log(pl / pr)
    return float(total)


def quantile_edges(values: Sequence[float], n_bins: int = MEAN_BINS_DEFAULT) -> list[float]:
    """Limites de faixa a partir dos quantis empíricos (inclui min e max)."""
    if n_bins < 1:
        raise ValueError("n_bins deve ser ≥ 1")
    if not values:
        raise ValueError("values não pode ser vazio")
    ordered = sorted(float(v) for v in values)
    n = len(ordered)
    edges: list[float] = []
    for i in range(n_bins + 1):
        if i == 0:
            edges.append(ordered[0])
            continue
        if i == n_bins:
            edges.append(ordered[-1])
            continue
        # posição linear no estilo numpy percentile
        pos = (i / n_bins) * (n - 1)
        lo = int(math.floor(pos))
        hi = int(math.ceil(pos))
        if lo == hi:
            edges.append(ordered[lo])
        else:
            w = pos - lo
            edges.append(ordered[lo] * (1.0 - w) + ordered[hi] * w)
    # garante monotonia estrita onde há empates (empurra epsilon de valor)
    for i in range(1, len(edges)):
        if edges[i] <= edges[i - 1]:
            edges[i] = edges[i - 1] + 1e-9
    return edges


def bin_values(values: Sequence[float], edges: Sequence[float]) -> list[int]:
    """Contagens por faixa; última faixa inclui o extremo direito."""
    if len(edges) < 2:
        raise ValueError("edges precisa de pelo menos 2 limites")
    n_bins = len(edges) - 1
    counts = [0] * n_bins
    last = n_bins - 1
    for v in values:
        x = float(v)
        placed = False
        for b in range(last):
            if edges[b] <= x < edges[b + 1]:
                counts[b] += 1
                placed = True
                break
        if not placed:
            # cai na última faixa (inclui max)
            counts[last] += 1
    return counts


def compare_psi_means(
    corpus_stats: dict,
    production_stats: dict,
    *,
    n_bins: int = MEAN_BINS_DEFAULT,
    eps: float = EPS_DEFAULT,
) -> dict:
    """P2: PSI sobre média de L por imagem (faixas = quantis da referência)."""
    means_ref = [float(x) for x in corpus_stats["luminance_means"]]
    means_lote = [float(x) for x in production_stats["luminance_means"]]
    edges = quantile_edges(means_ref, n_bins=n_bins)
    counts_ref = bin_values(means_ref, edges)
    counts_lote = bin_values(means_lote, edges)
    # massas brutas (sem renormalizar eps nas massas); compute_psi aplica eps
    p_ref = counts_to_masses(counts_ref)
    p_lote = counts_to_masses(counts_lote)
    psi = compute_psi(p_ref, p_lote, eps=eps)
    return {
        "pipeline": "psi_means",
        "variable": "mean_L_per_image",
        "n_bins": n_bins,
        "eps": eps,
        "psi": psi,
        "edges": edges,
        "counts_ref": counts_ref,
        "counts_lote": counts_lote,
        "p_ref": p_ref,
        "p_lote": p_lote,
        "n_images_corpus": int(corpus_stats["n_images"]),
        "n_images_production": int(production_stats["n_images"]),
        "means_ref": means_ref,
        "means_lote": means_lote,
    }


def compare_psi_pixels(
    corpus_stats: dict,
    production_stats: dict,
    *,
    channel: str = "L",
    bins: int = DEFAULT_BINS,
    eps: float = EPS_DEFAULT,
) -> dict:
    """P1: PSI sobre histograma de L por pixel (espelho da aula KS)."""
    key = CHANNEL_KEYS[channel]
    counts_ref = rebin_counts(corpus_stats["histograms"][key]["counts"], bins)
    counts_lote = rebin_counts(production_stats["histograms"][key]["counts"], bins)
    p_ref = counts_to_masses(counts_ref)
    p_lote = counts_to_masses(counts_lote)
    psi = compute_psi(p_ref, p_lote, eps=eps)
    return {
        "pipeline": "psi_pixels",
        "variable": "L_per_pixel",
        "channel": channel,
        "bins": bins,
        "eps": eps,
        "psi": psi,
        "counts_ref": counts_ref,
        "counts_lote": counts_lote,
        "p_ref": p_ref,
        "p_lote": p_lote,
        "n_pixels_corpus": int(sum(counts_ref)),
        "n_pixels_production": int(sum(counts_lote)),
        "n_images_corpus": int(corpus_stats["n_images"]),
        "n_images_production": int(production_stats["n_images"]),
    }


def compare_production_to_corpus_means(
    *,
    n_bins: int = MEAN_BINS_DEFAULT,
    eps: float = EPS_DEFAULT,
    corpus_stats: dict | None = None,
    production_stats: dict | None = None,
    production_stats_path: str | Path | None = None,
) -> dict:
    corpus = corpus_stats if corpus_stats is not None else load_default_corpus_stats()
    if production_stats is None:
        if production_stats_path is None:
            raise ValueError("indique production_stats ou production_stats_path")
        production_stats = load_request_stats(Path(production_stats_path))
    return compare_psi_means(corpus, production_stats, n_bins=n_bins, eps=eps)
