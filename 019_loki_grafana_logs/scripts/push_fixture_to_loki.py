#!/usr/bin/env python3
"""Empurra fixtures/bentoml_requests.jsonl para Loki (HTTP push).

Usado pelo harness quando se quer capturas estáveis sem depender do
ciclo de vida do Promtail no primeiro boot.
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "bentoml_requests.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:3100/loki/api/v1/push")
    parser.add_argument("--fixture", type=Path, default=FIXTURE)
    args = parser.parse_args()

    by: dict[tuple[str, str], list[list[str]]] = defaultdict(list)
    for line in args.fixture.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        ts = datetime.fromisoformat(rec["logged_at"].replace("Z", "+00:00"))
        ns = str(int(ts.timestamp() * 1_000_000_000))
        key = (rec.get("phase", "unknown"), rec.get("endpoint", "unknown"))
        by[key].append([ns, rec["message"]])

    streams = [
        {
            "stream": {
                "job": "bentoml",
                "service": "image-processor",
                "phase": phase,
                "endpoint": endpoint,
            },
            "values": values,
        }
        for (phase, endpoint), values in by.items()
    ]
    body = json.dumps({"streams": streams}).encode("utf-8")
    req = urllib.request.Request(
        args.url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        print(f"push HTTP {resp.status}; streams={len(streams)}; lines={sum(len(s['values']) for s in streams)}")


if __name__ == "__main__":
    main()
