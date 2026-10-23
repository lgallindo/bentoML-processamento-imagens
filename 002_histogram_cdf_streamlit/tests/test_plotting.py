from __future__ import annotations

from histcdf import histogram_with_cdf
from plotting import plot_histogram_cdf


def test_plot_returns_figure() -> None:
    payload = histogram_with_cdf([1, 2, 2, 5], bins=4)
    fig = plot_histogram_cdf(payload["counts"], payload["edges"], payload["cdf"])
    assert fig is not None
    assert len(fig.axes) == 2
