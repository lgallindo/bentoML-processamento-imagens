"""Baixa (ou verifica) amostras temáticas a partir de samples/SOURCES.toml.

Fonte: Wikimedia Commons (lista congelada de títulos File:…). Miniaturas
iiurlwidth=640, gravadas como JPEG. Preenche samples/MANIFEST.json e
samples/ATTRIBUTION.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

USER_AGENT = (
    "bentoml-imagens/1.0 (educational themed samples; "
    "+https://github.com/lgallindo/bentoml-imagens)"
)
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
LONG_EDGE = 640
JPEG_QUALITY = 85
BATCHES = ("beaches", "forests", "balls")
SLEEP_BETWEEN = 1.25


def repo_root() -> Path:
    out = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        text=True,
    ).strip()
    return Path(out)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def load_sources(path: Path) -> dict[str, list[str]]:
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    batches: dict[str, list[str]] = {}
    for name in BATCHES:
        section = raw.get(name)
        if not isinstance(section, dict):
            raise ValueError(f"SOURCES.toml: secção [{name}] em falta")
        files = section.get("files")
        if not isinstance(files, list) or not files:
            raise ValueError(f"SOURCES.toml: [{name}].files deve ser lista não vazia")
        batches[name] = [str(t) for t in files]
    return batches


def commons_imageinfo(title: str, timeout: float = 90.0) -> dict:
    if not title.startswith("File:"):
        title = f"File:{title}"
    params = {
        "action": "query",
        "titles": title,
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": str(LONG_EDGE),
        "format": "json",
    }
    url = COMMONS_API + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode())
    pages = payload.get("query", {}).get("pages", {})
    page = next(iter(pages.values()))
    if "missing" in page or not page.get("imageinfo"):
        raise FileNotFoundError(f"Commons sem imageinfo para {title}")
    info = page["imageinfo"][0]
    meta = info.get("extmetadata") or {}
    return {
        "title": page.get("title", title),
        "mime": info.get("mime"),
        "width": info.get("width"),
        "height": info.get("height"),
        "url": info.get("thumburl") or info.get("url"),
        "original_url": info.get("url"),
        "license": (meta.get("LicenseShortName") or {}).get("value", ""),
        "license_url": (meta.get("LicenseUrl") or {}).get("value", ""),
        "artist": strip_html((meta.get("Artist") or {}).get("value", "")),
        "credit": strip_html((meta.get("Credit") or {}).get("value", "")),
        "description_url": info.get("descriptionurl")
        or f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(page.get('title', title))}",
    }


def fetch_bytes(url: str, timeout: float = 90.0) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def to_jpeg_bytes(raw: bytes) -> bytes:
    with Image.open(BytesIO(raw)) as img:
        img = img.convert("RGB")
        w, h = img.size
        scale = LONG_EDGE / max(w, h)
        if scale < 1.0:
            img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))))
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        return buf.getvalue()


def slug_filename(index: int, title: str) -> str:
    base = title.removeprefix("File:").rsplit(".", 1)[0]
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower()
    slug = slug[:48] or "image"
    return f"{index:03d}-{slug}.jpg"


def write_attribution(manifest: dict, path: Path) -> None:
    lines = [
        "# Attribution — themed sample images",
        "",
        "Images under `samples/{beaches,forests,balls}/` come from",
        "[Wikimedia Commons](https://commons.wikimedia.org/). Licenses and authors",
        "below are taken from Commons `extmetadata` at download time.",
        "",
    ]
    for batch in BATCHES:
        lines.append(f"## {batch}")
        lines.append("")
        for entry in manifest["images"]:
            if entry["batch"] != batch:
                continue
            artist = entry.get("artist") or "(see Commons page)"
            lic = entry.get("license") or "see Commons"
            lines.append(
                f"- `{entry['path']}` — {artist} — {lic} — "
                f"[{entry['commons_title']}]({entry['source_url']})"
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def download_all(root: Path, *, force: bool = False) -> Path:
    sources_path = root / "samples" / "SOURCES.toml"
    batches = load_sources(sources_path)
    images: list[dict] = []
    for batch, titles in batches.items():
        dest_dir = root / "samples" / batch
        dest_dir.mkdir(parents=True, exist_ok=True)
        for index, title in enumerate(titles, start=1):
            filename = slug_filename(index, title)
            dest = dest_dir / filename
            rel = f"samples/{batch}/{filename}"
            print(f"[{batch}] {index}/{len(titles)} {title}", flush=True)
            info = commons_imageinfo(title)
            time.sleep(SLEEP_BETWEEN)
            if dest.exists() and not force:
                data = dest.read_bytes()
            else:
                raw = fetch_bytes(info["url"])
                data = to_jpeg_bytes(raw)
                dest.write_bytes(data)
                time.sleep(SLEEP_BETWEEN)
            images.append(
                {
                    "batch": batch,
                    "path": rel,
                    "commons_title": info["title"],
                    "source_url": info["description_url"],
                    "thumb_url": info["url"],
                    "license": info["license"],
                    "license_url": info.get("license_url") or "",
                    "artist": info["artist"],
                    "sha256": sha256_bytes(data),
                    "bytes": len(data),
                }
            )
    manifest = {
        "source": "wikimedia-commons",
        "long_edge_px": LONG_EDGE,
        "jpeg_quality": JPEG_QUALITY,
        "batches": {name: len(batches[name]) for name in BATCHES},
        "images": images,
    }
    manifest_path = root / "samples" / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_attribution(manifest, root / "samples" / "ATTRIBUTION.md")
    return manifest_path


def verify(root: Path) -> int:
    manifest_path = root / "samples" / "MANIFEST.json"
    if not manifest_path.is_file():
        print(f"manifesto em falta: {manifest_path}", file=sys.stderr)
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = 0
    for entry in manifest.get("images", []):
        path = root / entry["path"]
        if not path.is_file():
            print(f"em falta: {entry['path']}", file=sys.stderr)
            errors += 1
            continue
        digest = sha256_bytes(path.read_bytes())
        if digest != entry.get("sha256"):
            print(
                f"sha256 diverge: {entry['path']} "
                f"(esperado {entry.get('sha256')}, obtido {digest})",
                file=sys.stderr,
            )
            errors += 1
    for batch in BATCHES:
        count = sum(1 for e in manifest["images"] if e["batch"] == batch)
        minimum = 100
        if count < minimum:
            print(
                f"batch {batch}: {count} imagens (mínimo {minimum})",
                file=sys.stderr,
            )
            errors += 1
    demo = root / "samples" / "demo"
    demos = list(demo.glob("*.webp")) + list(demo.glob("*.jpg"))
    if len(demos) < 3:
        print(f"samples/demo/ tem {len(demos)} ficheiros (esperado ≥3)", file=sys.stderr)
        errors += 1
    if errors:
        print(f"verify falhou: {errors} problema(s)", file=sys.stderr)
        return 1
    print(f"verify OK — {len(manifest['images'])} imagens + demo/")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode",
        nargs="?",
        default="download",
        choices=("download", "verify"),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="voltar a descarregar mesmo se o JPEG já existir",
    )
    args = parser.parse_args(argv)
    root = repo_root()
    try:
        if args.mode == "verify":
            return verify(root)
        download_all(root, force=args.force)
        return verify(root)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
