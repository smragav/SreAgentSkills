"""Unit tests for the pure helpers in reliability_scan (no Azure calls)."""

import reliability_scan as rs


def test_adjust_severity_lowers_non_production():
    assert rs.adjust_severity("High", "vm-prod-web01") == "High"
    assert rs.adjust_severity("High", "vm-sandbox-01") == "Medium"
    assert rs.adjust_severity("Medium", "lab-cosmos") == "Low"
    assert rs.adjust_severity("Low", "dev-thing") == "Low"


def test_severity_counts_ordered_critical_first():
    findings = [
        {"severity": "Low"},
        {"severity": "High"},
        {"severity": "High"},
        {"severity": "Critical"},
    ]
    counts = rs.severity_counts(findings)
    assert [c["name"] for c in counts] == ["Critical", "High", "Low"]
    assert counts[1]["value"] == 2
    assert all("band" in c for c in counts)


def test_subscription_counts_highest_first():
    findings = [
        {"subscription": "a"},
        {"subscription": "a"},
        {"subscription": "b"},
    ]
    rows = rs.subscription_counts(findings, {"a": "Sub A", "b": "Sub B"})
    assert rows[0]["name"] == "Sub A"
    assert rows[0]["value"] == 2


def test_build_report_data_shape():
    findings = [
        {"resource": "vm1", "severity": "High", "subscription": "a", "resource_group": "rg1", "issue": "x", "recommendation": "y", "resource_type": "Virtual machine"},
        {"resource": "sa1", "severity": "Medium", "subscription": "a", "resource_group": "rg1", "issue": "x", "recommendation": "y", "resource_type": "Storage account"},
    ]
    data = rs.build_report_data(findings, {"a": "Sub A"}, 1, [])
    assert data["title"] == "Reliability Posture Review"
    assert data["findings"]["rows"][0]["severity"] == "High"  # sorted, High first
    assert data["findings"]["rows"][0]["_band"] == "High"
    assert data["summary_cards"][1]["value"] == "1"  # one Critical/High
    assert data["findings"]["rows"][0]["subscription"] == "Sub A"


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all reliability_scan tests passed")
