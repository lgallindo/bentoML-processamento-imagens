"""Imprime PSI P2/P1 e faixas de alerta para corpus vs batch_stats/<lote>.json."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alert_psi import alert_on_psi, label_pt  # noqa: E402
from corpus_stats import load_default_corpus_stats  # noqa: E402
from ks_compare import compare_stats  # noqa: E402
from psi import compare_psi_means, compare_psi_pixels  # noqa: E402
from request_stats import load_request_stats  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("uso: verify_psi.py <lote>", file=sys.stderr)
        return 1
    name = argv[0]
    path = ROOT / "batch_stats" / f"{name}.json"
    if not path.is_file():
        print(f"em falta: {path}", file=sys.stderr)
        return 1
    corpus = load_default_corpus_stats()
    production = load_request_stats(path)
    p2 = compare_psi_means(corpus, production)
    p1 = compare_psi_pixels(corpus, production, channel="L", bins=256)
    state_p2 = alert_on_psi(
        p2["psi"], p2["n_images_corpus"], p2["n_images_production"]
    )
    state_p1 = alert_on_psi(
        p1["psi"], p1["n_images_corpus"], p1["n_images_production"]
    )
    ks = compare_stats(corpus, production, channel="L", bins=256)
    print(
        f"batch={name} "
        f"PSI_P2(mean_L)={p2['psi']:.6f} ({label_pt(state_p2)}) "
        f"PSI_P1(pixel_L)={p1['psi']:.6f} ({label_pt(state_p1)}) "
        f"KS_D={ks['statistic']:.6f} "
        f"n_c={p2['n_images_corpus']} n_p={p2['n_images_production']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
