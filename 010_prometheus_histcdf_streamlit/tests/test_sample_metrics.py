"""Contratos dos dados sintéticos usados no laboratório de PromQL."""

from __future__ import annotations

import pytest

from scripts.serve_sample_metrics import (
    BUCKETS,
    DURATION,
    OBSERVATIONS,
    histogram,
    phase_seconds,
    render_metrics,
)


@pytest.mark.parametrize(
    ("elapsed", "expected"),
    [(0, (0, 0)), (120, (120, 0)), (180, (120, 60)),
     (240, (120, 120)), (360, (240, 120)), (540, (360, 180))],
)
def test_phase_accumulation(elapsed, expected):
    assert phase_seconds(elapsed) == expected


@pytest.mark.parametrize("endpoint", OBSERVATIONS)
def test_cumulative_histogram_preserves_all_observations(endpoint):
    values = histogram(360, endpoint)
    assert len(values["cumulative"]) == len(BUCKETS)
    assert values["cumulative"] == sorted(values["cumulative"])
    assert values["cumulative"][-1] == values["count"] == 360 * len(OBSERVATIONS[endpoint])
    assert values["sum"] == pytest.approx(sum(OBSERVATIONS[endpoint]) * (240 + 1200))


def test_stable_grayscale_matches_known_distribution_per_second():
    values = histogram(1, "/inference-grayscale")
    assert values["cumulative"] == [2, 5, 12, 18, 20, 20, 20, 20, 20]
    assert values["sum"] == pytest.approx(0.572)


def test_slow_phase_changes_latency_without_changing_request_rate():
    before = histogram(120, "/inference-grayscale")
    during = histogram(180, "/inference-grayscale")
    assert (during["count"] - before["count"]) / 60 == 20
    assert (during["sum"] - before["sum"]) / 60 == pytest.approx(5.72)
    # Só 2/20 observações lentas ficam até 0,05 s; normalmente são 18/20.
    assert during["cumulative"][3] - before["cumulative"][3] == 60 * 2


def test_snapshot_is_independent_of_collection_frequency():
    sparse = render_metrics(350)
    for elapsed in range(350):
        render_metrics(elapsed)
    assert render_metrics(350) == sparse
    earlier = histogram(240, "/inference-blur")
    later = histogram(360, "/inference-blur")
    assert all(new >= old for old, new in zip(earlier["cumulative"], later["cumulative"]))


def test_exposition_has_types_and_a_complete_histogram_for_every_endpoint():
    text = render_metrics(180)
    assert text.endswith("\n")
    assert f"# TYPE {DURATION} histogram\n" in text
    assert "aula004_demo_phase 1\n" in text
    for endpoint, observations in OBSERVATIONS.items():
        total = 180 * len(observations)
        assert f'{DURATION}_bucket{{endpoint="{endpoint}",le="+Inf"}} {total}\n' in text
        assert f'{DURATION}_count{{endpoint="{endpoint}"}} {total}\n' in text


def test_phase_duration_changes_schedule_not_observations_per_second():
    assert phase_seconds(15, duration=10) == (10, 5)
    assert "aula004_demo_phase 1\n" in render_metrics(15, duration=10)
    assert histogram(15, "/inference-resize", duration=10)["count"] == 75
