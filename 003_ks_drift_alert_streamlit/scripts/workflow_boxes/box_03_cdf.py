#!/usr/bin/env python3
"""Caixa 3 — CDF F: fração acumulada das contagens do histograma.

Executa somente esta caixa (entrada = lista de contagens).

Uso::

    python scripts/workflow_boxes/box_03_cdf.py
"""

from __future__ import annotations


def cdf_F(counts: list[int]) -> list[float]:
    """CDF empírica: F_k = (soma das contagens até k) / N.

    Propriedades usadas pelo KS: F é não-decrescente e termina em 1
    (se N>0). Não exige Pillow — só aritmética.

    Alternativas:
      - ``numpy.cumsum(counts) / sum(counts)``;
      - CDF com correção de continuidade / método da escada à direita;
      - ECDF ponto a ponto sem histogramar (um salto por observação).
    """
    total = sum(counts)
    if total == 0:
        raise ValueError("histograma vazio: N=0")
    acc = 0
    out: list[float] = []
    for c in counts:
        acc += int(c)
        out.append(acc / total)
    return out


def main() -> int:
    # Exemplo mínimo do handout: [2, 1, 3] → [1/3, 1/2, 1].
    counts = [2, 1, 3]
    F = cdf_F(counts)
    assert abs(F[0] - 2 / 6) < 1e-12
    assert abs(F[1] - 3 / 6) < 1e-12
    assert abs(F[2] - 1.0) < 1e-12
    print(f"counts={counts} F={F}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
