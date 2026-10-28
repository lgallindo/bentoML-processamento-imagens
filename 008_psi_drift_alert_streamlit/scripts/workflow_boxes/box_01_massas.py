#!/usr/bin/env python3
"""Caixa 1 — massas relativas a partir de contagens por faixa.

Executa somente esta caixa (entrada = contagens).

Uso::

    python scripts/workflow_boxes/box_01_massas.py
"""

from __future__ import annotations


def massas_p(counts: list[int]) -> list[float]:
    """p_b = c_b / Σ c. Alternativas: suavizar eps e renormalizar."""
    total = sum(counts)
    return [c / total for c in counts]


def main() -> int:
    assert massas_p([2, 2, 6]) == [0.2, 0.2, 0.6]
    assert abs(sum(massas_p([1, 1, 1, 1])) - 1.0) < 1e-12
    print("massas p_b — ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
