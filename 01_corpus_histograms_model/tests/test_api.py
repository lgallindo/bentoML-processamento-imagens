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
def asgi_client(ensure_model, ensure_corpus) -> TestClient:
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
    assert "per_image_means" not in body.get("brightness", {})


def test_training_histograms_csv(asgi_client: TestClient) -> None:
    response = asgi_client.post("/monitor-histogram-corpus-csv", data={"channel": "L", "bins": "32"})
    assert response.status_code == 200
    assert response.text.startswith("bin,count,cdf")


def test_training_histogram_image(asgi_client: TestClient) -> None:
    response = asgi_client.post(
        "/monitor-histogram-corpus-image",
        data={"channel": "L", "bins": "64", "width": "200", "height": "100"},
    )
    assert response.status_code == 200
    image = Image.open(io.BytesIO(response.content))
    assert image.size == (200, 100)


def test_grayscale_matches_pillow(asgi_client: TestClient) -> None:
    image = Image.new("RGB", (12, 12), (200, 100, 50))
    expected = image.convert("L")
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    response = asgi_client.post(
        "/inference-grayscale",
        files={"image": ("x.png", buf.getvalue(), "image/png")},
    )
    assert response.status_code == 200
    got = Image.open(io.BytesIO(response.content))
    assert got.mode == "L"
    assert list(got.getdata()) == list(expected.getdata())
