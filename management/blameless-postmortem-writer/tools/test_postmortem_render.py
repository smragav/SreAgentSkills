"""Unit tests for the pure render helpers in postmortem_render (no file or network)."""

import postmortem_render as pm

SAMPLE = {
    "title": "Checkout latency",
    "severity": "Sev2",
    "status": "Resolved",
    "summary": "Checkout slowed for 40 minutes.",
    "impact": {"duration": "40 minutes", "scope": "Checkout API", "customer": "Timeouts for some users"},
    "timeline": [{"time": "10:02 UTC", "event": "Config change deployed"}],
    "root_cause": "Pool too small (trigger); no guardrail (weakness).",
    "contributing_factors": ["No saturation alert"],
    "detection": "Latency alert fired.",
    "resolution": "Rolled back the change.",
    "lessons": {"went_well": ["Alert caught it"], "went_wrong": ["No guardrail"], "got_lucky": ["Low traffic"]},
    "action_items": [{"action": "Add saturation alert", "owner": "Platform", "due": "2026-07-23", "type": "Detect"}],
}


def test_render_includes_all_sections():
    doc = pm.render_html(SAMPLE)
    for text in ["Checkout latency", "Summary", "Impact", "Timeline", "Root cause", "Contributing factors", "Detection", "Resolution", "Lessons", "Action items"]:
        assert text in doc, f"missing section: {text}"


def test_render_is_blameless_callout_present():
    doc = pm.render_html(SAMPLE)
    assert "blameless review" in doc
    assert "Add saturation alert" in doc
    assert "Detect" in doc


def test_render_handles_sparse_input():
    doc = pm.render_html({"title": "Minimal"})
    assert "Minimal" in doc
    assert "Summary" not in doc  # omitted when empty


def test_action_item_type_colour():
    doc = pm.render_html(SAMPLE)
    assert pm.ACTION_CLASS["Detect"] in doc
    assert "Detect" in doc


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all postmortem_render tests passed")
