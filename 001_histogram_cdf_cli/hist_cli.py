"""CLI: lista de números → histograma + CDF (JSON / CSV / PNG)."""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

import numpy as np

from histcdf import DEFAULT_BINS, histogram_with_cdf
from plotting import plot_histogram_cdf


def parse_values_text(raw: str) -> np.ndarray:
    text = raw.strip()
    if not text:
        raise SystemExit("lista de valores vazia")
    if text.startswith("["):
        data = json.loads(text)
        if not isinstance(data, list):
            raise SystemExit("JSON deve ser uma lista de números")
        return np.asarray(data, dtype=float)
    parts = [p.strip() for p in text.replace(";", ",").split(",") if p.strip()]
    return np.asarray([float(p) for p in parts], dtype=float)


def load_values(args: argparse.Namespace) -> np.ndarray:
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
        return parse_values_text(text)
    if args.values is None:
        raise SystemExit("informe --values ou --file")
    return parse_values_text(args.values)


def to_csv(payload: dict) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["bin", "left", "right", "count", "cdf"])
    edges = payload["edges"]
    for i, (count, cdf) in enumerate(zip(payload["counts"], payload["cdf"], strict=True)):
        writer.writerow([i, edges[i], edges[i + 1], count, cdf])
    return buf.getvalue()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Histograma e CDF de uma lista de números")
    parser.add_argument("--values", help="JSON list ou números separados por vírgula")
    parser.add_argument("--file", help="arquivo texto/JSON com a lista")
    parser.add_argument("--bins", type=int, default=DEFAULT_BINS)
    parser.add_argument("--lo", type=float, default=None)
    parser.add_argument("--hi", type=float, default=None)
    parser.add_argument("--format", choices=("json", "csv", "image"), default="json")
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    if (args.lo is None) ^ (args.hi is None):
        raise SystemExit("use --lo e --hi juntos, ou nenhum dos dois")
    value_range = None if args.lo is None else (args.lo, args.hi)

    values = load_values(args)
    try:
        payload = histogram_with_cdf(values, bins=args.bins, value_range=value_range)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    if args.format == "json":
        text = json.dumps(payload, indent=2) + "\n"
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
        return 0

    if args.format == "csv":
        text = to_csv(payload)
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
        return 0

    fig = plot_histogram_cdf(payload["counts"], payload["edges"], payload["cdf"])
    out = Path(args.output) if args.output else Path("histogram.png")
    fig.savefig(out, dpi=120)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
