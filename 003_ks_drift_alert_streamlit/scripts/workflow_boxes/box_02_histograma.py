#!/usr/bin/env python3
"""Caixa 2 — histograma h: conta pixels por faixa de L.

Executa somente esta caixa (assume L já obtido via convert).

Uso::

    python scripts/workflow_boxes/box_02_histograma.py
"""

from __future__ import annotations

from PIL import Image


def histograma_h(image: Image.Image, bins: int = 256) -> list[int]:
    """Contagens por faixa de luminância.

    Com ``bins=256``, cada inteiro L∈{0…255} é um balde (histograma nativo
    do Pillow). Com ``bins`` menor, reagrupamos baldes consecutivos
    (mesmo espírito de ``histogram.rebin_counts`` na aula).

    Alternativas:
      - ``numpy.histogram`` sobre ``list(image.getdata())``;
      - densidades (frações) em vez de contagens — aí a CDF vira soma das
        densidades, equivalente se a normalização for consistente.
    """
    # Garante modo L sem depender da caixa 1 como import.
    cinza = image.convert("L")
    counts = list(cinza.histogram())  # sempre 256 baldes
    if bins == 256:
        return counts
    out = [0] * bins
    for i, value in enumerate(counts):
        out[min(bins - 1, (i * bins) // 256)] += int(value)
    return out


def main() -> int:
    rgb = Image.new("RGB", (8, 8), (10, 10, 10))
    h = histograma_h(rgb, bins=16)
    assert len(h) == 16
    assert sum(h) == 8 * 8
    print(f"bins={len(h)} total_pixels={sum(h)} h={h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
