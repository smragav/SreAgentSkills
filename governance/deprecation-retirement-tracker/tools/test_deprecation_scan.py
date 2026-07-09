"""Unit tests for the pure predicates in deprecation_scan (no Azure calls)."""

import deprecation_scan as ds


def test_k8s_minor_and_severity():
    assert ds.k8s_minor("1.26.10") == 26
    assert ds.k8s_minor("bad") is None
    assert ds.k8s_severity(26, floor=28) == "Medium"
    assert ds.k8s_severity(24, floor=28) == "High"
    assert ds.k8s_severity(30, floor=28) is None


def test_eol_runtime():
    assert ds.eol_runtime("PYTHON|3.7")[0] == "Python 3.7"
    assert ds.eol_runtime("NODE|18-lts")[1] == "Medium"
    assert ds.eol_runtime("PYTHON|3.12") is None


def test_eol_image():
    assert ds.eol_image("WindowsServer", "2012-datacenter")[0] == "Windows Server 2012"
    assert ds.eol_image("UbuntuServer", "18.04-LTS")[1] == "High"
    assert ds.eol_image("0001-com-ubuntu-server-jammy", "22_04-lts") is None


def test_scanners_produce_findings():
    apps = ds.scan_app_service([{"name": "app1", "subscriptionId": "a", "fx": "PYTHON|3.7"}])
    assert apps[0]["category"] == "App Service runtime"
    retired = ds.scan_retired_types([{"name": "pg1", "type": "microsoft.dbforpostgresql/servers", "subscriptionId": "a"}])
    assert retired[0]["severity"] == "High"
    aks = ds.scan_aks([{"name": "k1", "subscriptionId": "a", "kubernetesVersion": "1.24.0"}])
    assert aks[0]["category"] == "AKS version"


def test_build_report_data_categories():
    findings = ds.scan_app_service([{"name": "app1", "subscriptionId": "a", "fx": "PYTHON|3.7"}])
    data = ds.build_report_data(findings, 1, [])
    assert data["summary_cards"][0]["value"] == "1"
    assert data["charts"][1]["items"][0]["name"] == "App Service runtime"


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all deprecation_scan tests passed")
