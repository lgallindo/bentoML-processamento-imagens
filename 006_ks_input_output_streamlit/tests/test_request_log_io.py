from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from request_log import log_grayscale_pair


def test_log_pair_shares_pair_id(tmp_path: Path) -> None:
    img_in = Image.new("RGB", (8, 8), (20, 40, 60))
    img_out = img_in.convert("L")
    din = tmp_path / "in"
    dout = tmp_path / "out"
    path_in, path_out = log_grayscale_pair(
        img_in,
        img_out,
        endpoint="grayscale",
        input_dir=din,
        output_dir=dout,
    )
    payload_in = json.loads(path_in.read_text(encoding="utf-8"))
    payload_out = json.loads(path_out.read_text(encoding="utf-8"))
    assert payload_in["side"] == "input"
    assert payload_out["side"] == "output"
    assert payload_in["pair_id"] == payload_out["pair_id"]
    assert payload_in["endpoint"] == "grayscale"
    assert "histograms" in payload_in and "L" in payload_in["histograms"]
