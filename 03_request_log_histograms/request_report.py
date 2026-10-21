"""Relatórios do log de pedidos (JSON, CSV, imagem) — só lê request_stats.json."""

from __future__ import annotations

import csv
import io

from PIL.Image import Image as PILImage

from histogram import DEFAULT_BINS, cumulative_distribution, draw_histogram, rebin_counts
from request_stats import CHANNEL_KEYS, load_default_request_stats


def report_request_histogram_json(
    channel: str = "L",
    bins: int = DEFAULT_BINS,
    *,
    stats: dict | None = None,
) -> dict:
    stats = stats if stats is not None else load_default_request_stats()
    key = CHANNEL_KEYS[channel]
    counts = rebin_counts(stats["histograms"][key]["counts"], bins)
    return {
        "n_images": stats["n_images"],
        "source": stats.get("source", "request_features"),
        "brightness": stats["brightness"],
        "channel": channel,
        "bins": bins,
        "counts": counts,
        "cdf": cumulative_distribution(counts),
    }


def report_request_histogram_csv(
    channel: str = "L",
    bins: int = DEFAULT_BINS,
    *,
    stats: dict | None = None,
) -> str:
    payload = report_request_histogram_json(channel=channel, bins=bins, stats=stats)
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["bin", "count", "cdf"])
    for i, (count, cdf) in enumerate(zip(payload["counts"], payload["cdf"], strict=True)):
        writer.writerow([i, count, cdf])
    return buf.getvalue()


def report_request_histogram_image(
    channel: str = "L",
    bins: int = DEFAULT_BINS,
    *,
    width: int = 640,
    height: int = 360,
    include_cdf: bool = True,
    stats: dict | None = None,
) -> PILImage:
    payload = report_request_histogram_json(channel=channel, bins=bins, stats=stats)
    return draw_histogram(
        payload["counts"],
        cdf=payload["cdf"] if include_cdf else None,
        width=width,
        height=height,
    )
