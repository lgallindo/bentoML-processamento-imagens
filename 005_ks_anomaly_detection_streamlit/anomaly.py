"""Detecção de anomalia: uma imagem (ou janela) vs referência via KS em L."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image

from histogram import DEFAULT_BINS, compute_histogram, cumulative_distribution, rebin_counts
from ks_compare import ks_statistic

# Alerta centrado em D (mesma filosofia da aula 003).
D_ALERT = 0.10
MIN_WINDOW_IMAGES = 8
DEFAULT_WINDOW_DAYS = 30


def histogram_l(image: Image.Image, bins: int = DEFAULT_BINS) -> list[int]:
    return compute_histogram(image, channel="L", bins=bins)


def score_counts_vs_reference(
    candidate_counts: Sequence[int],
    reference_counts: Sequence[int],
    *,
    bins: int = DEFAULT_BINS,
) -> dict:
    """D entre histograma do candidato e o da referência (mesmo número de faixas)."""
    ref = rebin_counts(reference_counts, bins)
    cand = rebin_counts(candidate_counts, bins)
    f_ref = cumulative_distribution(ref)
    f_cand = cumulative_distribution(cand)
    d = ks_statistic(f_ref, f_cand)
    return {
        "statistic": d,
        "bins": bins,
        "cdf_reference": f_ref,
        "cdf_candidate": f_cand,
        "counts_reference": ref,
        "counts_candidate": cand,
        "alert": "ALERT" if d >= D_ALERT else "QUIET",
    }


def score_image_vs_reference(
    image: Image.Image,
    reference_counts: Sequence[int],
    *,
    bins: int = DEFAULT_BINS,
) -> dict:
    return score_counts_vs_reference(histogram_l(image, bins=bins), reference_counts, bins=bins)


def score_path_vs_reference(
    path: Path,
    reference_counts: Sequence[int],
    *,
    bins: int = DEFAULT_BINS,
) -> dict:
    with Image.open(path) as im:
        payload = score_image_vs_reference(im, reference_counts, bins=bins)
    payload["path"] = str(path)
    return payload


def parse_feature_timestamp(path: Path) -> datetime | None:
    """Nomes típicos: 20261022T132711846833Z_….json → instante UTC."""
    stem = path.stem
    head = stem.split("_", 1)[0]
    if len(head) < 16 or head[8] != "T":
        return None
    try:
        # 20261022T132711846833Z → date + time to seconds
        date_part = head[:8]
        time_part = head[9:15]
        return datetime.strptime(date_part + time_part, "%Y%m%d%H%M%S").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        return None


def filter_paths_by_window(
    paths: Sequence[Path],
    *,
    now: datetime | None = None,
    window_days: int = DEFAULT_WINDOW_DAYS,
) -> list[Path]:
    """Time boxing: só arquivos cujo timestamp no nome cai nos últimos `window_days`."""
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=window_days)
    kept: list[Path] = []
    for path in paths:
        ts = parse_feature_timestamp(path)
        if ts is None or ts >= cutoff:
            kept.append(path)
    return kept


def pool_histograms_from_feature_files(
    paths: Sequence[Path],
    *,
    bins: int = DEFAULT_BINS,
) -> list[int]:
    """Soma histogramas L gravados em JSON de request_features/features."""
    import json

    acc = [0] * bins
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        hist = data.get("histograms", {}).get("L") or data.get("histograms", {}).get(
            "luminance"
        )
        if hist is None:
            continue
        for i, value in enumerate(rebin_counts(hist, bins)):
            acc[i] += int(value)
    return acc


def window_alert(
    n_images: int,
    statistic: float,
    *,
    min_images: int = MIN_WINDOW_IMAGES,
    d_threshold: float = D_ALERT,
) -> str:
    if n_images < min_images:
        return "INCONCLUSIVE"
    if statistic >= d_threshold:
        return "ALERT"
    return "QUIET"
