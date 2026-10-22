"""Salva o modelo picklable de tons de cinza no model store do BentoML."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grayscale_model import save_grayscale_model  # noqa: E402


def main() -> int:
    tag = save_grayscale_model()
    print(f"modelo salvo: {tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
