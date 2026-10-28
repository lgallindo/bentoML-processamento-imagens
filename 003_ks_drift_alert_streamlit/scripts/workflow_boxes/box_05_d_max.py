#!/usr/bin/env python3
"""Caixa 5 — D = max δ: estatística de Kolmogorov–Smirnov.

Executa somente esta caixa (entrada = lista de δ).

Uso::

    python scripts/workflow_boxes/box_05_d_max.py
"""

from __future__ import annotations


def D_max_delta(delta: list[float]) -> float:
    """D = máximo de |F−G| ao longo das faixas.

    Alternativas:
      - KS com peso (Anderson–Darling) — penaliza caudas;
      - valor-p assintótico a partir de D e n_eff (nota de rodapé na aula;
        não entra na regra de alerta).
    """
    if not delta:
        raise ValueError("lista delta vazia")
    return max(float(x) for x in delta)


def main() -> int:
    delta = [1 / 6, 1 / 6, 0.0]
    D = D_max_delta(delta)
    assert abs(D - 1 / 6) < 1e-12
    print(f"D={D}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
