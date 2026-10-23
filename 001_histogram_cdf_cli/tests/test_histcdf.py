from __future__ import annotations

import numpy as np
import pytest

from histcdf import cdf_from_counts, histogram_from_values, histogram_with_cdf


def test_sum_of_counts_equals_n() -> None:
    values = np.array([1.0, 2.0, 2.0, 5.0])
    counts, edges = histogram_from_values(values, bins=4)
    assert int(counts.sum()) == values.size
    assert len(counts) == 4
    assert len(edges) == 5


def test_golden_toy_vector() -> None:
    values = np.array([0.0, 0.5, 1.0, 2.5, 4.0])
    counts, _edges = histogram_from_values(values, bins=4, value_range=(0.0, 4.0))
    assert counts.tolist() == [2, 1, 1, 1]


def test_out_of_range_rejected() -> None:
    with pytest.raises(ValueError, match="fora do intervalo"):
        histogram_from_values([1.0, 9.0], bins=2, value_range=(0.0, 5.0))


def test_empty_rejected() -> None:
    with pytest.raises(ValueError, match="vazia"):
        histogram_from_values([], bins=3)


def test_bins_one() -> None:
    counts, _edges = histogram_from_values([3.0, 1.0, 2.0], bins=1)
    assert counts.tolist() == [3]


def test_cdf_ends_at_one_and_monotonic() -> None:
    cdf = cdf_from_counts([1, 2, 3, 4])
    assert cdf[-1] == pytest.approx(1.0)
    assert np.all(np.diff(cdf) >= 0)


def test_cdf_empty_rejected() -> None:
    with pytest.raises(ValueError, match="vazias|nulas"):
        cdf_from_counts([])
    with pytest.raises(ValueError, match="vazias|nulas"):
        cdf_from_counts([0, 0, 0])


def test_histogram_with_cdf_keys() -> None:
    payload = histogram_with_cdf([1, 2, 2, 5], bins=4)
    assert payload["n"] == 4
    assert payload["bins"] == 4
    assert len(payload["counts"]) == 4
    assert len(payload["edges"]) == 5
    assert len(payload["cdf"]) == 4
    assert payload["cdf"][-1] == pytest.approx(1.0)
