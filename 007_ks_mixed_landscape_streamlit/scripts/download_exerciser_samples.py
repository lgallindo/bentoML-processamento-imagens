"""Passagem offline: baixa o conjunto do exercitador (distinto do corpus).

LEGADO: produção padrão = samples/forests/ na raiz do repo.
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_COUNT = 50
SEED_PREFIX = "bentoml-exer"
WIDTH = 640
HEIGHT = 480
USER_AGENT = "bentoml-image-demo-03-exerciser/1.0"
SAMPLES_DIR = ROOT / "exerciser_samples"


def image_url(index: int) -> str:
    return f"https://picsum.photos/seed/{SEED_PREFIX}-{index}/{WIDTH}/{HEIGHT}"


def download_exerciser_set(
    samples_dir: Path = SAMPLES_DIR,
    count: int = DEFAULT_COUNT,
) -> Path:
    samples_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    for index in range(1, count + 1):
        seed = f"{SEED_PREFIX}-{index}"
        url = image_url(index)
        filename = f"exer_{index:03d}.jpg"
        dest = samples_dir / filename
        print(f"baixando exercitador {index}/{count}...", flush=True)
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
        dest.write_bytes(data)
        entries.append(
            {
                "id": index,
                "seed": seed,
                "url": url,
                "path": f"exerciser_samples/{filename}",
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    manifest = {
        "source": "picsum.photos",
        "seed_prefix": SEED_PREFIX,
        "note": "distinto do corpus samples/train_* (prefixo bentoml-edu)",
        "count": count,
        "images": entries,
    }
    out = samples_dir / "MANIFEST.json"
    out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    count = DEFAULT_COUNT
    for arg in argv:
        if arg.startswith("--count="):
            count = int(arg.split("=", 1)[1])
    try:
        out = download_exerciser_set(count=count)
    except OSError as exc:
        print(f"falha no download: {exc}", file=sys.stderr)
        return 1
    print(f"manifesto em {out} ({count} imagens)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
