"""Camada 2 (CLI): agrega features/ → corpus_stats.json."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from corpus_stats import CORPUS_STATS_PATH, build_corpus_stats, write_corpus_stats  # noqa: E402
from image_extract import FEATURES_DIR  # noqa: E402


def main() -> int:
    features_dir = ROOT / FEATURES_DIR
    try:
        stats = build_corpus_stats(features_dir)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    out = write_corpus_stats(stats, ROOT / CORPUS_STATS_PATH)
    print(f"corpus em {out} (n_images={stats['n_images']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
