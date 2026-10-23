from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from prom_client import (
    PromClientError,
    fetch_duration_buckets_from_fixture,
    normalize_bucket_result,
    query_instant,
)

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "duration_histogram.json"


def test_fixture_loads_without_network() -> None:
    samples = fetch_duration_buckets_from_fixture(endpoint="/grayscale")
    assert samples
    assert all(s["labels"]["endpoint"] == "/grayscale" for s in samples)
    assert any(s["le"] == float("inf") for s in samples)


def test_normalize_filters_endpoint() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    samples = normalize_bucket_result(payload, endpoint="/blur")
    assert samples
    assert all(s["labels"]["endpoint"] == "/blur" for s in samples)


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
