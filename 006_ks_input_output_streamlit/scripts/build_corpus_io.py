"""Agrega features_* → corpus_stats_input / output / output_shifted."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from corpus_stats import build_corpus_stats, write_corpus_stats  # noqa: E402


def main() -> int:
    mapping = {
        ROOT / "features_input": ROOT / "corpus_stats_input.json",
        ROOT / "features_output": ROOT / "corpus_stats_output.json",
        ROOT / "features_output_shifted": ROOT / "corpus_stats_output_shifted.json",
    }
    for features_dir, out in mapping.items():
        if not features_dir.is_dir() or not any(features_dir.glob("*.json")):
            print(f"pula {out.name}: sem JSON em {features_dir.name}", file=sys.stderr)
            continue
        stats = build_corpus_stats(features_dir)
        write_corpus_stats(stats, out)
        print(f"{out} n_images={stats['n_images']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
