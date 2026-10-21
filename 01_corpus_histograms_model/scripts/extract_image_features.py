"""Camada 1 (CLI): extrai features de cada train_* para features/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from image_extract import FEATURES_DIR, save_image_features  # noqa: E402


def main() -> int:
    samples = ROOT / "samples"
    features_dir = ROOT / FEATURES_DIR
    paths = sorted(samples.glob("train_*"))
    if not paths:
        print("nenhuma imagem train_* em samples/", file=sys.stderr)
        return 1
    for path in paths:
        out = save_image_features(path, features_dir)
        print(out)
    print(f"{len(paths)} features em {features_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
