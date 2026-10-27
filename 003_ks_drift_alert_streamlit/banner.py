"""Regras de alerta sobre a estatística KS (D)."""

from __future__ import annotations

MIN_IMAGES = 8
P_ALERT = 0.05
D_ALERT = 0.10

Alert = str  # ALERT | QUIET | INCONCLUSIVE
Banner = Alert  # compatível com testes legados


def alert_on_d(
    statistic: float,
    n_images_corpus: int,
    n_images_production: int,
    *,
    min_images: int = MIN_IMAGES,
    d_threshold: float = D_ALERT,
) -> Alert:
    """Alerta didático centrado em D (a estatística monitorada)."""
    if n_images_corpus < min_images or n_images_production < min_images:
        return "INCONCLUSIVE"
    if statistic >= d_threshold:
        return "ALERT"
    return "QUIET"


def banner_rule(
    p_value: float,
    statistic: float,
    n_images_corpus: int,
    n_images_production: int,
    *,
    min_images: int = MIN_IMAGES,
    p_threshold: float = P_ALERT,
    d_threshold: float = D_ALERT,
) -> Banner:
    """Legado: quatro saídas com valor-p (testes / scripts antigos)."""
    if n_images_corpus < min_images or n_images_production < min_images:
        return "INCONCLUSIVE"
    p_fire = p_value < p_threshold
    d_fire = statistic >= d_threshold
    if p_fire and d_fire:
        return "ALERT"
    if p_fire or d_fire:
        return "WATCH"
    return "QUIET"
