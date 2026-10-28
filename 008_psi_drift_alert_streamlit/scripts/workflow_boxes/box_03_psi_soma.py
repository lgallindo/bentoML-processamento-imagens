#!/usr/bin/env python3
"""Caixa 3 — PSI = soma dos termos KL em todas as faixas.

Executa somente esta caixa (entrada = vetores de massas).

Uso::

    python scripts/workflow_boxes/box_03_psi_soma.py
"""

from __future__ import annotations

import math


def termo_kl(p_ref_b: float, p_lote_b: float, eps: float = 1e-6) -> float:
    pr = max(p_ref_b, eps)
    pl = max(p_lote_b, eps)
    return (pl - pr) * math.log(pl / pr)


def psi_soma(
    p_ref: list[float],
    p_lote: list[float],
    eps: float = 1e-6,
) -> float:
    """PSI = Σ_b termo_kl. Alternativas: χ²; JS divergence."""
    return sum(termo_kl(pr, pl, eps=eps) for pr, pl in zip(p_ref, p_lote))


def main() -> int:
    assert abs(psi_soma([0.5, 0.5], [0.5, 0.5])) < 1e-12
    psi = psi_soma([0.7, 0.3], [0.3, 0.7])
    assert psi > 0.2
    print("PSI = Σ — ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
