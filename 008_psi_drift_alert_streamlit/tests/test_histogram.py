from __future__ import annotations

import pytest
from PIL import Image

from histogram import (
    compute_histogram,
    cumulative_distribution,
    draw_histogram,
    histogram_with_cdf,
)


def test_compute_histogram_sums_to_pixels() -> None:
    image = Image.new("RGB", (10, 5), (255, 0, 0))
    assert sum(compute_histogram(image, channel="R", bins=256)) == 50
    assert sum(compute_histogram(image, channel="L", bins=64)) == 50


def test_cdf_ends_at_one() -> None:
    cdf = cumulative_distribution([1, 2, 3, 4])
    assert cdf[-1] == pytest.approx(1.0)
    assert cdf == sorted(cdf)


def test_histogram_with_cdf_keys() -> None:
    image = Image.new("RGB", (8, 8), (20, 40, 60))
    payload = histogram_with_cdf(image, channel="B", bins=32)
    assert payload["bins"] == 32
    assert len(payload["counts"]) == 32
    assert len(payload["cdf"]) == 32


def test_draw_histogram_size() -> None:
    counts = [0, 1, 5, 2, 0]
    image = draw_histogram(counts, cdf=cumulative_distribution(counts), width=320, height=180)
    assert image.size == (320, 180)
