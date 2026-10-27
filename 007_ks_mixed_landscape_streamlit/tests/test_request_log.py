from __future__ import annotations

from PIL import Image

from request_log import log_grayscale_submission


def test_log_grayscale_submission_writes_features(tmp_path) -> None:
    image = Image.new("RGB", (16, 16), (200, 50, 10))
    out = log_grayscale_submission(image, features_dir=tmp_path)
    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert "luminance_mean" in text
    assert "histograms" in text
    assert '"endpoint": "grayscale"' in text
    assert "logged_at" in text
