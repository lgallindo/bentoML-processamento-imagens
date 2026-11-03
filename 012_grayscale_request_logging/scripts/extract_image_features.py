"""Camada 1 (CLI): extrai features do corpus temático (samples/beaches/)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from image_extract import FEATURES_DIR, save_image_features  # noqa: E402


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
    if not paths:
        print(
            f"nenhuma imagem em {beaches}/ — rode `just verify-themed-samples` "
            f"na raiz do repositório",
            file=sys.stderr,
        )
        return 1
    for path in paths:
        out = save_image_features(path, features_dir)
        print(out)
    print(f"{len(paths)} features em {features_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
