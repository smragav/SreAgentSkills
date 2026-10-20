"""Unit tests for the pure helpers in change_scan (no Azure calls)."""

import change_scan as cs


def _ev(category, op, status="Succeeded", ts="2026-07-09T10:00:00Z", rid="/subscriptions/a/resourceGroups/rg/providers/x/vm1", health=None):
    event = {"category": {"value": category}, "operationName": {"value": op, "localizedValue": op}, "status": {"value": status}, "eventTimestamp": ts, "resourceId": rid, "resourceGroupName": "rg", "caller": "u@x"}
    if health:
        event["properties"] = {"currentHealthStatus": health}
    return event


def test_is_change_event():
    assert cs.is_change_event(_ev("Administrative", "Microsoft.Compute/virtualMachines/write")) is True
    assert cs.is_change_event(_ev("Administrative", "Microsoft.Compute/virtualMachines/read")) is False
    assert cs.is_change_event(_ev("ResourceHealth", "x/write")) is False


def test_is_health_degraded():
    assert cs.is_health_degraded(_ev("ResourceHealth", "x", health="Unavailable")) is True
    assert cs.is_health_degraded(_ev("ResourceHealth", "x", health="Available")) is False


def test_correlate_links_change_before_degradation():
    change = cs.extract_change(_ev("Administrative", "Microsoft.Compute/virtualMachines/write", ts="2026-07-09T10:00:00Z"))
    health = cs.extract_health(_ev("ResourceHealth", "x", ts="2026-07-09T10:30:00Z", health="Unavailable"))
    findings, linked = cs.correlate([change], [health], window_minutes=120)
    assert len(findings) == 1
    assert findings[0]["severity"] == "High"
    assert "30 min" in findings[0]["note"]
    assert len(linked) == 1


def test_correlate_ignores_change_after_or_outside_window():
    change = cs.extract_change(_ev("Administrative", "x/write", ts="2026-07-09T13:00:00Z"))
    health = cs.extract_health(_ev("ResourceHealth", "x", ts="2026-07-09T10:30:00Z", health="Unavailable"))
    findings, _ = cs.correlate([change], [health], window_minutes=120)
    assert findings == []


def test_classify_unlinked_delete_and_failure():
    delete = cs.extract_change(_ev("Administrative", "x/delete", status="Succeeded"))
    assert cs.classify_unlinked(delete)["severity"] == "Medium"
    fail = cs.extract_change(_ev("Administrative", "x/write", status="Failed"))
    assert "failed" in cs.classify_unlinked(fail)["note"].lower()
    ok = cs.extract_change(_ev("Administrative", "x/write", status="Succeeded"))
    assert cs.classify_unlinked(ok) is None


def test_build_report_data_counts():
    change = cs.extract_change(_ev("Administrative", "x/write", ts="2026-07-09T10:00:00Z"))
    health = cs.extract_health(_ev("ResourceHealth", "x", ts="2026-07-09T10:20:00Z", health="Unavailable"))
    data = cs.build_report_data([change], [health], 7, 1, {"a": "Sub A"}, [])
    assert data["summary_cards"][1]["value"] == "1"  # one linked
    assert data["title"] == "Change Audit"


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all change_scan tests passed")
