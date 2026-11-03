"""Regras de alerta operacional sobre a estatística KS (D).

Define quando o painel e os scripts imprimem INCONCLUSIVO, ALERTA ou
TRANQUILO. O alerta operacional da aula é calculado somente a partir de D.

Pré-condições:
  - statistic é D ∈ [0, 1] (máximo |F_ref − F_lote|);
  - n_images_* contam imagens (não pixels) de cada conjunto.

Fluxo::

    n_ref, n_lote ──► n < min? ──► INCONCLUSIVO
                           │
                           └─► (regra D) D ≥ limiar? ──► ALERTA / TRANQUILO

Saída principal: alert_on_d(...), baseada somente em D.
"""

from __future__ import annotations

MIN_IMAGES = 8
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
