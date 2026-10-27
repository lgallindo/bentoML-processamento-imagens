"""Freeze qualitativo: control estável-ish; forests mais forte. Skip sem JSONs."""

from __future__ import annotations

from pathlib import Path

import pytest

from alert_psi import alert_on_psi
from corpus_stats import load_default_corpus_stats
from psi import compare_psi_means, compare_psi_pixels
from request_stats import load_request_stats

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus_stats.json"
CONTROL = ROOT / "batch_stats" / "control.json"
FORESTS = ROOT / "batch_stats" / "forests.json"

pytestmark = pytest.mark.skipif(
    not (CORPUS.is_file() and CONTROL.is_file() and FORESTS.is_file()),
    reason="corpus/batch_stats ausentes — rode just build-demo-batches",
)


def test_control_p2_below_forests_and_bounded() -> None:
    """P2 com quantis (10 faixas) é sensível em n=50; o handout documenta o PSI.

    No freeze local o controle fica perto do corte 0,25 (às vezes logo acima);
    florestas sobe uma ordem de magnitude. Cortes clássicos 0,10/0,25 mantidos.
    """
    corpus = load_default_corpus_stats()
    control = load_request_stats(CONTROL)
    forests = load_request_stats(FORESTS)
    p2_c = compare_psi_means(corpus, control)
    p2_f = compare_psi_means(corpus, forests)
    assert p2_c["psi"] < p2_f["psi"]
    # mesmo tema: não explode como troca de tema
    assert p2_c["psi"] < 1.0
    assert p2_f["psi"] > 0.25  # mudança forte sob faixas clássicas


def test_forests_p2_alert_or_watch() -> None:
    corpus = load_default_corpus_stats()
    forests = load_request_stats(FORESTS)
    p2 = compare_psi_means(corpus, forests)
    state = alert_on_psi(p2["psi"], p2["n_images_corpus"], p2["n_images_production"])
    assert state in {"WATCH", "ALERT"}


def test_p1_control_stable_forests_elevated() -> None:
    """Espelho P1 (pixels): faixas clássicas separam limpo no freeze."""
    corpus = load_default_corpus_stats()
    control = load_request_stats(CONTROL)
    forests = load_request_stats(FORESTS)
    p1_c = compare_psi_pixels(corpus, control)
    p1_f = compare_psi_pixels(corpus, forests)
    state_c = alert_on_psi(
        p1_c["psi"], p1_c["n_images_corpus"], p1_c["n_images_production"]
    )
    state_f = alert_on_psi(
        p1_f["psi"], p1_f["n_images_corpus"], p1_f["n_images_production"]
    )
    assert state_c == "QUIET"
    assert p1_f["psi"] > p1_c["psi"]
    assert state_f in {"WATCH", "ALERT"}
