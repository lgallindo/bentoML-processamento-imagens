from __future__ import annotations

import pytest
from PIL import Image

from corpus_stats import MIN_TRAINING_IMAGES, build_corpus_stats
from image_extract import save_image_features


def _write_features(tmp_path, n: int):
    features_dir = tmp_path / "features"
    for i in range(n):
        image_path = tmp_path / f"train_{i:03d}.jpg"
        Image.new("RGB", (8, 8), (i % 256, 40, 80)).save(image_path, format="JPEG")
        save_image_features(image_path, features_dir)
    return features_dir


def test_build_corpus_stats_requires_minimum(tmp_path) -> None:
    features_dir = _write_features(tmp_path, 3)
    with pytest.raises(ValueError, match="pelo menos"):
        build_corpus_stats(features_dir)


def test_build_corpus_stats_aggregates(tmp_path) -> None:
    features_dir = _write_features(tmp_path, MIN_TRAINING_IMAGES)
    stats = build_corpus_stats(features_dir)
    assert stats["n_images"] == MIN_TRAINING_IMAGES
    assert "per_image_means" not in stats.get("brightness", {})
    lum = stats["histograms"]["luminance"]
    assert len(lum["counts"]) == 256
    assert lum["cdf"][-1] == pytest.approx(1.0)
