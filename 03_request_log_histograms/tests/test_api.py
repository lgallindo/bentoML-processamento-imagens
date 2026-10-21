from __future__ import annotations

import io
from pathlib import Path

import pytest
from PIL import Image
from starlette.testclient import TestClient

from corpus_stats import (
    CORPUS_STATS_PATH,
    MIN_TRAINING_IMAGES,
    build_corpus_stats,
    write_corpus_stats,
)
from grayscale_model import save_grayscale_model
from image_extract import FEATURES_DIR, save_image_features
from request_log import REQUEST_FEATURES_DIR, log_grayscale_submission
from request_stats import REQUEST_STATS_PATH, build_request_stats, write_request_stats


@pytest.fixture(scope="module")
def ensure_model() -> None:
    save_grayscale_model()


@pytest.fixture(scope="module")
def ensure_corpus() -> None:
    root = Path(__file__).resolve().parent.parent
    features_dir = root / FEATURES_DIR
    samples = root / "samples"
    existing = sorted(samples.glob("train_*"))
    if len(existing) >= MIN_TRAINING_IMAGES:
        if len(list(features_dir.glob("*.json"))) < MIN_TRAINING_IMAGES:
            features_dir.mkdir(parents=True, exist_ok=True)
            for path in existing:
                save_image_features(path, features_dir)
        stats = build_corpus_stats(features_dir)
    else:
        tmp = root / ".pytest_train_fixtures"
        tmp.mkdir(exist_ok=True)
        features_dir = tmp / "features"
        for i in range(MIN_TRAINING_IMAGES):
            path = tmp / f"train_{i:03d}.jpg"
            if not path.is_file():
                Image.new("RGB", (8, 8), (i % 256, 10, 20)).save(path, format="JPEG")
            save_image_features(path, features_dir)
        stats = build_corpus_stats(features_dir)
    write_corpus_stats(stats, root / CORPUS_STATS_PATH)


@pytest.fixture(scope="module")
def ensure_request_stats() -> None:
    root = Path(__file__).resolve().parent.parent
    log_dir = root / REQUEST_FEATURES_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    if len(list(log_dir.glob("*.json"))) < 3:
        for i in range(5):
            log_grayscale_submission(
                Image.new("RGB", (8, 8), (i * 30, 20, 40)),
                features_dir=log_dir,
            )
    stats = build_request_stats(log_dir)
    write_request_stats(stats, root / REQUEST_STATS_PATH)


@pytest.fixture(scope="module")
def asgi_client(ensure_model, ensure_corpus, ensure_request_stats) -> TestClient:
    import service as service_module

    app = service_module.ImageProcessor.to_asgi()
    with TestClient(app) as client:
        yield client


def test_training_histograms_json(asgi_client: TestClient) -> None:
    response = asgi_client.post("/monitor-histogram-corpus-json", data={"channel": "L", "bins": "256"})
    assert response.status_code == 200
    body = response.json()
    assert body["n_images"] >= MIN_TRAINING_IMAGES
    assert "counts" in body and "cdf" in body


def test_request_histograms_json(asgi_client: TestClient) -> None:
    response = asgi_client.post("/monitor-histogram-production-json", data={"channel": "L", "bins": "256"})
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "request_features"
    assert body["n_images"] >= 1
    assert "cdf" in body


def test_request_histograms_csv(asgi_client: TestClient) -> None:
    response = asgi_client.post("/monitor-histogram-production-csv", data={"channel": "R", "bins": "16"})
    assert response.status_code == 200
    assert response.text.startswith("bin,count,cdf")


def test_request_histogram_image(asgi_client: TestClient) -> None:
    response = asgi_client.post(
        "/monitor-histogram-production-image",
        data={"channel": "L", "bins": "32", "width": "180", "height": "90"},
    )
    assert response.status_code == 200
    image = Image.open(io.BytesIO(response.content))
    assert image.size == (180, 90)


def test_grayscale_logs(asgi_client: TestClient) -> None:
    root = Path(__file__).resolve().parent.parent
    log_dir = root / REQUEST_FEATURES_DIR
    before = set(log_dir.glob("*.json"))
    buf = io.BytesIO()
    Image.new("RGB", (12, 12), (1, 2, 3)).save(buf, format="PNG")
    response = asgi_client.post(
        "/inference-grayscale",
        files={"image": ("x.png", buf.getvalue(), "image/png")},
    )
    assert response.status_code == 200
    assert len(set(log_dir.glob("*.json")) - before) >= 1
