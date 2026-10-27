"""Log offline das features de entrada e de saída em /inference-grayscale*."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from PIL.Image import Image as PILImage

from image_extract import extract_image_features

REQUEST_FEATURES_INPUT_DIR = Path("request_features_input")
REQUEST_FEATURES_OUTPUT_DIR = Path("request_features_output")
# Alias para request_stats legado / scripts que esperam um único dir
REQUEST_FEATURES_DIR = REQUEST_FEATURES_INPUT_DIR


def _write_feature(
    image: PILImage,
    *,
    features_dir: Path,
    endpoint: str,
    side: str,
    pair_id: str,
) -> Path:
    payload = extract_image_features(image)
    payload["logged_at"] = datetime.now(timezone.utc).isoformat()
    payload["endpoint"] = endpoint
    payload["side"] = side
    payload["pair_id"] = pair_id
    features_dir.mkdir(parents=True, exist_ok=True)
    name = (
        f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}_"
        f"{uuid4().hex[:8]}.json"
    )
    out = features_dir / name
    out.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return out


def log_grayscale_pair(
    image_in: PILImage,
    image_out: PILImage,
    *,
    endpoint: str,
    input_dir: Path = REQUEST_FEATURES_INPUT_DIR,
    output_dir: Path = REQUEST_FEATURES_OUTPUT_DIR,
    pair_id: str | None = None,
) -> tuple[Path, Path]:
    """Grava um par entrada/saída com o mesmo pair_id."""
    pid = pair_id or uuid4().hex
    path_in = _write_feature(
        image_in,
        features_dir=input_dir,
        endpoint=endpoint,
        side="input",
        pair_id=pid,
    )
    path_out = _write_feature(
        image_out,
        features_dir=output_dir,
        endpoint=endpoint,
        side="output",
        pair_id=pid,
    )
    return path_in, path_out
