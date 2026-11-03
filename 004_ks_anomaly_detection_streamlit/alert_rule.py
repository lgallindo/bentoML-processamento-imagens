"""Alerta operacional sobre D com mínimo de imagens na janela.

Pré-condições: statistic = D ∈ [0, 1]; n_images conta imagens da janela.

Fluxo::

    n < min? ──► INCONCLUSIVO
         │
         └─► D ≥ limiar? ──► ALERTA / TRANQUILO

Saídas principais: alert_on_d(...); rótulos em ALERT_PT.
"""

from __future__ import annotations

from anomaly import D_ALERT, MIN_WINDOW_IMAGES

ALERT_PT = {
    "ALERT": "ALERTA",
    "QUIET": "TRANQUILO",
    "INCONCLUSIVE": "INCONCLUSIVO",
}


def alert_on_d(
    statistic: float,
    n_images: int,
    *,
    min_images: int = MIN_WINDOW_IMAGES,
    d_threshold: float = D_ALERT,
) -> str:
    if n_images < min_images:
        return "INCONCLUSIVE"
    if statistic >= d_threshold:
        return "ALERT"
    return "QUIET"
