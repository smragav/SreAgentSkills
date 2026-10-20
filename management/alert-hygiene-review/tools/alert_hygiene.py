"""
alert_hygiene: Find noisy and misconfigured Azure Monitor alert rules.

Azure SRE Agent Python tool. Uses the agent managed identity (ARM scope) to read
the fired alert history over a window, group it by rule, compute the fire count,
the auto resolved share, and the unacknowledged share per rule, read the disabled
rules with Azure Resource Graph, and print a report_data object as JSON ready to
pipe into report_render.py.

    python alert_hygiene.py [days] | python report_render.py

Heavy imports (azure-identity, requests) are lazy so the pure aggregation and
classification helpers can be unit tested without them. See references/checks-catalog.md.
"""

import json
import sys

ARM_ENDPOINT = "https://management.azure.com"
NOISY_DEFAULT = 20
SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def _sev_number(sev):
    try:
        return int(str(sev).lower().replace("sev", ""))
    except ValueError:
        return 4


def aggregate_alerts(alerts):
    """Group fired alerts by rule. Returns {rule: stats}. Pure and testable.

    stats: count, resolved, new, min_sev (lowest Sev number, highest urgency),
    and a display name.
    """
    stats = {}
    for alert in alerts:
        essentials = (alert.get("properties", {}) or {}).get("essentials", {}) or {}
        rule = essentials.get("alertRule") or alert.get("name") or "unknown"
        entry = stats.setdefault(rule, {"count": 0, "resolved": 0, "new": 0, "min_sev": 4, "name": rule})
        entry["count"] += 1
        if (essentials.get("monitorCondition") or "").lower() == "resolved" or (essentials.get("alertState") or "").lower() == "closed":
            entry["resolved"] += 1
        if (essentials.get("alertState") or "").lower() == "new":
            entry["new"] += 1
        entry["min_sev"] = min(entry["min_sev"], _sev_number(essentials.get("severity", "Sev4")))
    return stats


def classify_rule(rule, stats, noisy_threshold):
    """Return a finding for a rule that trips a hygiene signal, or None. Pure."""
    count = stats["count"]
    resolved_share = stats["resolved"] / count if count else 0.0
    new_share = stats["new"] / count if count else 0.0
    issues, severity = [], None

    def bump(level):
        order = ["Low", "Medium", "High", "Critical"]
        nonlocal severity
        if severity is None or order.index(level) > order.index(severity):
            severity = level

    if count >= noisy_threshold:
        issues.append(f"fired {count} times in the window")
        bump("High" if count >= 2 * noisy_threshold else "Medium")
    if stats["min_sev"] <= 1 and resolved_share >= 0.8 and count >= 5:
        issues.append("high severity but usually auto resolves without action")
        bump("Medium")
    if new_share >= 0.5 and count >= 5:
        issues.append("most alerts left unacknowledged")
        bump("Medium")
    if not issues:
        return None

    recommendations = {
        "fired": "Widen the threshold, use a dynamic threshold, lengthen the aggregation window, or split the scope.",
        "high severity": "Lower the severity to match the real urgency, or make the condition more specific.",
        "unacknowledged": "Confirm the rule routes to an action group a team watches, or retire it.",
    }
    tip = recommendations["fired"] if count >= noisy_threshold else (
        recommendations["high severity"] if stats["min_sev"] <= 1 else recommendations["unacknowledged"]
    )
    return {
        "rule": stats["name"],
        "fired": count,
        "auto_resolved": f"{resolved_share * 100:.0f}%",
        "unacknowledged": f"{new_share * 100:.0f}%",
        "issue": "; ".join(issues),
        "recommendation": tip,
        "severity": severity,
        "_band": severity,
        "_sort": count,
    }


def severity_chart(alerts):
    counts = {}
    for alert in alerts:
        essentials = (alert.get("properties", {}) or {}).get("essentials", {}) or {}
        sev = essentials.get("severity", "Sev4")
        counts[sev] = counts.get(sev, 0) + 1
    return [{"name": sev, "value": counts[sev]} for sev in sorted(counts)]


def build_report_data(alerts, disabled_rules, window_label, subs_scanned, noisy_threshold, notes):
    stats = aggregate_alerts(alerts)
    findings = []
    for rule, rule_stats in stats.items():
        finding = classify_rule(rule, rule_stats, noisy_threshold)
        if finding:
            findings.append(finding)
    for rule in disabled_rules:
        findings.append({
            "rule": rule.get("name", ""), "fired": 0, "auto_resolved": "", "unacknowledged": "",
            "issue": "alert rule is disabled", "recommendation": "Re enable the rule or delete it so the intent is clear.",
            "severity": "Medium", "_band": "Medium", "_sort": 0,
        })
    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f["severity"], 9), -f["_sort"]))
    noisy = sum(1 for f in findings if "fired" in f["issue"])
    top = sorted(({"name": s["name"], "value": s["count"]} for s in stats.values()), key=lambda i: i["value"], reverse=True)[:10]
    return {
        "title": "Alert Hygiene Review",
        "subtitle": "Alert noise and tuning over the window.",
        "meta": {"window": window_label, "scope": f"{subs_scanned} subscription(s)", "source": "Azure Monitor alerts"},
        "summary_cards": [
            {"label": "Alerts fired", "value": f"{len(alerts):,}"},
            {"label": "Noisy rules", "value": f"{noisy:,}"},
            {"label": "Rules analyzed", "value": f"{len(stats):,}"},
            {"label": "Disabled rules", "value": f"{len(disabled_rules):,}"},
        ],
        "charts": [
            {"title": "Alerts by severity", "unit": "alerts", "items": severity_chart(alerts)},
            {"title": "Noisiest rules", "unit": "fires", "items": top},
        ],
        "findings": {
            "title": "Alert rules to tune",
            "columns": ["rule", "fired", "auto_resolved", "unacknowledged", "issue", "recommendation", "severity"],
            "rows": findings,
        },
        "method_notes": notes + [
            f"Window: {window_label}. Noisy threshold: {noisy_threshold} fires.",
            "A rule that trips more than one signal appears once, at the highest severity among them.",
        ],
    }


def _headers():
    from agent_identity import agent_token

    token = agent_token(f"{ARM_ENDPOINT}/.default")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _list_subscriptions(headers):
    import requests

    url = f"{ARM_ENDPOINT}/subscriptions?api-version=2022-12-01"
    subs = []
    while url:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        body = response.json()
        subs.extend(item["subscriptionId"] for item in body.get("value", []))
        url = body.get("nextLink")
    return subs


def _read_alerts(headers, subscription, time_range):
    import requests

    url = (
        f"{ARM_ENDPOINT}/subscriptions/{subscription}/providers/Microsoft.AlertsManagement/alerts"
        f"?api-version=2019-05-05-preview&timeRange={time_range}"
    )
    alerts, pages = [], 0
    while url and pages < 40:
        response = requests.get(url, headers=headers, timeout=120)
        response.raise_for_status()
        body = response.json()
        alerts.extend(body.get("value", []))
        url = body.get("nextLink")
        pages += 1
    return alerts


def _run_graph(headers, query):
    import requests

    url = f"{ARM_ENDPOINT}/providers/Microsoft.ResourceGraph/resources?api-version=2022-10-01"
    rows, skip_token = [], None
    while True:
        payload = {"query": query, "options": {"resultFormat": "objectArray", "top": 1000}}
        if skip_token:
            payload["options"]["$skipToken"] = skip_token
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        body = response.json()
        rows.extend(body.get("data", []))
        skip_token = body.get("$skipToken")
        if not skip_token:
            return rows


def main(days: int = 7) -> dict:
    time_range = "1d" if int(days) <= 1 else ("30d" if int(days) >= 30 else "7d")
    headers = _headers()
    notes = []
    subs = []
    try:
        subs = _list_subscriptions(headers)
    except Exception as error:  # noqa: BLE001
        notes.append(f"Could not list subscriptions ({error}).")

    alerts = []
    for sub in subs:
        try:
            alerts.extend(_read_alerts(headers, sub, time_range))
        except Exception:  # noqa: BLE001
            notes.append(f"Alert history not read for subscription {sub}.")

    try:
        disabled = _run_graph(headers, "resources | where type in~ ('microsoft.insights/metricalerts','microsoft.insights/scheduledqueryrules') | extend enabled = tostring(properties.enabled) | where enabled =~ 'false' | project name, id, resourceGroup, subscriptionId")
    except Exception as error:  # noqa: BLE001
        disabled = []
        notes.append(f"Disabled rules not read ({error}).")

    return build_report_data(alerts, disabled, time_range, len(subs), NOISY_DEFAULT, notes)


if __name__ == "__main__":
    window = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    print(json.dumps(main(window)))
