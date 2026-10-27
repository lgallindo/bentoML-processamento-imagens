from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image

from alert_rule import alert_on_d
from anomaly import (
    filter_paths_by_window,
    parse_feature_timestamp,
    score_image_vs_reference,
    window_alert,
)


def test_score_dark_vs_bright_reference() -> None:
    ref = [100] + [0] * 255  # só L=0
    dark = Image.new("L", (8, 8), 0)
    bright = Image.new("L", (8, 8), 255)
    d_dark = score_image_vs_reference(dark, ref)["statistic"]
    d_bright = score_image_vs_reference(bright, ref)["statistic"]
    assert d_dark == 0.0
    assert d_bright == 1.0


def test_alert_on_d() -> None:
    assert alert_on_d(0.15, 12) == "ALERT"
    assert alert_on_d(0.05, 12) == "QUIET"
    assert alert_on_d(0.5, 3) == "INCONCLUSIVE"
    assert window_alert(3, 0.5) == "INCONCLUSIVE"


def test_parse_and_window(tmp_path: Path) -> None:
    now = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc)
    fresh = tmp_path / "20261020T120000000000Z_a.json"
    old = tmp_path / "20260901T120000000000Z_b.json"
    fresh.write_text("{}")
    old.write_text("{}")
    assert parse_feature_timestamp(fresh) is not None
    kept = filter_paths_by_window([fresh, old], now=now, window_days=30)
    assert fresh in kept
    assert old not in kept
