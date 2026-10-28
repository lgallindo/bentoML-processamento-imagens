from __future__ import annotations

from alert_psi import alert_on_psi, label_pt


def test_inconclusive_when_short() -> None:
    assert alert_on_psi(0.5, 7, 12) == "INCONCLUSIVE"
    assert alert_on_psi(0.5, 12, 7) == "INCONCLUSIVE"


def test_stable_below_010() -> None:
    assert alert_on_psi(0.05, 12, 12) == "QUIET"
    assert label_pt("QUIET") == "ESTÁVEL"


def test_watch_band() -> None:
    assert alert_on_psi(0.10, 12, 12) == "WATCH"
    assert alert_on_psi(0.50, 12, 12) == "WATCH"
    assert label_pt("WATCH") == "INVESTIGAR"


def test_strong_shift_above_050() -> None:
    assert alert_on_psi(0.5000001, 12, 12) == "ALERT"
    assert alert_on_psi(0.60, 12, 12) == "ALERT"
    assert label_pt("ALERT") == "MUDANÇA FORTE"
