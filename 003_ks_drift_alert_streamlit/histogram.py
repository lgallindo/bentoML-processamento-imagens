"""Histograma e CDF de um canal de imagem (L/R/G/B) com Pillow.

Converte a imagem, conta pixels por faixa e acumula a CDF usada pelo KS.

Pré-condições:
  - imagem Pillow carregável; canal em {L, R, G, B};
  - bins ≥ 1.

Fluxo::

    imagem ──► extract_channel ──► histogram ──► rebin? ──► CDF

Saídas principais: compute_histogram, cumulative_distribution, draw helpers.
"""

from __future__ import annotations

from collections.abc import Sequence

from PIL import Image, ImageDraw
from PIL.Image import Image as PILImage

DEFAULT_BINS = 256
CHANNEL_INDEX = {"L": None, "R": 0, "G": 1, "B": 2}


def extract_channel(image: PILImage, channel: str) -> PILImage:
    """Devolve um canal em modo L (`L`/`R`/`G`/`B`)."""
    if channel == "L":
        return image.convert("L")
    rgb = image.convert("RGB")
    return rgb.getchannel(CHANNEL_INDEX[channel])


def rebin_counts(counts: Sequence[int], bins: int) -> list[int]:
    """Reagrupa contagens para um número arbitrário de bins."""
    source = list(counts)
    source_bins = len(source)
    if bins == source_bins:
        return source
    out = [0] * bins
    for i, value in enumerate(source):
        out[min(bins - 1, (i * bins) // source_bins)] += int(value)
    return out


def compute_histogram(
    image: PILImage,
    channel: str = "L",
    bins: int = DEFAULT_BINS,
) -> list[int]:
    """Histograma de um canal; `bins` controla a resolução."""
    counts = list(extract_channel(image, channel).histogram())
    return rebin_counts(counts, bins)


def cumulative_distribution(counts: Sequence[int]) -> list[float]:
    """CDF normalizada em [0, 1] a partir das contagens do histograma."""
    total = sum(counts)
    running = 0
    cdf: list[float] = []
    for value in counts:
        running += int(value)
        cdf.append(running / total)
    return cdf


def histogram_with_cdf(
    image: PILImage,
    channel: str = "L",
    bins: int = DEFAULT_BINS,
) -> dict:
    """Pacote didático: contagens + CDF para os mesmos parâmetros."""
    counts = compute_histogram(image, channel=channel, bins=bins)
    return {
        "channel": channel,
        "bins": bins,
        "counts": counts,
        "cdf": cumulative_distribution(counts),
    }


def draw_histogram(
    counts: Sequence[int],
    *,
    cdf: Sequence[float] | None = None,
    width: int = 640,
    height: int = 360,
    bar_color: tuple[int, int, int] = (40, 40, 40),
    cdf_color: tuple[int, int, int] = (200, 40, 40),
    background: tuple[int, int, int] = (245, 245, 245),
) -> PILImage:
    """Desenha barras do histograma e, se dado, a curva da CDF."""
    image = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(image)
    n = len(counts)
    peak = max(counts)
    margin = 8
    plot_w = width - 2 * margin
    plot_h = height - 2 * margin

    for i, value in enumerate(counts):
        x0 = margin + (i * plot_w) // n
        x1 = margin + ((i + 1) * plot_w) // n
        bar_h = 0 if peak == 0 else int((value / peak) * (plot_h - 1))
        y1 = margin + plot_h
        y0 = y1 - bar_h
        draw.rectangle([x0, y0, max(x0, x1 - 1), y1], fill=bar_color)

    if cdf is not None:
        points: list[tuple[int, int]] = []
        for i, value in enumerate(cdf):
            x = margin + (i * plot_w) // max(1, len(cdf) - 1) if len(cdf) > 1 else margin
            y = margin + plot_h - int(value * (plot_h - 1))
            points.append((x, y))
        if len(points) >= 2:
            draw.line(points, fill=cdf_color, width=2)

    return image
