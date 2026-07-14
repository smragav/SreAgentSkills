"""
pattern_scan: Rank recurring incident repeat offenders over a window.

Azure SRE Agent Python tool. Uses the agent managed identity (ARM scope) to read
fired alerts and resource health degradations across accessible subscriptions,
aggregate them by resource, rank the repeat offenders, group them by resource
type, and print a report_data object as JSON ready to pipe into report_render.py.

    python pattern_scan.py [days] | python report_render.py

Heavy imports (azure-identity, requests) are lazy so the pure aggregation helpers
can be unit tested without them. See references/checks-catalog.md.
"""

import json
import sys
from datetime import datetime, timedelta, timezone

ARM_ENDPOINT = "https://management.azure.com"
SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
REPEAT_THRESHOLD = 3


def resource_type_from_id(resource_id):
    """Return a friendly provider/type from a resource id. Pure and testable."""
    parts = [p for p in (resource_id or "").split("/") if p]
    lower = [p.lower() for p in parts]
    if "providers" in lower:
        i = lower.index("providers")
        if i + 2 < len(parts):
            return f"{parts[i + 1]}/{parts[i + 2]}"
    return "unknown"


def _name(resource_id):
    return [p for p in (resource_id or "").split("/") if p][-1] if resource_id else ""


def severity_by_count(count):
    """Severity band from an incident count. Pure and testable."""
    if count >= 10:
        return "High"
    if count >= 5:
        return "Medium"
    return "Low"


def aggregate(alerts, health_events):
    """Aggregate alerts and health degradations by resource. Pure and testable.

    alerts, health_events: lists of resource ids.
    Returns {resource_id: {name, type, alerts, health, count}}.
    """
    agg = {}
    for rid in alerts:
        if not rid:
            continue
        entry = agg.setdefault(rid.lower(), {"name": _name(rid), "type": resource_type_from_id(rid), "alerts": 0, "health": 0})
        entry["alerts"] += 1
    for rid in health_events:
        if not rid:
            continue
        entry = agg.setdefault(rid.lower(), {"name": _name(rid), "type": resource_type_from_id(rid), "alerts": 0, "health": 0})
        entry["health"] += 1
    for entry in agg.values():
        entry["count"] = entry["alerts"] + entry["health"]
    return agg


def repeat_offenders(agg, threshold=REPEAT_THRESHOLD):
    """Return offenders at or above the threshold, highest count first. Pure."""
    offenders = [entry for entry in agg.values() if entry["count"] >= threshold]
    offenders.sort(key=lambda e: e["count"], reverse=True)
    return offenders


def build_report_data(agg, window_label, subs_scanned, threshold, notes):
    offenders = repeat_offenders(agg, threshold)
    findings = []
    for entry in offenders:
        severity = severity_by_count(entry["count"])
        findings.append({
            "resource": entry["name"], "resource_type": entry["type"], "incidents": entry["count"],
            "signals": f"{entry['alerts']} alert(s), {entry['health']} health degradation(s)",
            "recommendation": "Review redundancy and dependencies for a resource that keeps degrading; tune the workload or threshold for one that keeps alerting.",
            "severity": severity, "_band": severity, "_sort": entry["count"],
        })
    findings.sort(key=lambda f: f["_sort"], reverse=True)
    total_incidents = sum(entry["count"] for entry in agg.values())

    by_type = {}
    for entry in agg.values():
        by_type[entry["type"]] = by_type.get(entry["type"], 0) + entry["count"]
    type_items = sorted(({"name": k, "value": v} for k, v in by_type.items()), key=lambda i: i["value"], reverse=True)[:10]
    top_items = [{"name": f["resource"], "value": f["incidents"]} for f in findings[:10]]

    return {
        "title": "Recurring Incident Patterns",
        "subtitle": "Repeat offenders over the window.",
        "meta": {"window": window_label, "scope": f"{subs_scanned} subscription(s)", "source": "Azure Monitor alerts and Resource Health"},
        "summary_cards": [
            {"label": "Total incidents", "value": f"{total_incidents:,}"},
            {"label": "Repeat offenders", "value": f"{len(offenders):,}", "sub": f"{threshold}+ incidents"},
            {"label": "Resources affected", "value": f"{len(agg):,}"},
            {"label": "Window", "value": window_label},
        ],
        "charts": [
            {"title": "Incidents by resource type", "unit": "incidents", "items": type_items},
            {"title": "Top repeat offenders", "unit": "incidents", "items": top_items},
        ],
        "findings": {
            "title": "Repeat offenders",
            "columns": ["resource", "resource_type", "incidents", "signals", "recommendation", "severity"],
            "rows": findings,
        },
        "method_notes": notes + [
            f"Window: {window_label}. Repeat threshold: {threshold} incidents.",
            "Incident count is fired alerts plus resource health degradations over the window.",
        ],
    }


def _headers():
    from azure.identity import DefaultAzureCredential

    token = DefaultAzureCredential().get_token(f"{ARM_ENDPOINT}/.default").token
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _list_subscriptions(headers):
    import requests

    url = f"{ARM_ENDPOINT}/subscriptions?api-version=2022-12-01"
    subs = []
    while url:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        body = response.json()
        subs.extend(item["subscriptionId"] for item in body.get("value", []) if item.get("state") in (None, "Enabled"))
        url = body.get("nextLink")
    return subs


def _read_alerts(headers, subscription, time_range):
    import requests

    url = f"{ARM_ENDPOINT}/subscriptions/{subscription}/providers/Microsoft.AlertsManagement/alerts?api-version=2019-05-05-preview&timeRange={time_range}"
    ids, pages = [], 0
    while url and pages < 40:
        response = requests.get(url, headers=headers, timeout=120)
        response.raise_for_status()
        body = response.json()
        for alert in body.get("value", []):
            essentials = (alert.get("properties", {}) or {}).get("essentials", {}) or {}
            ids.append(essentials.get("targetResource", ""))
        url = body.get("nextLink")
        pages += 1
    return ids


def _read_health(headers, subscription, start):
    import requests

    flt = f"eventTimestamp ge '{start}'"
    url = f"{ARM_ENDPOINT}/subscriptions/{subscription}/providers/microsoft.insights/eventtypes/management/values?api-version=2015-04-01&$filter={flt}"
    ids, pages = [], 0
    while url and pages < 40:
        response = requests.get(url, headers=headers, timeout=120)
        response.raise_for_status()
        body = response.json()
        for event in body.get("value", []):
            if ((event.get("category") or {}).get("value") or "").lower() != "resourcehealth":
                continue
            status = ((event.get("properties") or {}).get("currentHealthStatus") or "").lower()
            if status in ("unavailable", "degraded"):
                ids.append(event.get("resourceId", ""))
        url = body.get("nextLink")
        pages += 1
    return ids


def main(days: int = 30) -> dict:
    time_range = "1d" if int(days) <= 1 else ("7d" if int(days) <= 7 else "30d")
    headers = _headers()
    notes = []
    start = (datetime.now(timezone.utc) - timedelta(days=int(days))).replace(microsecond=0).isoformat()
    try:
        subs = _list_subscriptions(headers)
    except Exception as error:  # noqa: BLE001
        return build_report_data({}, time_range, 0, REPEAT_THRESHOLD, [f"Could not list subscriptions ({error})."])

    alerts, health = [], []
    for sub in subs:
        try:
            alerts.extend(_read_alerts(headers, sub, time_range))
        except Exception:  # noqa: BLE001
            notes.append(f"Alerts not read for subscription {sub}.")
        try:
            health.extend(_read_health(headers, sub, start))
        except Exception:  # noqa: BLE001
            notes.append(f"Resource health not read for subscription {sub}.")

    return build_report_data(aggregate(alerts, health), time_range, len(subs), REPEAT_THRESHOLD, notes)


if __name__ == "__main__":
    window = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    print(json.dumps(main(window)))
