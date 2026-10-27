from __future__ import annotations

import math

import pytest

from psi import (
    bin_values,
    compare_psi_means,
    compute_psi,
    counts_to_masses,
    quantile_edges,
)


def test_identical_masses_psi_zero() -> None:
    masses = [0.25, 0.25, 0.25, 0.25]
    assert compute_psi(masses, masses) == pytest.approx(0.0)


def test_known_toy_masses() -> None:
    # PSI = 1.6 * ln(9) ≈ 3.5129
    p_ref = [0.1, 0.9]
    p_lote = [0.9, 0.1]
    expected = 1.6 * math.log(9.0)
    assert compute_psi(p_ref, p_lote, eps=1e-12) == pytest.approx(expected, rel=1e-9)


def test_eps_handles_zero_mass() -> None:
    p_ref = [1.0, 0.0]
    p_lote = [0.0, 1.0]
    value = compute_psi(p_ref, p_lote, eps=1e-6)
    assert value > 0.0
    assert math.isfinite(value)


def test_counts_to_masses_sums_to_one() -> None:
    masses = counts_to_masses([2, 2, 4, 2])
    assert sum(masses) == pytest.approx(1.0)


def test_quantile_edges_and_bin_values() -> None:
    values = list(range(10))  # 0..9
    edges = quantile_edges(values, n_bins=5)
    assert len(edges) == 6
    assert edges[0] == pytest.approx(0.0)
    assert edges[-1] == pytest.approx(9.0)
    counts = bin_values(values, edges)
    assert sum(counts) == 10
    assert len(counts) == 5


def test_compare_psi_means_keys() -> None:
    corpus = {
        "n_images": 10,
        "luminance_means": [float(i) for i in range(10)],
        "histograms": {"luminance": {"counts": [1] * 256}},
    }
    production = {
        "n_images": 10,
        "luminance_means": [float(i + 40) for i in range(10)],
        "histograms": {"luminance": {"counts": [1] * 256}},
    }
    payload = compare_psi_means(corpus, production, n_bins=5)
    assert payload["pipeline"] == "psi_means"
    assert payload["psi"] > 0.0
    assert len(payload["p_ref"]) == 5
