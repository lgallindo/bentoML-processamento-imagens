from __future__ import annotations

from promql_compare import build_histogram_quantile_promql, compare_quantiles


def test_promql_string_snapshot() -> None:
    expr = build_histogram_quantile_promql(0.95, endpoint="/grayscale")
    assert expr == (
        'histogram_quantile(0.95, sum by (le) '
        '(bentoml_service_request_duration_seconds_bucket{endpoint="/grayscale"}))'
    )


def test_compare_payload_with_both_sides() -> None:
    les = [0.05, 0.1, float("inf")]
    cum = [18, 20, 20]
    payload = compare_quantiles(
        les,
        cum,
        q=0.95,
        endpoint="/grayscale",
        promql_value=0.075,
        promql_available=True,
    )
    assert payload["promql_available"] is True
    assert payload["python"]["value"] is not None
    assert payload["delta_abs"] is not None
    assert payload["promql_expr"] == build_histogram_quantile_promql(0.95, endpoint="/grayscale")
    assert "histogram_quantile" in payload["python_source"] or "rank" in payload["python_source"]


def test_compare_marks_promql_unavailable() -> None:
    payload = compare_quantiles(
        [0.1, 1.0],
        [5, 10],
        q=0.5,
        promql_available=False,
        promql_value=None,
    )
    assert payload["promql_available"] is False
    assert payload["promql_value"] is None
    assert payload["delta_abs"] is None
    assert "histogram_quantile" in payload["promql_expr"]
