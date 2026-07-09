"""Unit tests for the pure helpers in quota_scan (no Azure calls)."""

import quota_scan as qs


def test_utilization():
    assert qs.utilization(80, 100) == 80.0
    assert qs.utilization(0, 0) == 0.0
    assert qs.utilization(5, 0) == 0.0


def test_band_thresholds():
    assert qs.band(96) == "Critical"
    assert qs.band(90) == "High"
    assert qs.band(85) == "Medium"
    assert qs.band(50) == "Low"


def test_classify_usage_flags_near_limit():
    item = {"name": {"localizedValue": "Total Regional vCPUs"}, "currentValue": 95, "limit": 100}
    finding = qs.classify_usage(item, "Sub A", "westeurope", 80)
    assert finding["severity"] == "Critical"
    assert finding["utilization"] == "95%"
    assert finding["_percent"] == 95.0


def test_classify_usage_ignores_below_threshold_and_no_limit():
    below = {"name": {"value": "x"}, "currentValue": 10, "limit": 100}
    assert qs.classify_usage(below, "Sub A", "westeurope", 80) is None
    nolimit = {"name": {"value": "x"}, "currentValue": 10, "limit": 0}
    assert qs.classify_usage(nolimit, "Sub A", "westeurope", 80) is None


def test_build_report_data_sorts_by_tightness():
    findings = [
        qs.classify_usage({"name": {"value": "a"}, "currentValue": 82, "limit": 100}, "S", "r", 80),
        qs.classify_usage({"name": {"value": "b"}, "currentValue": 99, "limit": 100}, "S", "r", 80),
    ]
    data = qs.build_report_data(findings, 1, 1, 80, [])
    assert data["findings"]["rows"][0]["quota"] == "b"  # tightest first
    assert data["summary_cards"][1]["value"] == "1"  # one Critical


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all quota_scan tests passed")
