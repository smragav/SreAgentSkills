"""Unit tests for the pure helpers in waf_assess (no Azure calls)."""

import waf_assess as wa


def test_rating():
    assert wa.rating(95) == "Excellent"
    assert wa.rating(80) == "Good"
    assert wa.rating(60) == "Fair"
    assert wa.rating(30) == "Poor"
    assert wa.rating(None) == "Not assessed"


def test_score_pillars_weighted():
    assessed = [
        {"pillar": "Reliability", "severity": "High", "applicable": 10, "failing": 5},   # 0.5 pass, weight 3
        {"pillar": "Reliability", "severity": "Medium", "applicable": 10, "failing": 0},  # 1.0 pass, weight 2
    ]
    scores = wa.score_pillars(assessed)
    # (3*0.5 + 2*1.0) / (3+2) = 3.5/5 = 0.7 -> 70
    assert scores["Reliability"] == 70
    assert scores["Security"] is None  # not assessed


def test_score_pillars_skips_zero_applicable():
    assessed = [{"pillar": "Security", "severity": "High", "applicable": 0, "failing": 0}]
    assert wa.score_pillars(assessed)["Security"] is None


def test_build_report_data_five_pillar_cards():
    assessed = [{"pillar": "Reliability", "name": "x", "severity": "High", "applicable": 4, "failing": 1, "recommendation": "y"}]
    data = wa.build_report_data(assessed, 2, [])
    assert data["title"] == "Well-Architected Review"
    assert len(data["summary_cards"]) == 5
    assert data["summary_cards"][0]["label"] == "Reliability"
    assert data["summary_cards"][0]["value"] == "75"  # 3/4 pass -> 75
    assert data["findings"]["rows"][0]["pass_rate"] == "75%"


def test_build_report_data_marks_unassessed_pillars():
    data = wa.build_report_data([], 1, [])
    values = {c["label"]: c["value"] for c in data["summary_cards"]}
    assert values["Security"] == "n/a"


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all waf_assess tests passed")
