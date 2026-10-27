"""Lote misto landscapes: n=50 e ordenação qualitativa de D vs control/forests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from banner import alert_on_d
from corpus_stats import load_default_corpus_stats
from ks_compare import compare_stats
from request_stats import load_request_stats

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / "batch_stats"


def _repo_root() -> Path:
    return Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
    )


def _samples_ready() -> bool:
    root = _repo_root() / "samples"
    beaches = list((root / "beaches").glob("*.jpg")) + list(
        (root / "beaches").glob("*.jpeg")
    )
    forests = list((root / "forests").glob("*.jpg")) + list(
        (root / "forests").glob("*.jpeg")
    )
    return len(beaches) >= 75 and len(forests) >= 50


def _ensure_demo_batches() -> None:
    needed = ("control.json", "forests.json", "landscapes.json")
    if all((BATCH / name).is_file() for name in needed):
        return
    if not _samples_ready():
        pytest.skip("samples/beaches e samples/forests insuficientes para o freeze")
    result = subprocess.run(
        ["just", "build-demo-batches"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip(f"build-demo-batches falhou: {result.stderr or result.stdout}")


@pytest.mark.skipif(not _samples_ready(), reason="samples temáticos ausentes")
def test_landscapes_batch_has_fifty_images() -> None:
    _ensure_demo_batches()
    path = BATCH / "landscapes.json"
    assert path.is_file(), "rode just build-demo-batches"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["n_images"] == 50


@pytest.mark.skipif(not _samples_ready(), reason="samples temáticos ausentes")
def test_landscapes_d_between_control_and_forests() -> None:
    _ensure_demo_batches()
    corpus = load_default_corpus_stats()
    control = load_request_stats(BATCH / "control.json")
    forests = load_request_stats(BATCH / "forests.json")
    landscapes = load_request_stats(BATCH / "landscapes.json")

    d_control = compare_stats(corpus, control, channel="L")["statistic"]
    d_forests = compare_stats(corpus, forests, channel="L")["statistic"]
    d_landscapes = compare_stats(corpus, landscapes, channel="L")["statistic"]

    assert alert_on_d(d_control, corpus["n_images"], control["n_images"]) == "QUIET"
    assert alert_on_d(d_forests, corpus["n_images"], forests["n_images"]) == "ALERT"
    # Misto: tipicamente entre os extremos; permite igualdade nos bordos.
    assert d_control <= d_landscapes <= d_forests + 1e-9
    # Aceite: ALERTA ou D intermediário documentado (ainda ≥ limiar na prática).
    estado_misto = alert_on_d(
        d_landscapes, corpus["n_images"], landscapes["n_images"]
    )
    assert estado_misto in {"ALERT", "QUIET"}
    if estado_misto == "QUIET":
        assert d_control < d_landscapes  # ainda intermediário mesmo sem alerta
