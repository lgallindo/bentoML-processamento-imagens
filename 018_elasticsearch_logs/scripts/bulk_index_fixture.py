#!/usr/bin/env python3
"""Indexa fixtures/bentoml_requests.jsonl no Elasticsearch via _bulk."""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "bentoml_requests.jsonl"
INDEX = "bentoml-requests"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:9200")
    parser.add_argument("--index", default=INDEX)
    parser.add_argument("--fixture", type=Path, default=FIXTURE)
    args = parser.parse_args()

    # recreate index
    for method in ("DELETE",):
        req = urllib.request.Request(
            f"{args.url}/{args.index}",
            method=method,
        )
        try:
            urllib.request.urlopen(req)
        except Exception:
            pass

    mapping = {
        "mappings": {
            "properties": {
                "logged_at": {"type": "date"},
                "endpoint": {"type": "keyword"},
                "http_response_code": {"type": "integer"},
                "latency_ms": {"type": "integer"},
                "phase": {"type": "keyword"},
                "message": {"type": "text"},
            }
        }
    }
    req = urllib.request.Request(
        f"{args.url}/{args.index}",
        data=json.dumps(mapping).encode(),
        headers={"Content-Type": "application/json"},
        method="PUT",
    )
    urllib.request.urlopen(req)

    lines: list[str] = []
    for line in args.fixture.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        lines.append(json.dumps({"index": {"_index": args.index}}))
        lines.append(line)
    body = ("\n".join(lines) + "\n").encode()
    req = urllib.request.Request(
        f"{args.url}/_bulk",
        data=body,
        headers={"Content-Type": "application/x-ndjson"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
    errors = result.get("errors")
    n = len(result.get("items", []))
    print(f"bulk items={n} errors={errors}")
    # refresh
    urllib.request.urlopen(
        urllib.request.Request(f"{args.url}/{args.index}/_refresh", method="POST")
    )


if __name__ == "__main__":
    main()
