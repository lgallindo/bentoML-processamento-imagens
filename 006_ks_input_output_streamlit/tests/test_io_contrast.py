"""Contraste sintético: entrada quieta, saída deslocada em alerta."""

from __future__ import annotations

from PIL import Image

from banner import alert_on_d
from grayscale_model import GrayscaleModel, GrayscaleShiftedModel
from histogram import DEFAULT_BINS, compute_histogram, cumulative_distribution
from image_extract import extract_image_features
from ks_compare import compare_stats, ks_statistic


def _stats_from_images(images: list[Image.Image]) -> dict:
    counts = [0] * DEFAULT_BINS
    for img in images:
        feat = extract_image_features(img)
        for i, v in enumerate(feat["histograms"]["L"]):
            counts[i] += int(v)
    return {
        "n_images": len(images),
        "histograms": {
            "luminance": {
                "channel": "L",
                "bins": DEFAULT_BINS,
                "counts": counts,
                "cdf": cumulative_distribution(counts),
            }
        },
    }


def test_shifted_output_alerts_while_input_quiet() -> None:
    # Mesmo padrão na entrada (D≈0); saída deslocada vs emissão saudável → ALERTA
    ref_imgs = [Image.new("RGB", (32, 32), (80, 80, 80)) for _ in range(10)]
    lote_imgs = [Image.new("RGB", (32, 32), (80, 80, 80)) for _ in range(10)]
    healthy = GrayscaleModel()
    shifted = GrayscaleShiftedModel(40)

    ref_in = _stats_from_images(ref_imgs)
    lote_in = _stats_from_images(lote_imgs)
    ref_out = _stats_from_images([healthy(i) for i in ref_imgs])
    lote_out_shifted = _stats_from_images([shifted(i) for i in lote_imgs])

    pin = compare_stats(ref_in, lote_in, channel="L")
    pout = compare_stats(ref_out, lote_out_shifted, channel="L")
    assert alert_on_d(
        pin["statistic"], pin["n_images_corpus"], pin["n_images_production"]
    ) == "QUIET"
    assert alert_on_d(
        pout["statistic"], pout["n_images_corpus"], pout["n_images_production"]
    ) == "ALERT"


def test_ks_on_identical_channels_is_zero() -> None:
    counts = compute_histogram(Image.new("L", (4, 4), 100))
    cdf = cumulative_distribution(counts)
    assert ks_statistic(cdf, cdf) == 0.0
