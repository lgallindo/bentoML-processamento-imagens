"""Materializa lotes control/forests (entrada + saída + control shifted)."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from io_pipeline import extract_io_for_path  # noqa: E402
from request_stats import build_request_stats, write_request_stats  # noqa: E402


def repo_root() -> Path:
    return Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
    )


def theme_paths(theme: str, offset: int, count: int) -> list[Path]:
    folder = repo_root() / "samples" / theme
    paths = sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.jpeg"))
    sliced = paths[offset : offset + count]
    if len(sliced) < count:
        raise SystemExit(
            f"{theme}: pedidas {count} offset={offset}; há {len(sliced)}"
        )
    return sliced


def aggregate(feature_dir: Path, out: Path, source: str) -> None:
    stats = build_request_stats(feature_dir)
    stats["source"] = source
    out.parent.mkdir(parents=True, exist_ok=True)
    write_request_stats(stats, out)
    print(f"{out.name} n_images={stats['n_images']}")


def build_slice(
    theme: str,
    offset: int,
    count: int,
    *,
    name: str,
    with_shifted: bool,
) -> None:
    paths = theme_paths(theme, offset, count)
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        din = base / "in"
        dout = base / "out"
        dshift = base / "shift" if with_shifted else None
        for path in paths:
            extract_io_for_path(
                path,
                input_dir=din,
                output_dir=dout,
                shifted_dir=dshift,
            )
        batch = ROOT / "batch_stats"
        aggregate(
            din,
            batch / f"{name}_input.json",
            f"samples/{theme}[{offset}:{offset + count}]",
        )
        aggregate(
            dout,
            batch / f"{name}_output.json",
            f"samples/{theme}[{offset}:{offset + count}]/grayscale",
        )
        if dshift is not None:
            aggregate(
                dshift,
                batch / f"{name}_output_shifted.json",
                f"samples/{theme}[{offset}:{offset + count}]/grayscale-shifted",
            )


def main() -> int:
    for dname in ("features_input", "features_output", "features_output_shifted"):
        d = ROOT / dname
        if d.is_dir():
            for p in d.glob("*.json"):
                p.unlink()

    extract = ROOT / "scripts" / "extract_io_features.py"
    corpus = ROOT / "scripts" / "build_corpus_io.py"
    rc = subprocess.call(
        [sys.executable, str(extract), "beaches", "--offset", "0", "--count", "50"],
        cwd=str(ROOT),
    )
    if rc != 0:
        return rc
    rc = subprocess.call([sys.executable, str(corpus)], cwd=str(ROOT))
    if rc != 0:
        return rc

    build_slice("beaches", 50, 50, name="control", with_shifted=True)
    build_slice("forests", 0, 50, name="forests", with_shifted=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
