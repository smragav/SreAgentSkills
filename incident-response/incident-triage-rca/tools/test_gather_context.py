"""Unit tests for the pure helpers in gather_context (no Azure calls)."""

import gather_context as gc


def test_parse_resource_id():
    rid = "/subscriptions/abc/resourceGroups/rg1/providers/Microsoft.Compute/virtualMachines/vm1"
    assert gc.parse_resource_id(rid) == ("abc", "rg1")
    assert gc.parse_resource_id("") == ("", "")


def test_severity_for_activity():
    assert gc.severity_for_activity({"status": {"value": "Failed"}}) == "High"
    assert gc.severity_for_activity({"level": "Warning"}) == "Medium"
    assert gc.severity_for_activity({"level": "Informational", "status": {"value": "Succeeded"}}) == "Low"


def test_severity_for_health():
    assert gc.severity_for_health("Unavailable") == "Critical"
    assert gc.severity_for_health("Degraded") == "High"
    assert gc.severity_for_health("Available") == "Low"


def test_build_timeline_newest_first_and_banded():
    activity = [
        {"operationName": {"localizedValue": "Deploy"}, "status": {"value": "Succeeded"}, "caller": "u@x", "eventTimestamp": "2026-07-09T10:00:00Z", "level": "Informational"},
        {"operationName": {"localizedValue": "Scale"}, "status": {"value": "Failed"}, "eventTimestamp": "2026-07-09T11:00:00Z", "level": "Error"},
    ]
    health = [{"properties": {"availabilityState": "Unavailable", "summary": "down", "occuredTime": "2026-07-09T11:05:00Z"}}]
    timeline = gc.build_timeline(activity, health)
    assert timeline[0]["source"] == "Resource Health"  # 11:05 newest
    assert timeline[0]["_band"] == "Critical"
    assert timeline[1]["signal"] == "Scale"
    assert timeline[1]["severity"] == "High"


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all gather_context tests passed")
