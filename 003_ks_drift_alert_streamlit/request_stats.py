"""Agrega request_features/ (log de /inference-grayscale) em estatística de lote.

Pré-condições:
  - features_dir com ≥ min_images JSON no formato do request_log;
  - path de load_request_stats deve existir.

Fluxo::

    request_features/*.json ──► acumula ──► histograms + n_images ──► dict/JSON

Saídas principais: build_request_stats, load_request_stats.
"""

from __future__ import annotations

import json
from pathlib import Path

from histogram import DEFAULT_BINS, cumulative_distribution, rebin_counts
from image_extract import CHANNELS
from request_log import REQUEST_FEATURES_DIR

MIN_REQUEST_IMAGES = 1
REQUEST_STATS_PATH = Path("request_stats.json")
CHANNEL_KEYS = {"L": "luminance", "R": "r", "G": "g", "B": "b"}


def list_request_feature_files(features_dir: Path = REQUEST_FEATURES_DIR) -> list[Path]:
    return sorted(features_dir.glob("*.json"))


def build_request_stats(
    features_dir: Path = REQUEST_FEATURES_DIR,
    *,
    min_images: int = MIN_REQUEST_IMAGES,
) -> dict:
    files = list_request_feature_files(features_dir)
    if len(files) < min_images:
        raise ValueError(
            f"são necessárias pelo menos {min_images} features de pedido; "
            f"encontradas {len(files)}"
        )

    means: list[float] = []
    accumulators = {channel: [0] * DEFAULT_BINS for channel in CHANNELS}

    for path in files:
        feature = json.loads(path.read_text(encoding="utf-8"))
        means.append(float(feature["luminance_mean"]))
        for channel in CHANNELS:
            counts = rebin_counts(feature["histograms"][channel], DEFAULT_BINS)
            bucket = accumulators[channel]
            for i, value in enumerate(counts):
                bucket[i] += value

    ordered = sorted(means)
    histograms = {}
    for channel, key in CHANNEL_KEYS.items():
        counts = accumulators[channel]
        histograms[key] = {
            "channel": channel,
            "bins": DEFAULT_BINS,
            "counts": counts,
            "cdf": cumulative_distribution(counts),
        }

    return {
        "n_images": len(files),
        "source": "request_features",
        "brightness": {
            "mean": sum(means) / len(means),
            "p50": ordered[int(round(0.50 * (len(ordered) - 1)))],
            "p95": ordered[int(round(0.95 * (len(ordered) - 1)))],
        },
        "histograms": histograms,
    }


def write_request_stats(stats: dict, path: Path = REQUEST_STATS_PATH) -> Path:
    path.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    return path


def load_request_stats(path: Path = REQUEST_STATS_PATH) -> dict:
    if not path.is_file():
        raise FileNotFoundError(
            f"estatística de lote ausente: {path} "
            "(grave pedidos via just serve + exercise-theme, ou use batch_stats/)"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def load_default_request_stats() -> dict:
    return load_request_stats(Path(__file__).resolve().parent / REQUEST_STATS_PATH)
