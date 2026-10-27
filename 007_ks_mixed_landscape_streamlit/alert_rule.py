"""Regras de alerta operacional sobre a estatística KS (D).

Define quando o painel e os scripts imprimem INCONCLUSIVO, ALERTA, TRANQUILO
ou (na regra legada) WATCH, a partir de D e, opcionalmente, do valor-p.

Pré-condições:
  - statistic é D ∈ [0, 1] (máximo |F_ref − F_lote|);
  - n_images_* contam imagens (não pixels) de cada conjunto.

Fluxo::

    n_ref, n_lote ──► n < min? ──► INCONCLUSIVO
                           │
                           └─► (regra D) D ≥ limiar? ──► ALERTA / TRANQUILO
                           └─► (regra D+p) p e D ──► ALERTA / WATCH / TRANQUILO

Saídas principais: alert_on_d(...), alert_on_d_and_p(...).
"""

from __future__ import annotations

MIN_IMAGES = 8
P_ALERT = 0.05
D_ALERT = 0.10

Alert = str  # ALERT | QUIET | INCONCLUSIVE | WATCH


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


def alert_on_d_and_p(
    p_value: float,
    statistic: float,
    n_images_corpus: int,
    n_images_production: int,
    *,
    min_images: int = MIN_IMAGES,
    p_threshold: float = P_ALERT,
    d_threshold: float = D_ALERT,
) -> Alert:
    """Regra legada: cruza valor-p assintótico com D (testes / scripts)."""
    if n_images_corpus < min_images or n_images_production < min_images:
        return "INCONCLUSIVE"
    p_fire = p_value < p_threshold
    d_fire = statistic >= d_threshold
    if p_fire and d_fire:
        return "ALERT"
    if p_fire or d_fire:
        return "WATCH"
    return "QUIET"
