#!/usr/bin/env python3
"""Caixa 4 — δ = |F − G|: distância vertical entre duas CDFs.

Executa somente esta caixa (entrada = duas listas do mesmo comprimento).

Uso::

    python scripts/workflow_boxes/box_04_delta.py
"""

from __future__ import annotations


def delta_FG(F: list[float], G: list[float]) -> list[float]:
    """δ_k = |F_k − G_k| em cada faixa k.

    Alternativas:
      - distância com sinal (F−G) para ver qual curva está acima;
      - norma L2 das diferenças (não é o KS clássico);
      - estatística de Cramér–von Mises (∫ (F−G)² dH) — outro teste.
    O KS usa o máximo de |F−G|; por isso devolvemos a lista completa de δ.
    """
    if len(F) != len(G):
        raise ValueError("F e G devem ter o mesmo número de faixas")
    return [abs(float(a) - float(b)) for a, b in zip(F, G)]


def main() -> int:
    F = [1 / 3, 0.5, 1.0]
    G = [1 / 6, 1 / 3, 1.0]
    delta = delta_FG(F, G)
    assert abs(delta[0] - 1 / 6) < 1e-12
    assert abs(delta[1] - 1 / 6) < 1e-12
    assert abs(delta[2] - 0.0) < 1e-12
    print(f"delta={delta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
