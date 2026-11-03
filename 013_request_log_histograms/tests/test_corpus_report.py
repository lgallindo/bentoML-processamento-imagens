from __future__ import annotations

import pytest
from PIL import Image

from corpus_report import report_histogram_csv, report_histogram_image, report_histogram_json
from corpus_stats import MIN_TRAINING_IMAGES, build_corpus_stats
from image_extract import save_image_features


@pytest.fixture
def corpus_stats(tmp_path):
    features_dir = tmp_path / "features"
    for i in range(MIN_TRAINING_IMAGES):
        image_path = tmp_path / f"train_{i:03d}.jpg"
        Image.new("RGB", (8, 8), (i % 256, 10, 20)).save(image_path, format="JPEG")
        save_image_features(image_path, features_dir)
    return build_corpus_stats(features_dir)


def test_report_json_has_cdf(corpus_stats) -> None:
    payload = report_histogram_json(channel="L", bins=64, stats=corpus_stats)
    assert payload["bins"] == 64
    assert len(payload["counts"]) == 64
    assert payload["cdf"][-1] == pytest.approx(1.0)
    assert "n_images" in payload


def test_report_csv_header(corpus_stats) -> None:
    text = report_histogram_csv(channel="R", bins=16, stats=corpus_stats)
    assert text.startswith("bin,count,cdf\n")
    assert len(text.strip().splitlines()) == 17


def test_report_image_size(corpus_stats) -> None:
    image = report_histogram_image(channel="G", bins=32, width=200, height=100, stats=corpus_stats)
    assert image.size == (200, 100)
