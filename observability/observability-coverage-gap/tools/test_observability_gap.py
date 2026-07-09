"""Unit tests for the pure helpers in observability_gap (no Azure calls)."""

import observability_gap as og


def _res(name="vm1", sub="a", rg="rg1"):
    return {"name": name, "id": f"/subscriptions/{sub}/resourcegroups/{rg}/providers/microsoft.compute/virtualmachines/{name}",
            "type": "microsoft.compute/virtualmachines", "subscriptionId": sub, "resourceGroup": rg}


def test_alert_coverage_by_exact_id():
    res = _res()
    covered = {res["id"].lower()}
    assert og.is_alert_covered(res, covered, set(), set()) is True


def test_alert_coverage_by_resource_group_and_subscription():
    res = _res(sub="a", rg="rg1")
    assert og.is_alert_covered(res, set(), {"/subscriptions/a/resourcegroups/rg1"}, set()) is True
    assert og.is_alert_covered(res, set(), set(), {"/subscriptions/a"}) is True
    assert og.is_alert_covered(res, set(), set(), set()) is False


def test_classify_resource_flags_both_gaps():
    res = _res()
    finding = og.classify_resource(res, set(), True, set(), set(), set())
    assert "diagnostic settings" in finding["missing"]
    assert "metric alert" in finding["missing"]
    assert finding["severity"] == "High"


def test_classify_resource_none_when_fully_wired():
    res = _res()
    diag = {res["id"].lower()}
    covered = {res["id"].lower()}
    assert og.classify_resource(res, diag, True, covered, set(), set()) is None


def test_subscription_findings_for_missing_wiring():
    findings = og.subscription_findings({"a"}, action_group_subs=set(), workspace_subs={"a"}, sub_names={"a": "Sub A"})
    assert len(findings) == 1
    assert findings[0]["missing"] == "no action group"
    assert findings[0]["severity"] == "High"


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all observability_gap tests passed")
