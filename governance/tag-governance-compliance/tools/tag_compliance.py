"""
tag_compliance: Check Azure resources against a required tag standard.

Azure SRE Agent Python tool. Uses the agent managed identity (ARM scope) to
enumerate resources with Azure Resource Graph, check each against a required tag
list with tolerant (case and separator insensitive) key matching, and print a
report_data object as JSON ready to pipe into report_render.py.

    python tag_compliance.py [owner,environment,cost-center] | python report_render.py

Heavy imports (azure-identity, requests) are lazy so the pure compliance helpers
can be unit tested without them. See references/checks-catalog.md.
"""

import json
import sys

ARM_ENDPOINT = "https://management.azure.com"
DEFAULT_REQUIRED = ["owner", "environment", "cost-center"]


def normalize_key(key):
    """Lowercase and strip separators so tag key styles match. Pure."""
    return "".join(ch for ch in (key or "").lower() if ch.isalnum())


def missing_tags(resource_tags, required):
    """Return the required tags absent from a resource's tag bag. Pure.

    Matching is tolerant: cost-center is satisfied by CostCenter or cost_center.
    """
    present = {normalize_key(k) for k in (resource_tags or {}).keys()}
    return [req for req in required if normalize_key(req) not in present]


def severity_for_missing(missing):
    """High when the owner tag is missing, Medium otherwise. Pure."""
    if any(normalize_key(tag) == "owner" for tag in missing):
        return "High"
    return "Medium"


def classify_resource(resource, required):
    """Return a finding for a non compliant resource, or None. Pure."""
    missing = missing_tags(resource.get("tags"), required)
    if not missing:
        return None
    severity = severity_for_missing(missing)
    return {
        "resource": resource.get("name", ""),
        "resource_type": resource.get("type", ""),
        "resource_id": resource.get("id", ""),
        "subscription": resource.get("subscriptionId", ""),
        "resource_group": resource.get("resourceGroup", ""),
        "missing_tags": ", ".join(missing),
        "recommendation": "Apply " + ", ".join(missing) + " with the correct values; enforce with Azure Policy.",
        "severity": severity,
        "_band": severity,
        "_missing_list": missing,
    }


def build_report_data(resources, required, subs_scanned, sub_names, notes):
    findings = []
    for resource in resources:
        finding = classify_resource(resource, required)
        if finding:
            findings.append(finding)
    total = len(resources)
    compliant = total - len(findings)
    compliance = round(compliant / total * 100.0, 1) if total else 100.0
    no_owner = sum(1 for f in findings if any(normalize_key(t) == "owner" for t in f["_missing_list"]))

    per_tag = {req: 0 for req in required}
    for finding in findings:
        for tag in finding["_missing_list"]:
            per_tag[tag] = per_tag.get(tag, 0) + 1
    tag_items = [{"name": tag, "value": count} for tag, count in sorted(per_tag.items(), key=lambda kv: kv[1], reverse=True)]

    by_sub = {}
    for finding in findings:
        label = sub_names.get(finding["subscription"], finding["subscription"])
        finding["subscription"] = label
        by_sub[label] = by_sub.get(label, 0) + 1
    sub_items = sorted(({"name": k, "value": v} for k, v in by_sub.items()), key=lambda i: i["value"], reverse=True)

    findings.sort(key=lambda f: (0 if f["severity"] == "High" else 1, f["resource"]))
    for finding in findings:
        finding.pop("_missing_list", None)

    return {
        "title": "Tag Governance Compliance",
        "subtitle": "Resources against the required tag standard.",
        "meta": {"window": ", ".join(required), "scope": f"{subs_scanned} subscription(s)", "source": "Azure Resource Graph"},
        "summary_cards": [
            {"label": "Compliance", "value": f"{compliance}%", "sub": "all required tags present"},
            {"label": "Non compliant", "value": f"{len(findings):,}"},
            {"label": "Missing an owner", "value": f"{no_owner:,}"},
            {"label": "Resources scanned", "value": f"{total:,}"},
        ],
        "charts": [
            {"title": "Missing by tag", "unit": "resources", "items": tag_items},
            {"title": "Non compliance by subscription", "unit": "resources", "items": sub_items},
        ],
        "findings": {
            "title": "Tag gaps",
            "columns": ["resource", "resource_type", "subscription", "resource_group", "missing_tags", "recommendation", "severity"],
            "rows": findings,
        },
        "method_notes": notes + [
            f"Required tags: {', '.join(required)}. Key matching ignores case and separators.",
            "Compliance is resources with every required tag present, divided by all resources in scope.",
            "Enforce the standard durably with Azure Policy; a one time tagging pass drifts again without it.",
        ],
    }


def _headers():
    from agent_identity import agent_token

    token = agent_token(f"{ARM_ENDPOINT}/.default")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


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


def _list_subscription_names(headers):
    import requests

    url = f"{ARM_ENDPOINT}/subscriptions?api-version=2022-12-01"
    names = {}
    while url:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        body = response.json()
        for item in body.get("value", []):
            names[item["subscriptionId"]] = item.get("displayName", item["subscriptionId"])
        url = body.get("nextLink")
    return names


def main(required=None) -> dict:
    required = required or DEFAULT_REQUIRED
    headers = _headers()
    notes = []
    try:
        sub_names = _list_subscription_names(headers)
    except Exception as error:  # noqa: BLE001
        sub_names = {}
        notes.append(f"Could not list subscription names ({error}).")
    resources = _run_graph(headers, "resources | project name, id, type, resourceGroup, subscriptionId, tags")
    subs = {r.get("subscriptionId") for r in resources if r.get("subscriptionId")}
    return build_report_data(resources, required, len(subs), sub_names, notes)


if __name__ == "__main__":
    req = [t.strip() for t in sys.argv[1].split(",")] if len(sys.argv) > 1 else DEFAULT_REQUIRED
    print(json.dumps(main(req)))
