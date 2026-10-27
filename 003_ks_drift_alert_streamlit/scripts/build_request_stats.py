"""Agrega request_features/ → request_stats.json."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from request_log import REQUEST_FEATURES_DIR  # noqa: E402
from request_stats import (  # noqa: E402
    REQUEST_STATS_PATH,
    build_request_stats,
    write_request_stats,
)


def main() -> int:
    features_dir = ROOT / REQUEST_FEATURES_DIR
    try:
        stats = build_request_stats(features_dir)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    out = write_request_stats(stats, ROOT / REQUEST_STATS_PATH)
    print(f"pedidos em {out} (n_images={stats['n_images']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
