"""Unit tests for the pure helpers in expiry_scan (no Azure calls)."""

from datetime import datetime, timezone, timedelta

import expiry_scan as es

NOW = datetime(2026, 7, 9, tzinfo=timezone.utc)


def test_days_to_expiry():
    assert es.days_to_expiry(NOW + timedelta(days=10), NOW) == 10
    assert es.days_to_expiry(NOW - timedelta(days=2), NOW) == -2
    assert es.days_to_expiry(None, NOW) is None


def test_severity_for_days():
    assert es.severity_for_days(-1) == "Critical"
    assert es.severity_for_days(10) == "High"
    assert es.severity_for_days(20) == "Medium"
    assert es.severity_for_days(45) == "Low"


def test_time_bucket():
    assert es.time_bucket(-1) == "Expired"
    assert es.time_bucket(7) == "Within 14 days"
    assert es.time_bucket(20) == "15 to 30 days"
    assert es.time_bucket(45) == "31 days to horizon"


def test_classify_item_within_and_outside_horizon():
    inside = {"name": "c1", "kind": "Key Vault certificate", "source": "v1", "subscription": "a", "expiry": NOW + timedelta(days=5)}
    finding = es.classify_item(inside, NOW, 60)
    assert finding["severity"] == "High"
    assert finding["days_left"] == 5
    outside = {"name": "c2", "kind": "cert", "source": "v1", "subscription": "a", "expiry": NOW + timedelta(days=200)}
    assert es.classify_item(outside, NOW, 60) is None


def test_build_report_data_sorted_soonest_first():
    items = [
        {"name": "later", "kind": "Key Vault certificate", "source": "v", "subscription": "a", "expiry": NOW + timedelta(days=20)},
        {"name": "expired", "kind": "Key Vault secret", "source": "v", "subscription": "a", "expiry": NOW - timedelta(days=1)},
    ]
    data = es.build_report_data(items, 60, 1, [], now=NOW)
    assert data["findings"]["rows"][0]["item"] == "expired"  # soonest first
    assert data["summary_cards"][1]["value"] == "1"  # one expired


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all expiry_scan tests passed")
