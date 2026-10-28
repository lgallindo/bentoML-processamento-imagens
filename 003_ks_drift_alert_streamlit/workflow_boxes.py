"""Caixas de ``illustrations/01_workflow_l_to_alert.png`` → uma função cada.

Mapeamento (esquerda → direita)::

    L (pixel) → histograma h → CDF F → δ=|F−G| → D=max δ → alerta em D

Cada função é mínima, para exibição no README e no Streamlit; a lógica de
produção vive em ``histogram``, ``ks_compare`` e ``alert_rule``.
"""

from __future__ import annotations

from collections.abc import Sequence

from PIL.Image import Image as PILImage

from alert_rule import D_ALERT, MIN_IMAGES, alert_on_d
from histogram import compute_histogram, cumulative_distribution


def luminancia_L(image: PILImage) -> PILImage:
    """Caixa 1 — L (pixel): tons de cinza 0…255."""
    return image.convert("L")


def histograma_h(image: PILImage, bins: int = 256) -> list[int]:
    """Caixa 2 — histograma h: contagens por faixa de L."""
    return compute_histogram(image, channel="L", bins=bins)


def cdf_F(counts: Sequence[int]) -> list[float]:
    """Caixa 3 — CDF F: fração acumulada das contagens."""
    return cumulative_distribution(counts)


def delta_FG(F: Sequence[float], G: Sequence[float]) -> list[float]:
    """Caixa 4 — δ = |F − G| faixa a faixa."""
    return [abs(float(a) - float(b)) for a, b in zip(F, G)]


def D_max_delta(delta: Sequence[float]) -> float:
    """Caixa 5 — D = max δ."""
    return max(float(x) for x in delta)


def alerta_em_D(
    statistic: float,
    n_images_corpus: int,
    n_images_production: int,
    *,
    limiar: float = D_ALERT,
    min_images: int = MIN_IMAGES,
) -> str:
    """Caixa 6 — alerta em D: INCONCLUSIVO | ALERTA | TRANQUILO."""
    return alert_on_d(
        statistic,
        n_images_corpus,
        n_images_production,
        min_images=min_images,
        d_threshold=limiar,
    )


# Trechos para colar no README / Streamlit (exibição).
SNIPPETS: dict[str, str] = {
    "L (pixel)": '''def luminancia_L(image):
    return image.convert("L")
''',
    "histograma h": '''def histograma_h(image, bins=256):
    return list(image.convert("L").histogram())  # ou rebin para `bins`
''',
    "CDF F": '''def cdf_F(counts):
    total = sum(counts)
    acc, out = 0, []
    for c in counts:
        acc += c
        out.append(acc / total)
    return out
''',
    "δ = |F − G|": '''def delta_FG(F, G):
    return [abs(a - b) for a, b in zip(F, G)]
''',
    "D = max δ": '''def D_max_delta(delta):
    return max(delta)
''',
    "alerta em D": '''def alerta_em_D(D, n_ref, n_lote, limiar=0.10, min_n=8):
    if n_ref < min_n or n_lote < min_n:
        return "INCONCLUSIVO"
    return "ALERTA" if D >= limiar else "TRANQUILO"
''',
}
