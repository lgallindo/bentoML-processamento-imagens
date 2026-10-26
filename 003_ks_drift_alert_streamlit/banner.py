"""Classroom banner for KS drift alert (v1 design locks)."""

from __future__ import annotations

MIN_IMAGES = 8
P_ALERT = 0.05
D_ALERT = 0.10

Banner = str  # ALERT | WATCH | QUIET | INCONCLUSIVE


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
    """Four-outcome classroom banner from KS D, p-value, and image counts."""
    if n_images_corpus < min_images or n_images_production < min_images:
        return "INCONCLUSIVE"
    p_fire = p_value < p_threshold
    d_fire = statistic >= d_threshold
    if p_fire and d_fire:
        return "ALERT"
    if p_fire or d_fire:
        return "WATCH"
    return "QUIET"
