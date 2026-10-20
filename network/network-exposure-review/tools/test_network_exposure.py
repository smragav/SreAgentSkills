"""Unit tests for the pure helpers in network_exposure (no Azure calls)."""

import network_exposure as ne


def test_source_is_internet():
    assert ne.source_is_internet("*", None) is True
    assert ne.source_is_internet("Internet", None) is True
    assert ne.source_is_internet("10.0.0.0/8", None) is False
    assert ne.source_is_internet("VirtualNetwork", ["0.0.0.0/0"]) is True


def test_port_in_spec():
    assert ne.port_in_spec(22, "22") is True
    assert ne.port_in_spec(22, "*") is True
    assert ne.port_in_spec(3389, "3000-4000") is True
    assert ne.port_in_spec(22, "80") is False


def test_classify_open_ports():
    assert ne.classify_open_ports(["*"])[0] == "Critical"
    assert ne.classify_open_ports(["3389"])[0] == "Critical"
    assert ne.classify_open_ports(["1433"])[0] == "High"
    assert ne.classify_open_ports(["8080"])[0] == "Medium"


def test_classify_nsg_rule_internet_mgmt():
    row = {"name": "nsg1", "subscriptionId": "a", "ruleName": "rdp", "src": "*", "srcs": None, "portRange": "3389", "portRanges": None}
    finding = ne.classify_nsg_rule(row)
    assert finding["severity"] == "Critical"
    assert "management ports" in finding["detail"]


def test_classify_nsg_rule_internal_source_is_none():
    row = {"name": "nsg1", "subscriptionId": "a", "ruleName": "x", "src": "10.0.0.0/8", "srcs": None, "portRange": "3389", "portRanges": None}
    assert ne.classify_nsg_rule(row) is None


def test_build_report_data_counts_critical():
    row = {"name": "nsg1", "subscriptionId": "a", "ruleName": "rdp", "src": "*", "srcs": None, "portRange": "22", "portRanges": None}
    findings = [ne.classify_nsg_rule(row)]
    data = ne.build_report_data(findings, 1, [])
    assert data["summary_cards"][1]["value"] == "1"  # one critical
    assert data["title"] == "Network Exposure Review"


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all network_exposure tests passed")
