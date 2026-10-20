"""Unit tests for the pure evaluate functions in appservice_review (no Azure calls)."""

import appservice_review as ar


def test_site_https_and_tls():
    row = {"name": "s1", "subscriptionId": "a", "kind": "app", "properties": {"httpsOnly": False, "siteConfig": {"minTlsVersion": "1.0"}}}
    checks = [f["check"] for f in ar.evaluate_site(row)]
    assert "HTTPS not enforced" in checks
    assert "Minimum TLS below 1.2" in checks


def test_site_alwayson_and_healthcheck_skipped_without_siteconfig():
    row = {"name": "s1", "subscriptionId": "a", "kind": "app", "properties": {"httpsOnly": True}}
    assert ar.evaluate_site(row) == []  # no siteConfig, checks skipped


def test_site_function_app_skips_alwayson():
    row = {"name": "f1", "subscriptionId": "a", "kind": "functionapp", "properties": {"httpsOnly": True, "siteConfig": {"alwaysOn": False, "healthCheckPath": "/health"}}}
    checks = [f["check"] for f in ar.evaluate_site(row)]
    assert "Always On disabled" not in checks


def test_plan_free_tier_and_zone():
    free = {"name": "p1", "subscriptionId": "a", "sku": {"tier": "Free"}, "properties": {}}
    assert ar.evaluate_plan(free)[0]["severity"] == "Medium"
    std = {"name": "p2", "subscriptionId": "a", "sku": {"tier": "Standard"}, "properties": {"zoneRedundant": False}}
    assert ar.evaluate_plan(std)[0]["check"] == "Plan not zone redundant"


def test_containerapp_checks():
    row = {"name": "c1", "subscriptionId": "a", "properties": {"configuration": {"ingress": {"allowInsecure": True}}, "template": {"scale": {"maxReplicas": 1}, "containers": [{"name": "x"}]}}}
    checks = [f["check"] for f in ar.evaluate_containerapp(row)]
    assert "Insecure ingress allowed" in checks
    assert "No scale out (maxReplicas is 1)" in checks
    assert "No health probes defined" in checks


def test_build_report_data_categories():
    findings = ar.evaluate_plan({"name": "p1", "subscriptionId": "a", "sku": {"tier": "Free"}, "properties": {}})
    data = ar.build_report_data(findings, 1, 9, [])
    assert data["charts"][1]["items"][0]["name"] == "App Service plan"


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all appservice_review tests passed")
