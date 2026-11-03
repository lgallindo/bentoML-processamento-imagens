from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from prom_client import (
    INFERENCE_ENDPOINTS,
    PromClientError,
    endpoint_selector,
    fetch_duration_buckets,
    fetch_duration_buckets_from_fixture,
    normalize_bucket_result,
    query_instant,
)
from prom_hist import payload_from_samples
from promql_compare import live_compare

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "duration_histogram.json"


def test_fixture_loads_without_network() -> None:
    samples = fetch_duration_buckets_from_fixture(endpoint="/inference-grayscale")
    assert samples
    assert all(s["labels"]["endpoint"] == "/inference-grayscale" for s in samples)
    assert any(s["le"] == float("inf") for s in samples)


def test_normalize_filters_endpoint() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    samples = normalize_bucket_result(payload, endpoint="/inference-blur")
    assert samples
    assert all(s["labels"]["endpoint"] == "/inference-blur" for s in samples)


def test_query_instant_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*_a, **_k):
        raise httpx.ConnectError("refused")

    monkeypatch.setattr("prom_client.httpx.get", boom)
    with pytest.raises(PromClientError, match="inacessível"):
        query_instant("up", base_url="http://127.0.0.1:9")


def test_query_instant_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResp:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"status": "success", "data": {"resultType": "vector", "result": []}}

    monkeypatch.setattr("prom_client.httpx.get", lambda *a, **k: FakeResp())
    payload = query_instant("up")
    assert payload["status"] == "success"


def test_live_comparison_uses_one_evaluation_time(monkeypatch: pytest.MonkeyPatch) -> None:
    requests = []
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def get(url, *, params, timeout):
        requests.append(params)
        response = fixture
        if params["query"].startswith("histogram_quantile"):
            response = {
                "status": "success",
                "data": {
                    "resultType": "vector",
                    "result": [{"metric": {}, "value": [1729600000, "0.075"]}],
                },
            }
        return httpx.Response(200, json=response, request=httpx.Request("GET", url))

    monkeypatch.setattr("prom_client.httpx.get", get)
    timestamp = 1729600000.0
    samples = fetch_duration_buckets(evaluation_time=timestamp)
    histogram = payload_from_samples(samples)
    comparison = live_compare(
        histogram["les"], histogram["cumulative"], evaluation_time=timestamp
    )
    assert len(requests) == 2
    assert all(params["time"] == timestamp for params in requests)
    assert all('job="bentoml-imagens"' in params["query"] for params in requests)
    assert all('endpoint="/inference-grayscale"' in params["query"] for params in requests)
    assert comparison["delta_abs"] == pytest.approx(0)


def test_route_selection_matches_service_contract() -> None:
    assert set(INFERENCE_ENDPOINTS) == {
        "/inference-blur", "/inference-grayscale", "/inference-resize"
    }
    assert endpoint_selector(None) == (
        'job="bentoml-imagens",endpoint=~"/inference-(blur|grayscale|resize)"'
    )
