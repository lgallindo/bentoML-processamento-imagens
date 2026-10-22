from __future__ import annotations

import pytest
from PIL import Image

from request_log import log_grayscale_submission
from request_stats import build_request_stats


def test_build_request_stats_from_logs(tmp_path) -> None:
    for i in range(5):
        image = Image.new("RGB", (8, 8), (i * 20, 10, 30))
        log_grayscale_submission(image, features_dir=tmp_path)
    stats = build_request_stats(tmp_path, min_images=5)
    assert stats["n_images"] == 5
    assert stats["source"] == "request_features"
    assert stats["histograms"]["luminance"]["cdf"][-1] == pytest.approx(1.0)
