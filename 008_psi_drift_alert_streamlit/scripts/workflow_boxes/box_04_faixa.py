#!/usr/bin/env python3
"""Caixa 4 — faixa de alerta sobre PSI (cortes 0,10 / 0,25).

Executa somente esta caixa (entrada = PSI e tamanhos n).

Uso::

    python scripts/workflow_boxes/box_04_faixa.py
"""

from __future__ import annotations


def faixa_alerta_psi(
    psi: float,
    n_ref: int,
    n_lote: int,
    stable: float = 0.10,
    shift: float = 0.50,
    min_n: int = 8,
) -> str:
    """INCONCLUSIVO / ESTÁVEL / INVESTIGAR / MUDANÇA FORTE."""
    if n_ref < min_n or n_lote < min_n:
        return "INCONCLUSIVO"
    if psi > shift:
        return "MUDANÇA FORTE"
    if psi >= stable:
        return "INVESTIGAR"
    return "ESTÁVEL"


def main() -> int:
    assert faixa_alerta_psi(0.40, 5, 50) == "INCONCLUSIVO"
    assert faixa_alerta_psi(0.05, 50, 50) == "ESTÁVEL"
    assert faixa_alerta_psi(0.15, 50, 50) == "INVESTIGAR"
    assert faixa_alerta_psi(0.40, 50, 50) == "MUDANÇA FORTE"
    print("faixa alerta — ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
