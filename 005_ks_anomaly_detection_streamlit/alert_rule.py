"""Alerta sobre D com time boxing (janela mínima de imagens)."""

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
