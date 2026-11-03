"""Camada 1 (CLI): extrai features do corpus de treino (primeira metade de beaches/)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from image_extract import FEATURES_DIR, save_image_features  # noqa: E402

# Shipped freeze: first half of beaches as pretend training corpus.
CORPUS_TAKE = 50


def repo_root() -> Path:
    return Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
    )


def main() -> int:
    beaches = repo_root() / "samples" / "beaches"
    features_dir = ROOT / FEATURES_DIR
    paths = sorted(beaches.glob("*.jpg")) + sorted(beaches.glob("*.jpeg"))
    if len(paths) < CORPUS_TAKE:
        print(
            f"esperadas ≥{CORPUS_TAKE} imagens em {beaches}/; "
            f"encontradas {len(paths)}. "
            f"Confirme: just verify-themed-samples (raiz do repo)",
            file=sys.stderr,
        )
        return 1
    paths = paths[:CORPUS_TAKE]
    features_dir.mkdir(parents=True, exist_ok=True)
    for old in features_dir.glob("*.json"):
        old.unlink()
    for path in paths:
        out = save_image_features(path, features_dir)
        print(out)
    print(f"{len(paths)} features de corpus em {features_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
