"""Unit tests for the pure helpers in tag_compliance (no Azure calls)."""

import tag_compliance as tc


def test_normalize_key():
    assert tc.normalize_key("Cost-Center") == "costcenter"
    assert tc.normalize_key("cost_center") == "costcenter"
    assert tc.normalize_key("OWNER") == "owner"


def test_missing_tags_tolerant():
    tags = {"Owner": "team", "CostCenter": "1234"}
    assert tc.missing_tags(tags, ["owner", "environment", "cost-center"]) == ["environment"]
    assert tc.missing_tags({}, ["owner"]) == ["owner"]


def test_severity_for_missing():
    assert tc.severity_for_missing(["owner"]) == "High"
    assert tc.severity_for_missing(["environment"]) == "Medium"


def test_classify_resource():
    resource = {"name": "r1", "type": "x", "subscriptionId": "a", "tags": {"environment": "prod"}}
    finding = tc.classify_resource(resource, ["owner", "environment"])
    assert finding["missing_tags"] == "owner"
    assert finding["severity"] == "High"
    assert tc.classify_resource({"name": "r2", "tags": {"owner": "t", "environment": "p"}}, ["owner", "environment"]) is None


def test_build_report_data_compliance_percent():
    resources = [
        {"name": "r1", "type": "x", "subscriptionId": "a", "tags": {"owner": "t", "environment": "p", "cost-center": "1"}},
        {"name": "r2", "type": "x", "subscriptionId": "a", "tags": {}},
    ]
    data = tc.build_report_data(resources, ["owner", "environment", "cost-center"], 1, {"a": "Sub A"}, [])
    assert data["summary_cards"][0]["value"] == "50.0%"
    assert data["summary_cards"][2]["value"] == "1"  # one missing owner


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all tag_compliance tests passed")
