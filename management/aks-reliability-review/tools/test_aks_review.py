"""Unit tests for the pure helpers in aks_review (no Azure calls)."""

import aks_review as ar


def _cluster(**props):
    base = {
        "name": "k1", "subscriptionId": "a", "resourceGroup": "rg1", "sku": {"tier": "Standard"},
        "properties": {
            "kubernetesVersion": "1.29.0",
            "agentPoolProfiles": [{"name": "sys", "mode": "System", "count": 3, "availabilityZones": ["1", "2", "3"]}],
            "apiServerAccessProfile": {"enablePrivateCluster": True},
            "autoUpgradeProfile": {"upgradeChannel": "patch"},
            "addonProfiles": {"omsagent": {"enabled": True}},
            "networkProfile": {"networkPolicy": "azure"},
            "aadProfile": {"managed": True}, "enableRBAC": True,
        },
    }
    base["properties"].update(props)
    return base


def test_healthy_cluster_has_no_findings():
    assert ar.evaluate_cluster(_cluster()) == []


def test_old_version_flagged_high():
    findings = ar.evaluate_cluster(_cluster(kubernetesVersion="1.24.0"))
    assert any(f["severity"] == "High" and "below the supported floor" in f["check"] for f in findings)


def test_open_control_plane_and_no_zones():
    cluster = _cluster(
        apiServerAccessProfile={},
        agentPoolProfiles=[{"name": "np", "mode": "System", "count": 1, "availabilityZones": []}],
    )
    checks = [f["check"] for f in ar.evaluate_cluster(cluster)]
    assert any("Control plane open" in c for c in checks)
    assert any("no availability zones" in c for c in checks)
    assert any("fewer than two nodes" in c for c in checks)


def test_free_tier_flagged():
    cluster = _cluster()
    cluster["sku"] = {"tier": "Free"}
    assert any("no uptime SLA" in f["check"] for f in ar.evaluate_cluster(cluster))


def test_build_report_data_counts():
    data = ar.build_report_data([_cluster(kubernetesVersion="1.24.0")], [])
    assert data["summary_cards"][0]["value"] == "1"
    assert int(data["summary_cards"][2]["value"]) >= 1  # at least one High


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all aks_review tests passed")
