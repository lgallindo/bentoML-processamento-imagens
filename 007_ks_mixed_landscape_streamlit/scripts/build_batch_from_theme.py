"""Agrega features de um ou mais temas (offline) → batch_stats/<nome>.json."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from image_extract import save_image_features  # noqa: E402
from request_stats import build_request_stats, write_request_stats  # noqa: E402

THEME_CHOICES = ("beaches", "forests", "balls")


def repo_root() -> Path:
    return Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
    )


def list_theme_images(theme: str) -> list[Path]:
    folder = repo_root() / "samples" / theme
    return sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.jpeg"))


def slice_theme(
    theme: str,
    *,
    offset: int,
    count: int,
) -> list[Path]:
    theme_paths = list_theme_images(theme)
    sliced = theme_paths[offset : offset + count]
    if len(sliced) < count:
        raise SystemExit(
            f"{theme}: pedidas {count} offset={offset}; há {len(sliced)} "
            f"(disponíveis {len(theme_paths)} em samples/{theme}/)"
        )
    return sliced


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "theme",
        nargs="?",
        choices=THEME_CHOICES,
        help="tema único (omitir se usar --themes)",
    )
    parser.add_argument("--name", help="nome do arquivo em batch_stats/ (default=tema)")
    parser.add_argument("--offset", type=int, default=0, help="offset (tema único)")
    parser.add_argument("--count", type=int, default=12, help="contagem (tema único)")
    parser.add_argument(
        "--themes",
        nargs="+",
        choices=THEME_CHOICES,
        help="vários temas a fundir (ex.: beaches forests)",
    )
    parser.add_argument(
        "--counts",
        type=int,
        nargs="+",
        help="contagem por tema quando usa --themes (ex.: 25 25)",
    )
    parser.add_argument(
        "--offsets",
        type=int,
        nargs="+",
        help="offset por tema quando usa --themes (ex.: 50 0)",
    )
    args = parser.parse_args(argv)

    if args.themes:
        themes = list(args.themes)
        n = len(themes)
        counts = list(args.counts) if args.counts is not None else [args.count] * n
        offsets = list(args.offsets) if args.offsets is not None else [args.offset] * n
        if len(counts) != n or len(offsets) != n:
            print(
                "--counts e --offsets devem ter o mesmo número de itens que --themes",
                file=sys.stderr,
            )
            return 1
        paths: list[Path] = []
        for theme, offset, count in zip(themes, offsets, counts):
            paths.extend(slice_theme(theme, offset=offset, count=count))
    elif args.theme:
        themes = [args.theme]
        paths = slice_theme(args.theme, offset=args.offset, count=args.count)
    else:
        print("indique theme ou --themes", file=sys.stderr)
        return 1

    name = args.name or ("+".join(themes) if len(themes) > 1 else themes[0])

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for path in paths:
            save_image_features(path, tmp_dir)
        for feature_path in tmp_dir.glob("*.json"):
            payload = json.loads(feature_path.read_text(encoding="utf-8"))
            payload.setdefault("endpoint", "offline")
            feature_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        stats = build_request_stats(tmp_dir)
        stats["source"] = f"samples/{'+'.join(themes)}"
        out = ROOT / "batch_stats" / f"{name}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        write_request_stats(stats, out)
        print(f"{out} n_images={stats['n_images']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
