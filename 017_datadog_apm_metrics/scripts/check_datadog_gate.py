#!/usr/bin/env python3
"""DEGRADE-001: decide se o lab SaaS Datadog pode correr.

- chave ausente / só espaços → exit 0 com SKIP (lab opcional)
- chave presente → exit 0 com RUN
Nunca imprime o valor da chave.
"""

from __future__ import annotations

import os
import sys


def main() -> int:
    raw = os.environ.get("DD_API_KEY", "")
    key = raw.strip()
    if not key:
        print("DATADOG_LAB=SKIP  # DD_API_KEY omitida ou em branco — DEGRADE-001")
        return 0
    print("DATADOG_LAB=RUN  # DD_API_KEY presente (valor não exibido)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
