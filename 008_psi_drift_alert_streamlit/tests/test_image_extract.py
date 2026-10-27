from __future__ import annotations

from PIL import Image

from image_extract import extract_image_features, save_image_features


def test_extract_image_features_shape() -> None:
    image = Image.new("RGB", (4, 4), (10, 20, 30))
    payload = extract_image_features(image, bins=256)
    assert "luminance_mean" in payload
    assert set(payload["histograms"]) == {"L", "R", "G", "B"}
    assert len(payload["histograms"]["L"]) == 256


def test_save_image_features_roundtrip(tmp_path) -> None:
    image_path = tmp_path / "train_001.jpg"
    Image.new("RGB", (8, 8), (1, 2, 3)).save(image_path, format="JPEG")
    features_dir = tmp_path / "features"
    out = save_image_features(image_path, features_dir)
    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert "luminance_mean" in text
    assert "histograms" in text
