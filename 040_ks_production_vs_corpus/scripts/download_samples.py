"""Baixa o corpus de treino (Lorem Picsum, seeds fixas) e grava o manifesto.

LEGADO: o corpus padrão da turma é samples/beaches/ na raiz do repositório
(ver just download-themed-samples / verify-themed-samples). Este script permanece
para experimentos com Picsum.
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_COUNT = 50
SEED_PREFIX = "bentoml-edu"
WIDTH = 640
HEIGHT = 480
USER_AGENT = "bentoml-image-demo-01/1.0 (educational; corpus download)"


def training_url(index: int) -> str:
    seed = f"{SEED_PREFIX}-{index}"
    return f"https://picsum.photos/seed/{seed}/{WIDTH}/{HEIGHT}"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download_one(index: int, samples_dir: Path, timeout: float = 60.0) -> dict:
    seed = f"{SEED_PREFIX}-{index}"
    url = training_url(index)
    filename = f"train_{index:03d}.jpg"
    dest = samples_dir / filename
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = response.read()
        final_url = response.geturl()
    dest.write_bytes(data)
    return {
        "id": index,
        "seed": seed,
        "url": url,
        "final_url": final_url,
        "path": f"samples/{filename}",
        "sha256": sha256_bytes(data),
        "bytes": len(data),
    }


def download_corpus(
    samples_dir: Path,
    count: int = DEFAULT_COUNT,
    manifest_path: Path | None = None,
) -> Path:
    if count < DEFAULT_COUNT:
        raise ValueError(f"count deve ser >= {DEFAULT_COUNT}, recebido {count}")
    samples_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict] = []
    for index in range(1, count + 1):
        print(f"baixando {index}/{count}...", flush=True)
        entries.append(download_one(index, samples_dir))
    manifest = {
        "source": "picsum.photos",
        "seed_prefix": SEED_PREFIX,
        "count": count,
        "width": WIDTH,
        "height": HEIGHT,
        "images": entries,
    }
    out = manifest_path or (samples_dir / "MANIFEST.json")
    out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    count = DEFAULT_COUNT
    if argv:
        count = int(argv[0])
    root = Path(__file__).resolve().parent.parent
    samples_dir = root / "samples"
    try:
        manifest = download_corpus(samples_dir, count=count)
    except urllib.error.URLError as exc:
        print(f"falha ao baixar corpus: {exc}", file=sys.stderr)
        return 1
    print(f"manifesto gravado em {manifest} ({count} imagens)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
