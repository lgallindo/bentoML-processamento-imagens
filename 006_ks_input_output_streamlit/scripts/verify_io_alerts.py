"""Imprime D e alerta entrada/saída para control e forests (e control shifted)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from banner import alert_on_d  # noqa: E402
from corpus_stats import load_corpus_stats  # noqa: E402
from ks_compare import compare_stats  # noqa: E402
from request_stats import load_request_stats  # noqa: E402

ALERTA_PT = {
    "ALERT": "ALERTA",
    "QUIET": "TRANQUILO",
    "INCONCLUSIVE": "INCONCLUSIVO",
}


def row(label: str, ref: dict, lote: dict) -> None:
    payload = compare_stats(ref, lote, channel="L")
    estado = alert_on_d(
        payload["statistic"],
        payload["n_images_corpus"],
        payload["n_images_production"],
    )
    print(
        f"{label:32s}  D={payload['statistic']:.4f}  "
        f"{ALERTA_PT[estado]}"
    )


def main() -> int:
    ref_in = load_corpus_stats(ROOT / "corpus_stats_input.json")
    ref_out = load_corpus_stats(ROOT / "corpus_stats_output.json")
    ref_shift = load_corpus_stats(ROOT / "corpus_stats_output_shifted.json")

    print("--- saudável ---")
    row(
        "control entrada",
        ref_in,
        load_request_stats(ROOT / "batch_stats/control_input.json"),
    )
    row(
        "control saída",
        ref_out,
        load_request_stats(ROOT / "batch_stats/control_output.json"),
    )
    row(
        "forests entrada",
        ref_in,
        load_request_stats(ROOT / "batch_stats/forests_input.json"),
    )
    row(
        "forests saída",
        ref_out,
        load_request_stats(ROOT / "batch_stats/forests_output.json"),
    )
    print("--- deslocado (control) ---")
    row(
        "control saída deslocada",
        ref_shift,
        load_request_stats(ROOT / "batch_stats/control_output_shifted.json"),
    )
    # contraste: entrada control vs saída deslocada medida contra ref saída saudável?
    # Plano: ref de saída no modo deslocado = corpus_stats_output_shifted
    # e lote = control_output_shifted. Para o contraste pedagógico no app:
    # entrada = control_input vs ref_in; saída = control_output_shifted vs ref_out
    # (referência de treino saudável). Medir ambos:
    print("--- contraste pedagógico (ref saída = saudável) ---")
    row(
        "control out_shifted vs ref_out",
        ref_out,
        load_request_stats(ROOT / "batch_stats/control_output_shifted.json"),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
