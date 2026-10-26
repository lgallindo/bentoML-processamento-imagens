"""Agrega features de um tema (offline) → batch_stats/<nome>.json (sem servidor)."""

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


def repo_root() -> Path:
    return Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "theme",
        nargs="?",
        choices=("beaches", "forests", "balls"),
        help="tema único (omitir se usar --themes)",
    )
    parser.add_argument("--name", help="nome do ficheiro em batch_stats/ (default=tema)")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument(
        "--themes",
        nargs="+",
        help="vários temas a fundir (contingência landscapes)",
    )
    args = parser.parse_args(argv)

    if args.themes:
        themes = list(args.themes)
    elif args.theme:
        themes = [args.theme]
    else:
        print("indique theme ou --themes", file=sys.stderr)
        return 1
    name = args.name or ("+".join(themes) if len(themes) > 1 else themes[0])
    paths: list[Path] = []
    for theme in themes:
        folder = repo_root() / "samples" / theme
        theme_paths = sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.jpeg"))
        if args.themes:
            paths.extend(theme_paths)
        else:
            sliced = theme_paths[args.offset : args.offset + args.count]
            if len(sliced) < args.count:
                print(
                    f"{theme}: pedidas {args.count} offset={args.offset}; há {len(sliced)}",
                    file=sys.stderr,
                )
                return 1
            paths.extend(sliced)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for path in paths:
            save_image_features(path, tmp_dir)
        # save_image_features writes corpus-shaped JSON; build_request_stats expects
        # the same histogram keys — reuse by ensuring luminance_mean + histograms.
        # image_extract.save_image_features output matches request log shape minus logged_at.
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
