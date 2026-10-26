"""Expande samples/SOURCES.toml via pesquisa/categorias no Wikimedia Commons.

Uso (curadoria):
  uv run --no-active python scripts/expand_themed_sources.py --target 110
  just download-themed-samples
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import tomllib
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = (
    "bentoml-imagens/1.0 (educational themed samples; "
    "+https://github.com/lgallindo/bentoml-imagens)"
)
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
BATCHES = ("beaches", "forests", "balls")
SLEEP = 0.35

# Queries tuned for teaching themes (bitmap / photo-ish File: namespace).
SEARCH_QUERIES: dict[str, list[str]] = {
    "beaches": [
        'incategory:"Beaches" filetype:bitmap',
        'incategory:"Sandy beaches" filetype:bitmap',
        'incategory:"Beaches of Portugal" filetype:bitmap',
        "beach sand ocean filetype:bitmap",
        "praia costa filetype:bitmap",
    ],
    "forests": [
        'incategory:"Forests" filetype:bitmap',
        'incategory:"Temperate broadleaf forests" filetype:bitmap',
        "woodland path trees filetype:bitmap",
        "deciduous forest filetype:bitmap",
        "bosque floresta filetype:bitmap",
    ],
    "balls": [
        'incategory:"Basketballs" filetype:bitmap',
        'incategory:"Association football balls" filetype:bitmap',
        'incategory:"Balls" filetype:bitmap',
        "basketball ball filetype:bitmap",
        "soccer football ball closeup filetype:bitmap",
    ],
}

IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".gif")


def repo_root() -> Path:
    return Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
    )


def api_get(params: dict) -> dict:
    url = COMMONS_API + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.loads(response.read().decode())


def is_image_title(title: str) -> bool:
    lower = title.lower()
    return any(lower.endswith(suf) for suf in IMAGE_SUFFIXES)


def search_titles(query: str, *, want: int) -> list[str]:
    out: list[str] = []
    offset = 0
    while len(out) < want:
        batch = min(50, want - len(out))
        data = api_get(
            {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srnamespace": "6",
                "srlimit": str(batch),
                "sroffset": str(offset),
                "format": "json",
            }
        )
        time.sleep(SLEEP)
        hits = data.get("query", {}).get("search", [])
        if not hits:
            break
        for hit in hits:
            title = hit["title"]
            if is_image_title(title):
                out.append(title)
        if "continue" not in data:
            break
        offset = int(data["continue"].get("sroffset", offset + len(hits)))
    return out


def load_existing(path: Path) -> dict[str, list[str]]:
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    return {name: [str(t) for t in raw[name]["files"]] for name in BATCHES}


def write_sources(path: Path, batches: dict[str, list[str]]) -> None:
    lines = [
        "# Frozen Wikimedia Commons File: titles for themed teaching samples.",
        "# Regenerated only by curators; students use committed JPEGs + MANIFEST.json.",
        "",
    ]
    for name in BATCHES:
        lines.append(f"[{name}]")
        lines.append("files = [")
        for title in batches[name]:
            escaped = title.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'  "{escaped}",')
        lines.append("]")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def expand(target: int) -> dict[str, list[str]]:
    root = repo_root()
    sources_path = root / "samples" / "SOURCES.toml"
    batches = load_existing(sources_path)
    for name in BATCHES:
        seen = {t.removeprefix("File:") for t in batches[name]}
        # normalize to File: prefix
        ordered = []
        for t in batches[name]:
            if not t.startswith("File:"):
                t = f"File:{t}"
            if t not in ordered:
                ordered.append(t)
        batches[name] = ordered
        seen = set(batches[name])
        print(f"[{name}] start with {len(seen)} titles; target {target}", flush=True)
        for query in SEARCH_QUERIES[name]:
            if len(batches[name]) >= target:
                break
            need = target - len(batches[name]) + 40  # over-fetch then trim
            print(f"  search: {query!r} (need ~{need})", flush=True)
            for title in search_titles(query, want=need):
                if not title.startswith("File:"):
                    title = f"File:{title}"
                if title in seen:
                    continue
                seen.add(title)
                batches[name].append(title)
                if len(batches[name]) >= target:
                    break
        print(f"[{name}] now {len(batches[name])}", flush=True)
        if len(batches[name]) < target:
            print(
                f"aviso: {name} ficou com {len(batches[name])} < {target}",
                file=sys.stderr,
            )
    write_sources(sources_path, batches)
    print(f"escrito {sources_path}")
    return batches


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=int, default=110, help="mínimo por tema")
    args = parser.parse_args(argv)
    expand(args.target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
