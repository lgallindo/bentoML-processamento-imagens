"""Funções de produção alinhadas às caixas do fluxo (e aos scripts demo).

Miniaturas: ``illustrations/box_0N_*.png``.
Demos isolados: ``scripts/workflow_boxes/box_0N_*.py``.
Figura completa (inalterada): ``illustrations/01_workflow_l_to_alert.png``.
"""

from __future__ import annotations

from collections.abc import Sequence

from PIL.Image import Image as PILImage

from alert_rule import D_ALERT, MIN_IMAGES, alert_on_d
from histogram import compute_histogram, cumulative_distribution


def luminancia_L(image: PILImage) -> PILImage:
    return image.convert("L")


def histograma_h(image: PILImage, bins: int = 256) -> list[int]:
    return compute_histogram(image, channel="L", bins=bins)


def cdf_F(counts: Sequence[int]) -> list[float]:
    return cumulative_distribution(counts)


def delta_FG(F: Sequence[float], G: Sequence[float]) -> list[float]:
    return [abs(float(a) - float(b)) for a, b in zip(F, G)]


def D_max_delta(delta: Sequence[float]) -> float:
    return max(float(x) for x in delta)


def alerta_em_D(
    statistic: float,
    n_images_corpus: int,
    n_images_production: int,
    *,
    limiar: float = D_ALERT,
    min_images: int = MIN_IMAGES,
) -> str:
    return alert_on_d(
        statistic,
        n_images_corpus,
        n_images_production,
        min_images=min_images,
        d_threshold=limiar,
    )


# Textos curtos para o expander do Streamlit (handout traz a prosa longa).
SNIPPETS: dict[str, str] = {
    "L (pixel)": '''def luminancia_L(image):
    """Modo L. Alternativas: Rec. 601 manual; canal R/G/B isolado."""
    return image.convert("L")
''',
    "histograma h": '''def histograma_h(image, bins=256):
    """Contagens por faixa. Alternativas: numpy.histogram; densidades."""
    cinza = image.convert("L")
    counts = list(cinza.histogram())
    if bins == 256:
        return counts
    out = [0] * bins
    for i, value in enumerate(counts):
        out[min(bins - 1, (i * bins) // 256)] += int(value)
    return out
''',
    "CDF F": '''def cdf_F(counts):
    """F_k = soma_até_k / N. Alternativas: cumsum; ECDF ponto a ponto."""
    total = sum(counts)
    acc, out = 0, []
    for c in counts:
        acc += c
        out.append(acc / total)
    return out
''',
    "δ = |F − G|": '''def delta_FG(F, G):
    """δ_k = |F_k − G_k|. Alternativas: sinal; L2; Cramér–von Mises."""
    return [abs(a - b) for a, b in zip(F, G)]
''',
    "D = max δ": '''def D_max_delta(delta):
    """D = max δ. Alternativas: Anderson–Darling; valor-p (rodapé)."""
    return max(delta)
''',
    "alerta em D": '''def alerta_em_D(D, n_ref, n_lote, limiar=0.10, min_n=8):
    """INCONCLUSIVO / ALERTA / TRANQUILO. Alternativas: FRTB; D+p."""
    if n_ref < min_n or n_lote < min_n:
        return "INCONCLUSIVO"
    return "ALERTA" if D >= limiar else "TRANQUILO"
''',
}
