#!/usr/bin/env python3
"""Extrai pares label→tag a partir do fixture OpenMetrics (modo SKIP).

Não contacta Datadog nem exige BentoML em :3000.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "fixtures" / "sample_metrics_snippet.txt"
LABEL_RE = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)="([^"]*)"')


def pairs_from_metrics(text: str, limit: int = 3) -> list[dict[str, str]]:
    """Devolve até ``limit`` pares distintos a partir das linhas de amostra."""
    seen: set[tuple[str, str]] = set()
    out: list[dict[str, str]] = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        if "{" not in line:
            continue
        metric = line.split("{", 1)[0].strip()
        for key, value in LABEL_RE.findall(line):
            tip = (key, value)
            if tip in seen:
                continue
            seen.add(tip)
            out.append(
                {
                    "prometheus_label": f'{key}="{value}"',
                    "datadog_tag": f"{key}:{value}",
                    "metric_hint": metric,
                }
            )
            if len(out) >= limit:
                return out
    return out


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else DEFAULT_FIXTURE
    text = path.read_text(encoding="utf-8")
    pairs = pairs_from_metrics(text)
    if len(pairs) < 3:
        print(f"esperava ≥3 pares; obtive {len(pairs)} em {path}", file=sys.stderr)
        return 1
    print(json.dumps({"source": str(path.relative_to(ROOT)), "pairs": pairs}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
