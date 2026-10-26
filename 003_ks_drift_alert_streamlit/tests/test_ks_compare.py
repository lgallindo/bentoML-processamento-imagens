from __future__ import annotations

import pytest

from ks_compare import compare_production_to_corpus, ks_p_value, ks_statistic


def test_ks_statistic_identical_is_zero() -> None:
    cdf = [0.25, 0.5, 0.75, 1.0]
    assert ks_statistic(cdf, cdf) == 0.0


def test_ks_statistic_known_gap() -> None:
    a = [0.0, 0.5, 1.0]
    b = [0.0, 0.1, 1.0]
    assert ks_statistic(a, b) == pytest.approx(0.4)


def test_ks_p_value_bounds() -> None:
    assert ks_p_value(0.0, 100.0) == 1.0
    p = ks_p_value(0.5, 50.0)
    assert 0.0 <= p <= 1.0


def test_compare_production_to_corpus_keys() -> None:
    corpus = {
        "n_images": 2,
        "histograms": {
            "luminance": {"counts": [10, 0, 0, 10]},
        },
    }
    production = {
        "n_images": 2,
        "histograms": {
            "luminance": {"counts": [0, 10, 10, 0]},
        },
    }
    payload = compare_production_to_corpus(
        channel="L",
        bins=4,
        corpus_stats=corpus,
        production_stats=production,
    )
    assert payload["pipeline"] == "ks"
    assert payload["statistic"] > 0.0
    assert 0.0 <= payload["p_value"] <= 1.0
    assert "cdf_corpus" in payload
