"""Espelho offline do serviço: entrada → saída saudável / deslocada."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
from PIL.Image import Image as PILImage

from grayscale_model import SHIFT_DELTA, GrayscaleModel, GrayscaleShiftedModel
from image_extract import extract_image_features, save_image_features

_HEALTHY = GrayscaleModel()
_SHIFTED = GrayscaleShiftedModel(SHIFT_DELTA)


def apply_healthy(image: PILImage) -> PILImage:
    return _HEALTHY(image)


def apply_shifted(image: PILImage) -> PILImage:
    return _SHIFTED(image)


def extract_io_for_path(
    image_path: Path,
    *,
    input_dir: Path,
    output_dir: Path,
    shifted_dir: Path | None = None,
) -> dict[str, Path]:
    """Grava features de entrada, saída saudável e (opcional) saída deslocada."""
    with Image.open(image_path) as image:
        image.load()
        img_in = image.copy()
    out_healthy = apply_healthy(img_in)
    paths: dict[str, Path] = {}
    paths["input"] = save_image_features(image_path, input_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_payload = extract_image_features(out_healthy)
    out_payload["source"] = str(image_path).replace("\\", "/")
    out_payload["side"] = "output"
    out_payload["endpoint"] = "offline-grayscale"
    out_path = output_dir / f"{image_path.stem}.json"
    out_path.write_text(json.dumps(out_payload) + "\n", encoding="utf-8")
    paths["output"] = out_path
    if shifted_dir is not None:
        shifted_dir.mkdir(parents=True, exist_ok=True)
        out_shift = apply_shifted(img_in)
        shift_payload = extract_image_features(out_shift)
        shift_payload["source"] = str(image_path).replace("\\", "/")
        shift_payload["side"] = "output"
        shift_payload["endpoint"] = "offline-grayscale-shifted"
        shift_path = shifted_dir / f"{image_path.stem}.json"
        shift_path.write_text(json.dumps(shift_payload) + "\n", encoding="utf-8")
        paths["output_shifted"] = shift_path
    return paths
