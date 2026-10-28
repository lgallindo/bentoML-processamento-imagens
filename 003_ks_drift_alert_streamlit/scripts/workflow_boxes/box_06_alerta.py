#!/usr/bin/env python3
"""Caixa 6 — alerta em D: traduz a estatística em estado operacional.

Executa somente esta caixa (entrada = D e tamanhos n).

Uso::

    python scripts/workflow_boxes/box_06_alerta.py
"""

from __future__ import annotations


def alerta_em_D(
    D: float,
    n_ref: int,
    n_lote: int,
    limiar: float = 0.10,
    min_n: int = 8,
) -> str:
    """INCONCLUSIVO / ALERTA / TRANQUILO a partir de D e da massa amostral.

    Alternativas:
      - semáforo FRTB (verde < 0,09; vermelho > 0,12; âmbar no meio);
      - regra D+p (ALERT / WATCH / QUIET) em ``alert_rule.alert_on_d_and_p``;
      - limiar calibrado por quantil histórico de D em produção.
    A aula fixa limiar=0,10 e exige n≥8 em cada lado.
    """
    if n_ref < min_n or n_lote < min_n:
        return "INCONCLUSIVO"
    if D >= limiar:
        return "ALERTA"
    return "TRANQUILO"


def main() -> int:
    assert alerta_em_D(0.40, 5, 50) == "INCONCLUSIVO"
    assert alerta_em_D(0.05, 50, 50) == "TRANQUILO"
    assert alerta_em_D(0.23, 50, 50) == "ALERTA"
    print("INCONCLUSIVO / TRANQUILO / ALERTA — ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
