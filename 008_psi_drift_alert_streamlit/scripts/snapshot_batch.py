"""Copia request_features/ → batches/<nome>/ e grava batch_stats/<nome>.json."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from request_log import REQUEST_FEATURES_DIR  # noqa: E402
from request_stats import build_request_stats, write_request_stats  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="nome do lote (ex.: forests, control)")
    parser.add_argument(
        "--clear-source",
        action="store_true",
        help="apaga JSON em request_features/ depois de copiar",
    )
    args = parser.parse_args(argv)

    src = ROOT / REQUEST_FEATURES_DIR
    files = sorted(src.glob("*.json"))
    if not files:
        print(f"nenhum JSON em {src}/", file=sys.stderr)
        return 1

    batch_dir = ROOT / "batches" / args.name
    if batch_dir.exists():
        shutil.rmtree(batch_dir)
    batch_dir.mkdir(parents=True)
    for path in files:
        shutil.copy2(path, batch_dir / path.name)

    stats = build_request_stats(batch_dir)
    out = ROOT / "batch_stats" / f"{args.name}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    write_request_stats(stats, out)
    print(f"lote {args.name}: {stats['n_images']} imagens → {out}")

    if args.clear_source:
        for path in files:
            path.unlink()
        print(f"limpo: {src}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
