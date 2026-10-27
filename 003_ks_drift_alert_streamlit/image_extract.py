"""Camada 1 — extrai L/R/G/B de UMA imagem e grava em features/.

Não é API HTTP. Nenhum endpoint deve expor isto ao cliente.

Pré-condições: path de imagem legível pelo Pillow.

Fluxo::

    foto ──► histogramas L/R/G/B + média L ──► features/<stem>.json

Saídas principais: extract_image_features, save_image_features, list_feature_files.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
from PIL.Image import Image as PILImage

from histogram import DEFAULT_BINS, compute_histogram

FEATURES_DIR = Path("features")
CHANNELS = ("L", "R", "G", "B")


def luminance_mean(image: PILImage, bins: int = DEFAULT_BINS) -> float:
    counts = compute_histogram(image, channel="L", bins=bins)
    total = sum(counts)
    return sum(i * count for i, count in enumerate(counts)) / total


def extract_image_features(image: PILImage, *, bins: int = DEFAULT_BINS) -> dict:
    """Dados por imagem: média de L + histogramas L/R/G/B."""
    return {
        "bins": bins,
        "luminance_mean": luminance_mean(image, bins=bins),
        "histograms": {
            channel: compute_histogram(image, channel=channel, bins=bins)
            for channel in CHANNELS
        },
    }


def feature_path_for(image_path: Path, features_dir: Path = FEATURES_DIR) -> Path:
    return features_dir / f"{image_path.stem}.json"


def save_image_features(
    image_path: Path,
    features_dir: Path = FEATURES_DIR,
    *,
    bins: int = DEFAULT_BINS,
) -> Path:
    with Image.open(image_path) as image:
        image.load()
        payload = extract_image_features(image, bins=bins)
    payload["source"] = str(image_path).replace("\\", "/")
    features_dir.mkdir(parents=True, exist_ok=True)
    out = feature_path_for(image_path, features_dir)
    out.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return out


def load_image_features(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def list_feature_files(features_dir: Path = FEATURES_DIR) -> list[Path]:
    return sorted(features_dir.glob("*.json"))
