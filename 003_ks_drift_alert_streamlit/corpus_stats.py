"""Camada 2 — agrega features/*.json no freeze estatístico do corpus.

Lê apenas JSON já extraídos. Não abre imagens. Não serve HTTP.

Pré-condições:
  - features_dir com ≥ min_images arquivos JSON no formato de image_extract;
  - para load_default_corpus_stats, corpus_stats.json na pasta da aula.

Fluxo::

    features/*.json ──► rebin/acumula ──► histograms + brightness ──► JSON

Saídas principais: build_corpus_stats, load_default_corpus_stats.
"""

from __future__ import annotations

import json
from pathlib import Path

from histogram import DEFAULT_BINS, cumulative_distribution, rebin_counts
from image_extract import CHANNELS, FEATURES_DIR, list_feature_files, load_image_features

MIN_TRAINING_IMAGES = 8  # classroom freeze uses 12 beaches; alerta exige ≥8
CORPUS_STATS_PATH = Path("corpus_stats.json")
CHANNEL_KEYS = {"L": "luminance", "R": "r", "G": "g", "B": "b"}


def build_corpus_stats(
    features_dir: Path = FEATURES_DIR,
    *,
    min_images: int = MIN_TRAINING_IMAGES,
) -> dict:
    files = list_feature_files(features_dir)
    if len(files) < min_images:
        raise ValueError(
            f"são necessárias pelo menos {min_images} features; encontradas {len(files)}"
        )

    means: list[float] = []
    accumulators = {channel: [0] * DEFAULT_BINS for channel in CHANNELS}

    for path in files:
        feature = load_image_features(path)
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
        "brightness": {
            "mean": sum(means) / len(means),
            "p50": ordered[int(round(0.50 * (len(ordered) - 1)))],
            "p95": ordered[int(round(0.95 * (len(ordered) - 1)))],
        },
        "histograms": histograms,
    }


def write_corpus_stats(stats: dict, path: Path = CORPUS_STATS_PATH) -> Path:
    path.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    return path


def load_corpus_stats(path: Path = CORPUS_STATS_PATH) -> dict:
    if not path.is_file():
        raise FileNotFoundError(
            f"estatística de corpus ausente: {path} "
            "(rode just build-corpus-stats ou just build-demo-batches)"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def load_default_corpus_stats() -> dict:
    return load_corpus_stats(Path(__file__).resolve().parent / CORPUS_STATS_PATH)
