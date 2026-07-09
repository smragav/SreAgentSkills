"""Unit tests for the pure helpers in backup_coverage (no Azure calls)."""

from datetime import datetime, timezone, timedelta

import backup_coverage as bc

NOW = datetime(2026, 7, 9, tzinfo=timezone.utc)


def _vm(name, sub="a"):
    return {"name": name, "id": f"/subscriptions/{sub}/rg/{name}", "subscriptionId": sub, "resourceGroup": "rg"}


def test_unprotected_is_high():
    finding = bc.classify_vm(_vm("vm1"), {}, 3, NOW)
    assert finding["state"] == "Unprotected"
    assert finding["severity"] == "High"


def test_protected_healthy_recent_is_not_a_finding():
    vm = _vm("vm1")
    protected = {vm["id"].lower(): {"lastBackup": (NOW - timedelta(days=1)).isoformat(), "health": "Passed"}}
    assert bc.classify_vm(vm, protected, 3, NOW) is None


def test_stale_backup_is_high():
    vm = _vm("vm1")
    protected = {vm["id"].lower(): {"lastBackup": (NOW - timedelta(days=10)).isoformat(), "health": "Passed"}}
    finding = bc.classify_vm(vm, protected, 3, NOW)
    assert finding["state"] == "Stale"


def test_unhealthy_backup_is_high():
    vm = _vm("vm1")
    protected = {vm["id"].lower(): {"lastBackup": (NOW - timedelta(days=1)).isoformat(), "health": "ActionRequired"}}
    finding = bc.classify_vm(vm, protected, 3, NOW)
    assert finding["state"] == "Unhealthy"


def test_coverage_summary_counts():
    vms = [_vm("vm1"), _vm("vm2"), _vm("vm3")]
    protected = {vms[0]["id"].lower(): {"lastBackup": (NOW - timedelta(days=1)).isoformat(), "health": "Passed"}}
    findings, counts = bc.coverage_summary(vms, protected, 3, NOW)
    assert counts["total"] == 3
    assert counts["protected_healthy"] == 1
    assert counts["unprotected"] == 2
    assert counts["coverage_percent"] == 33.3


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all backup_coverage tests passed")
