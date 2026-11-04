#!/usr/bin/env python3
"""Gera request_features-like JSONL com um pico de latência recente."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent / "bentoml_requests.jsonl"


def main() -> None:
    # Janela terminando ~2 min atrás — cai em now-1h no Explore.
    end = datetime.now(timezone.utc) - timedelta(minutes=2)
    start = end - timedelta(seconds=15 * 39)
    lines: list[str] = []
    for i in range(40):
        ts = start + timedelta(seconds=15 * i)
        slow = 20 <= i <= 24
        latency_ms = 180 + (i % 5) * 3
        if slow:
            latency_ms = 420 + (i - 20) * 40
        rec = {
            "logged_at": ts.isoformat().replace("+00:00", "Z"),
            "endpoint": "/inference-grayscale",
            "http_response_code": 200,
            "latency_ms": latency_ms,
            "phase": "slow" if slow else "stable",
            "message": (
                "inference grayscale slow path"
                if slow
                else "inference grayscale ok"
            ),
        }
        lines.append(json.dumps(rec, ensure_ascii=False))
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(lines)} lines) window {start.isoformat()} → {end.isoformat()}")


if __name__ == "__main__":
    main()
