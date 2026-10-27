from __future__ import annotations

from matplotlib.figure import Figure

from plotting import plot_histogram_cdf


def test_plot_returns_figure() -> None:
    fig = plot_histogram_cdf([2, 3, 5], [0.0, 0.01, 0.05, 0.1], [0.2, 0.5, 1.0])
    assert isinstance(fig, Figure)
