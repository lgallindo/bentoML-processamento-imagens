"""Grava os dois modelos picklable da lição 006 no armazém BentoML local."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grayscale_model import (  # noqa: E402
    save_grayscale_model,
    save_grayscale_shifted_model,
)


def main() -> int:
    print(save_grayscale_model())
    print(save_grayscale_shifted_model())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
