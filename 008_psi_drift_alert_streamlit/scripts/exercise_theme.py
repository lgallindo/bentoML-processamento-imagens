"""Submete um tema de samples/ a /inference-grayscale (servidor: just serve)."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PORT = 3338


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


def submit_to_grayscale(image_path: Path, port: int) -> float:
    import httpx

    started = time.perf_counter()
    with image_path.open("rb") as handle:
        response = httpx.post(
            f"http://127.0.0.1:{port}/inference-grayscale",
            files={"image": (image_path.name, handle, "image/jpeg")},
            timeout=120.0,
        )
    response.raise_for_status()
    return time.perf_counter() - started


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "theme",
        choices=("beaches", "forests", "balls"),
        help="pasta sob samples/",
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--offset", type=int, default=0, help="salta as N primeiras")
    parser.add_argument("--count", type=int, default=50, help="quantas imagens enviar")
    args = parser.parse_args(argv)

    paths = list_theme_images(args.theme)
    sliced = paths[args.offset : args.offset + args.count]
    if len(sliced) < args.count:
        print(
            f"tema {args.theme}: pedidas {args.count} a partir de offset={args.offset}; "
            f"só há {len(sliced)} (total {len(paths)})",
            file=sys.stderr,
        )
        return 1

    for i, path in enumerate(sliced, start=1):
        elapsed = submit_to_grayscale(path, args.port)
        print(f"submetendo {i}/{args.count}: {path.name}  ({elapsed:.3f}s)", flush=True)
    print(f"ok: {args.count} imagens de {args.theme} → request_features/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
