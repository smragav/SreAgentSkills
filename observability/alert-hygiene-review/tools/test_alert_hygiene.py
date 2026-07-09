"""Unit tests for the pure helpers in alert_hygiene (no Azure calls)."""

import alert_hygiene as ah


def _alert(rule, severity="Sev3", condition="Fired", state="New"):
    return {"properties": {"essentials": {"alertRule": rule, "severity": severity, "monitorCondition": condition, "alertState": state}}}


def test_aggregate_counts_and_severity():
    alerts = [_alert("r1", "Sev1"), _alert("r1", "Sev3", condition="Resolved", state="Closed"), _alert("r2")]
    stats = ah.aggregate_alerts(alerts)
    assert stats["r1"]["count"] == 2
    assert stats["r1"]["resolved"] == 1
    assert stats["r1"]["min_sev"] == 1
    assert stats["r2"]["count"] == 1


def test_classify_noisy_rule_high_at_double_threshold():
    stats = {"count": 45, "resolved": 0, "new": 0, "min_sev": 3, "name": "r1"}
    finding = ah.classify_rule("r1", stats, 20)
    assert finding["severity"] == "High"
    assert "fired 45 times" in finding["issue"]


def test_classify_cry_wolf():
    stats = {"count": 10, "resolved": 9, "new": 0, "min_sev": 1, "name": "r1"}
    finding = ah.classify_rule("r1", stats, 20)
    assert finding is not None
    assert "auto resolves" in finding["issue"]
    assert finding["severity"] == "Medium"


def test_classify_returns_none_when_clean():
    stats = {"count": 3, "resolved": 1, "new": 0, "min_sev": 3, "name": "r1"}
    assert ah.classify_rule("r1", stats, 20) is None


def test_build_report_data_includes_disabled():
    alerts = [_alert("r1", "Sev1") for _ in range(25)]
    data = ah.build_report_data(alerts, [{"name": "off-rule"}], "7d", 1, 20, [])
    rules = [row["rule"] for row in data["findings"]["rows"]]
    assert "off-rule" in rules
    assert data["summary_cards"][0]["value"] == "25"


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all alert_hygiene tests passed")
