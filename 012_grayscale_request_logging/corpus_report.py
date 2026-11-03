"""Camada 3 — relatórios do corpus para as APIs (JSON, CSV, imagem).

Só lê `corpus_stats.json`. Não extrai imagem avulsa. Não agrega de novo.
"""

from __future__ import annotations

import csv
import io

from PIL.Image import Image as PILImage

from corpus_stats import CHANNEL_KEYS, load_default_corpus_stats
from histogram import DEFAULT_BINS, cumulative_distribution, draw_histogram, rebin_counts


def report_histogram_json(
    channel: str = "L",
    bins: int = DEFAULT_BINS,
    *,
    stats: dict | None = None,
) -> dict:
    stats = stats if stats is not None else load_default_corpus_stats()
    key = CHANNEL_KEYS[channel]
    counts = rebin_counts(stats["histograms"][key]["counts"], bins)
    return {
        "n_images": stats["n_images"],
        "brightness": stats["brightness"],
        "channel": channel,
        "bins": bins,
        "counts": counts,
        "cdf": cumulative_distribution(counts),
    }


def report_histogram_csv(
    channel: str = "L",
    bins: int = DEFAULT_BINS,
    *,
    stats: dict | None = None,
) -> str:
    payload = report_histogram_json(channel=channel, bins=bins, stats=stats)
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["bin", "count", "cdf"])
    for i, (count, cdf) in enumerate(zip(payload["counts"], payload["cdf"], strict=True)):
        writer.writerow([i, count, cdf])
    return buf.getvalue()


def report_histogram_image(
    channel: str = "L",
    bins: int = DEFAULT_BINS,
    *,
    width: int = 640,
    height: int = 360,
    include_cdf: bool = True,
    stats: dict | None = None,
) -> PILImage:
    payload = report_histogram_json(channel=channel, bins=bins, stats=stats)
    return draw_histogram(
        payload["counts"],
        cdf=payload["cdf"] if include_cdf else None,
        width=width,
        height=height,
    )
