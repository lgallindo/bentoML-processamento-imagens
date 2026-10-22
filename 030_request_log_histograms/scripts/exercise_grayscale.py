"""Submete exerciser_samples/exer_*.jpg a /inference-grayscale e cronometra a passagem.

Nao faz download. Prefira: just download-exerciser-samples && just serve
e, noutro terminal, just exercise-grayscale.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLES_DIR = ROOT / "exerciser_samples"
DEFAULT_COUNT = 50
DEFAULT_PORT = 3333


def list_exerciser_images(samples_dir: Path = SAMPLES_DIR) -> list[Path]:
    return sorted(samples_dir.glob("exer_*.jpg"))


def submit_to_grayscale(image_path: Path, port: int) -> float:
    """Devolve a duracao em segundos desta submissao."""
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
    argv = argv if argv is not None else sys.argv[1:]
    port = DEFAULT_PORT
    count = DEFAULT_COUNT
    for arg in argv:
        if arg.startswith("--port="):
            port = int(arg.split("=", 1)[1])
        elif arg.startswith("--count="):
            count = int(arg.split("=", 1)[1])

    paths = list_exerciser_images()
    if len(paths) < count:
        print(
            f"esperadas {count} imagens em {SAMPLES_DIR}/exer_*.jpg; "
            f"encontradas {len(paths)}. "
            f"Execute antes: just download-exerciser-samples",
            file=sys.stderr,
        )
        return 1

    paths = paths[:count]
    durations: list[float] = []
    wall_started = time.perf_counter()
    try:
        for i, path in enumerate(paths, start=1):
            elapsed = submit_to_grayscale(path, port)
            durations.append(elapsed)
            print(
                f"submetendo {i}/{count}: {path.name}  ({elapsed:.3f}s)",
                flush=True,
            )
    except Exception as exc:
        print(f"falha: {exc}", file=sys.stderr)
        return 1
    wall = time.perf_counter() - wall_started
    total = sum(durations)
    print(
        f"concluido: {count} submissoes a http://127.0.0.1:{port}/inference-grayscale\n"
        f"tempo parede: {wall:.3f}s\n"
        f"soma por pedido: {total:.3f}s\n"
        f"media por pedido: {total / count:.3f}s\n"
        f"min={min(durations):.3f}s  max={max(durations):.3f}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
