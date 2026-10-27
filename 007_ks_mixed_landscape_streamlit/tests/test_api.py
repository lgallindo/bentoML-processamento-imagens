from __future__ import annotations

import io
from pathlib import Path

import pytest
from PIL import Image
from starlette.testclient import TestClient

from grayscale_model import save_grayscale_model


@pytest.fixture(scope="module")
def ensure_model() -> None:
    save_grayscale_model()


@pytest.fixture(scope="module")
def asgi_client(ensure_model) -> TestClient:
    import service as service_module

    app = service_module.ImageProcessor.to_asgi()
    with TestClient(app) as client:
        yield client


def _png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (16, 16), (40, 80, 120)).save(buf, format="PNG")
    return buf.getvalue()


def test_inference_grayscale_ok(asgi_client: TestClient) -> None:
    response = asgi_client.post(
        "/inference-grayscale",
        files={"image": ("x.png", _png_bytes(), "image/png")},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")


def test_inference_grayscale_writes_log(
    asgi_client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "request_features").mkdir()
    response = asgi_client.post(
        "/inference-grayscale",
        files={"image": ("x.png", _png_bytes(), "image/png")},
    )
    assert response.status_code == 200
    logged = list((tmp_path / "request_features").glob("*.json"))
    assert len(logged) >= 1


def test_no_monitor_ks_route(asgi_client: TestClient) -> None:
    response = asgi_client.post("/monitor-ks-production-corpus-json", data={})
    assert response.status_code == 404
