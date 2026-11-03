from __future__ import annotations

from alert_rule import alert_on_d


def test_inconclusive_when_short_counts() -> None:
    assert alert_on_d(0.5, 7, 12) == "INCONCLUSIVE"


def test_alert_on_d_uses_statistic_only() -> None:
    assert alert_on_d(0.15, 12, 12) == "ALERT"
    assert alert_on_d(0.05, 12, 12) == "QUIET"
