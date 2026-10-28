"""Funções de produção alinhadas às caixas do fluxo PSI (e aos scripts demo).

Miniaturas: ``illustrations/box_0N_*.png``.
Demos isolados: ``scripts/workflow_boxes/box_0N_*.py``.
Figura completa: ``illustrations/01_workflow_hist_to_psi.png``.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from alert_psi import MIN_IMAGES, PSI_SHIFT, PSI_STABLE, alert_on_psi
from psi import EPS_DEFAULT, compute_psi, counts_to_masses


def massas_p(counts: Sequence[int | float]) -> list[float]:
    """Massas relativas a partir de contagens (delega a ``counts_to_masses``)."""
    return counts_to_masses(counts)


def termo_kl(
    p_ref_b: float,
    p_lote_b: float,
    *,
    eps: float = EPS_DEFAULT,
) -> float:
    """Contribuição de uma faixa: (q − p) · ln(q / p) com suavização eps."""
    pr = max(float(p_ref_b), eps)
    pl = max(float(p_lote_b), eps)
    return (pl - pr) * math.log(pl / pr)


def psi_soma(
    p_ref: Sequence[float],
    p_lote: Sequence[float],
    *,
    eps: float = EPS_DEFAULT,
) -> float:
    """PSI = Σ termo_kl (delega a ``compute_psi``)."""
    return compute_psi(p_ref, p_lote, eps=eps)


def faixa_alerta_psi(
    psi: float,
    n_images_corpus: int,
    n_images_production: int,
    *,
    min_images: int = MIN_IMAGES,
    stable: float = PSI_STABLE,
    shift: float = PSI_SHIFT,
) -> str:
    """INCONCLUSIVE / QUIET / WATCH / ALERT (códigos EN de ``alert_on_psi``)."""
    return alert_on_psi(
        psi,
        n_images_corpus,
        n_images_production,
        min_images=min_images,
        stable=stable,
        shift=shift,
    )


# Textos curtos para o expander do Streamlit (handout traz a prosa longa).
SNIPPETS: dict[str, str] = {
    "massas p_b": '''def massas_p(counts):
    """p_b = c_b / Σ c. Alternativas: suavizar eps e renormalizar."""
    total = sum(counts)
    return [c / total for c in counts]
''',
    "termo KL": '''def termo_kl(p_ref_b, p_lote_b, eps=1e-6):
    """(q−p)·ln(q/p) com max(·,eps). Alternativas: KL só num sentido."""
    import math
    pr, pl = max(p_ref_b, eps), max(p_lote_b, eps)
    return (pl - pr) * math.log(pl / pr)
''',
    "PSI = Σ": '''def psi_soma(p_ref, p_lote, eps=1e-6):
    """PSI = Σ_b termo_kl. Alternativas: χ²; JS divergence."""
    return sum(termo_kl(pr, pl, eps=eps) for pr, pl in zip(p_ref, p_lote))
''',
    "faixa alerta": '''def faixa_alerta_psi(psi, n_ref, n_lote, stable=0.10, shift=0.25, min_n=8):
    """INCONCLUSIVO / ESTÁVEL / INVESTIGAR / MUDANÇA FORTE."""
    if n_ref < min_n or n_lote < min_n:
        return "INCONCLUSIVO"
    if psi > shift:
        return "MUDANÇA FORTE"
    if psi >= stable:
        return "INVESTIGAR"
    return "ESTÁVEL"
''',
}
