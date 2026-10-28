#!/usr/bin/env python3
"""Caixa 2 — termo KL simétrico por faixa: (q − p) · ln(q / p).

Executa somente esta caixa (entrada = massas de uma faixa).

Uso::

    python scripts/workflow_boxes/box_02_termo_kl.py
"""

from __future__ import annotations

import math


def termo_kl(p_ref_b: float, p_lote_b: float, eps: float = 1e-6) -> float:
    """(q−p)·ln(q/p) com max(·,eps). Alternativas: KL só num sentido."""
    pr = max(p_ref_b, eps)
    pl = max(p_lote_b, eps)
    return (pl - pr) * math.log(pl / pr)


def main() -> int:
    assert abs(termo_kl(0.5, 0.5)) < 1e-12
    t = termo_kl(0.2, 0.8)
    assert t > 0
    # massa zero no lote: suaviza com eps
    assert math.isfinite(termo_kl(0.5, 0.0))
    print("termo KL — ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
