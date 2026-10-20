"""Unit tests for the pure helpers in readiness_check (no Azure calls)."""

import readiness_check as rc


def test_verdict_for():
    assert rc.verdict_for(["High"]) == "NO-GO"
    assert rc.verdict_for(["Critical", "Medium"]) == "NO-GO"
    assert rc.verdict_for(["Medium"]) == "CAUTION"
    assert rc.verdict_for([]) == "GO"


def test_verdicts_overall_is_worst():
    findings = [
        {"category": "Reliability", "severity": "High"},
        {"category": "Exposure", "severity": "Medium"},
    ]
    v = rc.verdicts(findings)
    assert v["Reliability"] == "NO-GO"
    assert v["Exposure"] == "CAUTION"
    assert v["Capacity"] == "GO"
    assert v["overall"] == "NO-GO"


def test_classify_ports():
    assert rc.classify_ports(["*"])[0] == "Critical"
    assert rc.classify_ports(["22"])[0] == "Critical"
    assert rc.classify_ports(["1433"])[0] == "High"
    assert rc.classify_ports(["8080"])[0] == "Medium"


def test_source_is_internet():
    assert rc.source_is_internet("*", None) is True
    assert rc.source_is_internet("10.0.0.0/8", None) is False


def test_build_report_data_verdict_cards():
    findings = [rc._finding("Reliability", {"name": "vm1", "subscriptionId": "a"}, "no zone", "fix", "High")]
    data = rc.build_report_data(findings, "a", [])
    assert data["summary_cards"][0]["value"] == "NO-GO"  # overall
    assert data["summary_cards"][1]["value"] == "NO-GO"  # reliability
    assert data["summary_cards"][2]["value"] == "GO"     # exposure clean


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all readiness_check tests passed")
