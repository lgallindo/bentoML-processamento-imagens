"""Extrai features de entrada/saída/saída-deslocada para um tema fatiado."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from io_pipeline import extract_io_for_path  # noqa: E402


def repo_root() -> Path:
    return Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("theme", choices=("beaches", "forests", "balls"))
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=ROOT / "features_input",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "features_output",
    )
    parser.add_argument(
        "--shifted-dir",
        type=Path,
        default=ROOT / "features_output_shifted",
    )
    parser.add_argument(
        "--no-shifted",
        action="store_true",
        help="não grava features_output_shifted",
    )
    args = parser.parse_args(argv)

    folder = repo_root() / "samples" / args.theme
    paths = sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.jpeg"))
    sliced = paths[args.offset : args.offset + args.count]
    if len(sliced) < args.count:
        print(
            f"{args.theme}: pedidas {args.count} offset={args.offset}; há {len(sliced)}",
            file=sys.stderr,
        )
        return 1

    shifted = None if args.no_shifted else args.shifted_dir
    for path in sliced:
        extract_io_for_path(
            path,
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            shifted_dir=shifted,
        )
    print(
        f"{args.theme}[{args.offset}:{args.offset + args.count}] → "
        f"{args.input_dir.name}/ + {args.output_dir.name}/"
        + (f" + {args.shifted_dir.name}/" if shifted else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
