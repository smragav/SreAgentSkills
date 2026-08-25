"""
gather_context: Collect triage evidence for one affected Azure resource.

Azure SRE Agent Python tool. Uses the agent managed identity (ARM scope) to read
Azure Resource Health (current and recent), the Activity Log changes over a
window for the resource's resource group, and the neighbouring resources, then
prints an evidence object as JSON. The skill reasons over this evidence to a
probable cause and assembles the incident report.

    python gather_context.py "<resource id>" [hours]

Heavy imports (azure-identity, requests) are lazy so the pure parsing and
timeline helpers can be unit tested without them. See references/triage-method.md.
"""

import json
import sys
from datetime import datetime, timedelta, timezone

ARM_ENDPOINT = "https://management.azure.com"


def parse_resource_id(resource_id):
    """Return (subscription, resource_group) from a resource id. Pure."""
    parts = [p for p in (resource_id or "").split("/") if p]
    lower = [p.lower() for p in parts]
    sub = rg = ""
    if "subscriptions" in lower:
        i = lower.index("subscriptions")
        sub = parts[i + 1] if i + 1 < len(parts) else ""
    if "resourcegroups" in lower:
        i = lower.index("resourcegroups")
        rg = parts[i + 1] if i + 1 < len(parts) else ""
    return sub, rg


def severity_for_activity(event):
    """Band for an Activity Log event. Pure and testable."""
    level = (event.get("level") or "").lower()
    status = ((event.get("status") or {}).get("value") or "").lower()
    if status == "failed" or level in ("critical", "error"):
        return "High"
    if level == "warning":
        return "Medium"
    return "Low"


def severity_for_health(state):
    """Band for a Resource Health availability state. Pure and testable."""
    value = (state or "").lower()
    if value == "unavailable":
        return "Critical"
    if value == "degraded":
        return "High"
    return "Low"


def build_timeline(activity_events, health_statuses):
    """Merge changes and health transitions into one timeline, newest first. Pure."""
    timeline = []
    for event in activity_events:
        operation = (event.get("operationName") or {})
        signal = operation.get("localizedValue") or operation.get("value") or "operation"
        status = (event.get("status") or {}).get("value", "")
        caller = event.get("caller", "")
        detail = " ".join(part for part in [status, "by " + caller if caller else ""] if part).strip()
        timeline.append({
            "time": event.get("eventTimestamp", ""),
            "source": "Activity log",
            "signal": signal,
            "detail": detail,
            "severity": severity_for_activity(event),
        })
    for status in health_statuses:
        props = status.get("properties", status)
        state = props.get("availabilityState", "")
        timeline.append({
            "time": props.get("occuredTime") or props.get("reportedTime", ""),
            "source": "Resource Health",
            "signal": state or "health",
            "detail": props.get("summary", "") or props.get("reasonType", ""),
            "severity": severity_for_health(state),
        })
    for row in timeline:
        row["_band"] = row["severity"]
    timeline.sort(key=lambda row: row.get("time", ""), reverse=True)
    return timeline


def _headers():
    from agent_identity import agent_token

    token = agent_token(f"{ARM_ENDPOINT}/.default")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _get(headers, url):
    import requests

    response = requests.get(url, headers=headers, timeout=90)
    response.raise_for_status()
    return response.json()


def _run_graph(headers, query):
    import requests

    url = f"{ARM_ENDPOINT}/providers/Microsoft.ResourceGraph/resources?api-version=2022-10-01"
    payload = {"query": query, "options": {"resultFormat": "objectArray", "top": 200}}
    response = requests.post(url, headers=headers, json=payload, timeout=90)
    response.raise_for_status()
    return response.json().get("data", [])


def main(resource_id: str, hours: int = 24) -> dict:
    sub, rg = parse_resource_id(resource_id)
    name = [p for p in resource_id.split("/") if p][-1] if resource_id else ""
    headers = _headers()
    notes = []
    start = (datetime.now(timezone.utc) - timedelta(hours=int(hours))).replace(microsecond=0).isoformat()

    health_statuses, current = [], {}
    try:
        body = _get(headers, f"{ARM_ENDPOINT}{resource_id}/providers/Microsoft.ResourceHealth/availabilityStatuses?api-version=2020-05-01")
        health_statuses = body.get("value", [])
        if health_statuses:
            props = health_statuses[0].get("properties", {})
            current = {
                "state": props.get("availabilityState", "Unknown"),
                "summary": props.get("summary", ""),
                "reason": props.get("reasonType", ""),
                "time": props.get("occuredTime") or props.get("reportedTime", ""),
            }
    except Exception as error:  # noqa: BLE001
        notes.append(f"Resource Health not read ({error}).")

    activity = []
    try:
        flt = f"eventTimestamp ge '{start}' and resourceGroupName eq '{rg}'"
        url = f"{ARM_ENDPOINT}/subscriptions/{sub}/providers/microsoft.insights/eventtypes/management/values?api-version=2015-04-01&$filter={flt}"
        body = _get(headers, url)
        activity = body.get("value", [])
    except Exception as error:  # noqa: BLE001
        notes.append(f"Activity Log not read ({error}).")

    neighbors = []
    try:
        neighbors = _run_graph(headers, f"resources | where subscriptionId == '{sub}' and resourceGroup =~ '{rg}' | project name, type, id")
    except Exception as error:  # noqa: BLE001
        notes.append(f"Neighbours not read ({error}).")

    return {
        "resource_id": resource_id,
        "resource_name": name,
        "subscription": sub,
        "resource_group": rg,
        "window_hours": int(hours),
        "current_health": current,
        "timeline": build_timeline(activity, health_statuses),
        "neighbors": neighbors,
        "notes": notes,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Pass the affected resource id as the first argument."}))
        raise SystemExit(1)
    window = int(sys.argv[2]) if len(sys.argv) > 2 else 24
    print(json.dumps(main(sys.argv[1], window)))
