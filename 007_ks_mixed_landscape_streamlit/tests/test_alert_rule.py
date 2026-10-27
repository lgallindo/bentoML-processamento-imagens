from __future__ import annotations

from alert_rule import alert_on_d, alert_on_d_and_p


def test_inconclusive_when_short_counts() -> None:
    assert alert_on_d_and_p(0.001, 0.5, 7, 12) == "INCONCLUSIVE"
    assert alert_on_d_and_p(0.001, 0.5, 12, 7) == "INCONCLUSIVE"
    assert alert_on_d(0.5, 7, 12) == "INCONCLUSIVE"


def test_alert_both_fire() -> None:
    assert alert_on_d_and_p(0.01, 0.15, 12, 12) == "ALERT"


def test_watch_one_fire() -> None:
    assert alert_on_d_and_p(0.01, 0.05, 12, 12) == "WATCH"
    assert alert_on_d_and_p(0.2, 0.15, 12, 12) == "WATCH"


def test_quiet_neither() -> None:
    assert alert_on_d_and_p(0.2, 0.05, 12, 12) == "QUIET"


def test_alert_on_d_uses_statistic_only() -> None:
    assert alert_on_d(0.15, 12, 12) == "ALERT"
    assert alert_on_d(0.05, 12, 12) == "QUIET"
