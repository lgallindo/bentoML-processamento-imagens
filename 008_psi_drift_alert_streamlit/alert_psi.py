"""Faixas de alerta sobre o PSI (Population Stability Index).

Literatura de *credit scoring* / scorecards (Siddiqi) cita com frequência
os cortes 0,10 / 0,25. No freeze offline desta aula (P2 = médias de L por
imagem em 10 quantis da referência) o lote **controle** (praias [50:100])
fica em PSI ≈ 0,26 — logo acima de 0,25 — o que pintaria o mesmo tema como
MUDANÇA FORTE e estragaria a demonstração.

Cortes **operacionais do painel** (calibrados no freeze Streamlit)::

| PSI (P2)       | Código EN | Leitura PT        |
| -------------- | --------- | ----------------- |
| < 0,10         | QUIET     | ESTÁVEL           |
| 0,10 – 0,50    | WATCH     | INVESTIGAR        |
| > 0,50         | ALERT     | MUDANÇA FORTE     |

Assim o controle cai em INVESTIGAR; florestas/bolas (PSI ≫ 1) em MUDANÇA
FORTE. P1 (pixels) continua bem abaixo de 0,10 no controle com estes cortes.
"""

from __future__ import annotations

MIN_IMAGES = 8
PSI_STABLE = 0.10
# Calibrado no freeze P2 (controle ≈ 0,26); clássico de scorecard seria 0,25.
PSI_SHIFT = 0.50

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
    """Semáforo de PSI; exige imagens suficientes em ambos os lados."""
    if n_images_corpus < min_images or n_images_production < min_images:
        return "INCONCLUSIVE"
    if psi > shift:
        return "ALERT"
    if psi >= stable:
        return "WATCH"
    return "QUIET"


def label_pt(state: Alert) -> str:
    return ALERT_PT.get(state, state)
