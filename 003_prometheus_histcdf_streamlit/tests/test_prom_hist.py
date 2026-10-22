from __future__ import annotations

import pytest

from prom_client import fetch_duration_buckets_from_fixture
from prom_hist import (
    cdf_from_counts,
    cumulative_to_bins,
    histogram_quantile_from_cumulative,
    payload_from_samples,
    python_quantile_source,
)


def test_differencing_golden() -> None:
    # Spec: cumulative [2, 5, 5] → per_bin [2, 3, 0]
    bins = cumulative_to_bins([0.1, 0.2, float("inf")], [2, 5, 5])
    assert bins["per_bin"] == pytest.approx([2, 3, 0])


def test_cdf_ends_at_one() -> None:
    cdf = cdf_from_counts([2, 3, 5])
    assert cdf[-1] == pytest.approx(1.0)
    assert list(cdf) == pytest.approx([0.2, 0.5, 1.0])


def test_zero_mass_rejected() -> None:
    with pytest.raises(ValueError, match="nulas|vazias"):
        cdf_from_counts([0, 0])
    with pytest.raises(ValueError, match="massa nula"):
        histogram_quantile_from_cumulative(0.95, [0.1, 1.0], [0, 0])


def test_p95_within_bucket() -> None:
    # 20 observations; p95 → rank 19; mass reaches 18 at 0.05, 20 at 0.1
    les = [0.005, 0.01, 0.025, 0.05, 0.1, float("inf")]
    cum = [2, 5, 12, 18, 20, 20]
    result = histogram_quantile_from_cumulative(0.95, les, cum)
    assert result["bounded"] is True
    assert result["bucket_lo"] == pytest.approx(0.05)
    assert result["bucket_hi"] == pytest.approx(0.1)
    assert 0.05 <= result["value"] <= 0.1


def test_fixture_payload_cdf() -> None:
    samples = fetch_duration_buckets_from_fixture(endpoint="/grayscale")
    payload = payload_from_samples(samples)
    assert payload["total"] == 20
    assert payload["cdf"]
    assert payload["cdf"][-1] == pytest.approx(1.0)


def test_python_snippet_has_walk_steps() -> None:
    src = python_quantile_source()
    assert "rank" in src
    assert "frac" in src or "interpol" in src.lower() or "bucket_mass" in src
