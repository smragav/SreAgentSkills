"""Unit tests for the pure helpers in pattern_scan (no Azure calls)."""

import pattern_scan as ps

VM = "/subscriptions/a/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm1"
DB = "/subscriptions/a/resourceGroups/rg/providers/Microsoft.Sql/servers/s/databases/db1"


def test_resource_type_from_id():
    assert ps.resource_type_from_id(VM) == "Microsoft.Compute/virtualMachines"
    assert ps.resource_type_from_id("") == "unknown"


def test_severity_by_count():
    assert ps.severity_by_count(12) == "High"
    assert ps.severity_by_count(6) == "Medium"
    assert ps.severity_by_count(3) == "Low"


def test_aggregate_counts_alerts_and_health():
    agg = ps.aggregate([VM, VM, DB], [VM])
    assert agg[VM.lower()]["alerts"] == 2
    assert agg[VM.lower()]["health"] == 1
    assert agg[VM.lower()]["count"] == 3
    assert agg[DB.lower()]["count"] == 1


def test_repeat_offenders_threshold_and_order():
    agg = ps.aggregate([VM, VM, VM, DB], [VM, DB])
    offenders = ps.repeat_offenders(agg, threshold=3)
    assert len(offenders) == 1  # only VM has >= 3 (4); DB has 2
    assert offenders[0]["name"] == "vm1"


def test_build_report_data_offender_count():
    agg = ps.aggregate([VM] * 5, [VM])
    data = ps.build_report_data(agg, "30d", 1, 3, [])
    assert data["summary_cards"][1]["value"] == "1"  # one repeat offender
    assert data["findings"]["rows"][0]["incidents"] == 6


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all pattern_scan tests passed")
