from __future__ import annotations

from banner import banner_rule


def test_inconclusive_when_short_counts() -> None:
    assert banner_rule(0.001, 0.5, 7, 12) == "INCONCLUSIVE"
    assert banner_rule(0.001, 0.5, 12, 7) == "INCONCLUSIVE"


def test_alert_both_fire() -> None:
    assert banner_rule(0.01, 0.15, 12, 12) == "ALERT"


def test_watch_one_fire() -> None:
    assert banner_rule(0.01, 0.05, 12, 12) == "WATCH"
    assert banner_rule(0.2, 0.15, 12, 12) == "WATCH"


def test_quiet_neither() -> None:
    assert banner_rule(0.2, 0.05, 12, 12) == "QUIET"
