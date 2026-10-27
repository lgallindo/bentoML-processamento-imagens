"""Faixas de alerta sobre o PSI (Population Stability Index).

Cortes clássicos de credit scoring (Siddiqi / scorecards):

| PSI            | Código EN | Leitura PT        |
| -------------- | --------- | ----------------- |
| < 0,10         | QUIET     | ESTÁVEL           |
| 0,10 – 0,25    | WATCH     | INVESTIGAR        |
| > 0,25         | ALERT     | MUDANÇA FORTE     |
"""

from __future__ import annotations

MIN_IMAGES = 8
PSI_STABLE = 0.10
PSI_SHIFT = 0.25

Alert = str  # QUIET | WATCH | ALERT | INCONCLUSIVE

ALERT_PT = {
    "QUIET": "ESTÁVEL",
    "WATCH": "INVESTIGAR",
    "ALERT": "MUDANÇA FORTE",
    "INCONCLUSIVE": "INCONCLUSIVO",
}


def alert_on_psi(
    psi: float,
    n_images_corpus: int,
    n_images_production: int,
    *,
    min_images: int = MIN_IMAGES,
    stable: float = PSI_STABLE,
    shift: float = PSI_SHIFT,
) -> Alert:
    """Semáforo clássico de PSI; exige imagens suficientes em ambos os lados."""
    if n_images_corpus < min_images or n_images_production < min_images:
        return "INCONCLUSIVE"
    if psi > shift:
        return "ALERT"
    if psi >= stable:
        return "WATCH"
    return "QUIET"


def label_pt(state: Alert) -> str:
    return ALERT_PT.get(state, state)
