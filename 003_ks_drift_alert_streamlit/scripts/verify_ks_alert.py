"""Imprime D e o estado do alerta para corpus vs batch_stats/<lote>.json.

Pré-condições: corpus_stats.json e batch_stats/<lote>.json nesta aula.

Fluxo::

    corpus + lote JSON ──► compare_stats ──► alert_on_d ──► stdout

Saída: uma linha com D, tamanhos e o estado (ALERT|QUIET|…).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alert_rule import alert_on_d  # noqa: E402
from corpus_stats import load_default_corpus_stats  # noqa: E402
from ks_compare import compare_stats  # noqa: E402
from request_stats import load_request_stats  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("uso: verify_ks_alert.py <lote>", file=sys.stderr)
        return 1
    name = argv[0]
    path = ROOT / "batch_stats" / f"{name}.json"
    if not path.is_file():
        raise FileNotFoundError(f"em falta: {path}")
    corpus = load_default_corpus_stats()
    production = load_request_stats(path)
    payload = compare_stats(corpus, production, channel="L", bins=256)
    state = alert_on_d(
        payload["statistic"],
        payload["n_images_corpus"],
        payload["n_images_production"],
    )
    print(
        f"batch={name} D={payload['statistic']:.6f} "
        f"n_c={payload['n_images_corpus']} n_p={payload['n_images_production']} "
        f"alerta={state}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
