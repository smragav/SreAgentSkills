"""
reliability_scan: Find Azure reliability and resilience gaps with Resource Graph.

Azure SRE Agent Python tool. Uses the agent managed identity (ARM scope) to run
a set of Azure Resource Graph queries across every accessible subscription,
flags single points of failure and redundancy gaps (no availability zones,
single instance compute, retiring Basic tiers, single region data services),
assigns a severity to each, and prints a report_data object as JSON on standard
output ready to pipe into report_render.py.

    python reliability_scan.py | python report_render.py

Heavy imports (azure-identity, requests) are loaded lazily inside functions so
the pure aggregation helpers can be imported and unit tested without them. See
references/checks-catalog.md and references/scoring-method.md.
"""

import json
import sys
from datetime import datetime, timezone

ARM_ENDPOINT = "https://management.azure.com"
SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}

# Each rule: a Resource Graph query that already filters to the risky condition,
# plus the severity, resource type label, issue, and recommendation to record.
RULES = [
    {
        "key": "vm_no_redundancy",
        "severity": "High",
        "resource_type": "Virtual machine",
        "issue": "No availability zone and no availability set",
        "recommendation": "Deploy across availability zones, or place in an availability set for rack level redundancy.",
        "kql": "resources | where type =~ 'microsoft.compute/virtualmachines' | where isnull(zones) or array_length(zones) == 0 | where isnull(properties.availabilitySet) | project name, id, resourceGroup, subscriptionId, location",
    },
    {
        "key": "vmss_single",
        "severity": "Medium",
        "resource_type": "Scale set",
        "issue": "Scale set runs fewer than two instances",
        "recommendation": "Run at least two instances, ideally spread across availability zones.",
        "kql": "resources | where type =~ 'microsoft.compute/virtualmachinescalesets' | extend capacity = toint(sku.capacity) | where capacity < 2 | project name, id, resourceGroup, subscriptionId, location, capacity",
    },
    {
        "key": "pip_basic",
        "severity": "High",
        "resource_type": "Public IP",
        "issue": "Basic SKU public IP is retiring and not zone redundant",
        "recommendation": "Migrate to a Standard SKU public IP.",
        "kql": "resources | where type =~ 'microsoft.network/publicipaddresses' | where tostring(sku.name) =~ 'Basic' | project name, id, resourceGroup, subscriptionId, location",
    },
    {
        "key": "lb_basic",
        "severity": "High",
        "resource_type": "Load balancer",
        "issue": "Basic load balancer is retiring and has no zone support or SLA",
        "recommendation": "Migrate to Standard Load Balancer.",
        "kql": "resources | where type =~ 'microsoft.network/loadbalancers' | where tostring(sku.name) =~ 'Basic' | project name, id, resourceGroup, subscriptionId, location",
    },
    {
        "key": "sql_no_zone",
        "severity": "High",
        "resource_type": "SQL database",
        "issue": "Premium or Business Critical database without zone redundancy",
        "recommendation": "Enable zoneRedundant on the database for zone resilient failover.",
        "kql": "resources | where type =~ 'microsoft.sql/servers/databases' | where tostring(properties.zoneRedundant) =~ 'false' | where tostring(sku.tier) in~ ('Premium','BusinessCritical') | project name, id, resourceGroup, subscriptionId, location",
    },
    {
        "key": "storage_lrs",
        "severity": "Medium",
        "resource_type": "Storage account",
        "issue": "Locally redundant storage has no zone or regional protection",
        "recommendation": "Use ZRS for zone redundancy, or GRS and RA-GRS for regional redundancy where the data warrants it.",
        "kql": "resources | where type =~ 'microsoft.storage/storageaccounts' | where tostring(sku.name) endswith 'LRS' | project name, id, resourceGroup, subscriptionId, location",
    },
    {
        "key": "appgw_no_zone",
        "severity": "Medium",
        "resource_type": "Application Gateway",
        "issue": "Application Gateway not zone redundant",
        "recommendation": "Redeploy the gateway across availability zones (v2 SKU).",
        "kql": "resources | where type =~ 'microsoft.network/applicationgateways' | where isnull(zones) or array_length(zones) == 0 | project name, id, resourceGroup, subscriptionId, location",
    },
    {
        "key": "aks_no_zone",
        "severity": "Medium",
        "resource_type": "AKS node pool",
        "issue": "Node pool without availability zones or with a single node",
        "recommendation": "Spread node pools across availability zones and run at least two nodes.",
        "kql": "resources | where type =~ 'microsoft.containerservice/managedclusters' | mv-expand pool = properties.agentPoolProfiles | extend zones = pool.availabilityZones, nodes = toint(pool['count']) | where isnull(zones) or array_length(zones) == 0 or nodes < 2 | project name, id, resourceGroup, subscriptionId, location",
    },
    {
        "key": "cosmos_single_region",
        "severity": "Medium",
        "resource_type": "Cosmos DB account",
        "issue": "Cosmos DB account configured with a single region",
        "recommendation": "Add a second region and enable automatic failover for regional resilience.",
        "kql": "resources | where type =~ 'microsoft.documentdb/databaseaccounts' | extend regions = properties.locations | where array_length(regions) < 2 | project name, id, resourceGroup, subscriptionId, location",
    },
]

NON_PROD = ("lab", "dev", "sandbox", "poc", "temp", "demo", "test")


def adjust_severity(base, name):
    """Lower non production resources by one band. Pure and testable."""
    lowered = {"Critical": "High", "High": "Medium", "Medium": "Low", "Low": "Low"}
    label = (name or "").lower()
    if any(token in label for token in NON_PROD):
        return lowered.get(base, base)
    return base


def severity_counts(findings):
    """Return an ordered list of {name, value, band} for the severity chart."""
    counts = {}
    for finding in findings:
        band = finding.get("severity", "Low")
        counts[band] = counts.get(band, 0) + 1
    ordered = sorted(counts.items(), key=lambda kv: SEVERITY_ORDER.get(kv[0], 9))
    return [{"name": band, "value": value, "band": band} for band, value in ordered]


def subscription_counts(findings, names):
    """Return {name, value} per subscription, highest first."""
    counts = {}
    for finding in findings:
        sub = finding.get("subscription", "")
        counts[sub] = counts.get(sub, 0) + 1
    rows = [{"name": names.get(sub, sub) or sub, "value": value} for sub, value in counts.items()]
    rows.sort(key=lambda item: item["value"], reverse=True)
    return rows


def build_report_data(findings, subscription_names, subscriptions_scanned, notes):
    """Assemble the report_data object. Pure and testable."""
    findings = sorted(findings, key=lambda f: SEVERITY_ORDER.get(f.get("severity", "Low"), 9))
    for finding in findings:
        finding["_band"] = finding.get("severity", "Low")
    high = sum(1 for f in findings if f.get("severity") in ("Critical", "High"))
    subs_display = {sid: subscription_names.get(sid, sid) for sid in subscription_names}
    for finding in findings:
        finding["subscription"] = subs_display.get(finding.get("subscription"), finding.get("subscription"))
    return {
        "title": "Reliability Posture Review",
        "subtitle": "Well-Architected reliability pillar: single points of failure and redundancy gaps.",
        "meta": {
            "window": "Point in time",
            "scope": f"{subscriptions_scanned} subscription(s)",
            "source": "Azure Resource Graph",
        },
        "summary_cards": [
            {"label": "Resources with findings", "value": f"{len(findings):,}"},
            {"label": "Critical and High", "value": f"{high:,}", "sub": "act on these first"},
            {"label": "Signals evaluated", "value": str(len(RULES))},
            {"label": "Subscriptions scanned", "value": str(subscriptions_scanned)},
        ],
        "charts": [
            {"title": "Findings by severity", "unit": "findings", "items": severity_counts(findings)},
            {"title": "Findings by subscription", "unit": "findings", "items": subscription_counts(findings, subs_display)},
        ],
        "findings": {
            "title": "Reliability findings",
            "columns": ["resource", "resource_type", "subscription", "resource_group", "issue", "recommendation", "severity"],
            "rows": findings,
        },
        "method_notes": notes
        + [
            "Live idle and underused resources are assessed by the cost optimizer skill.",
            "Severity reflects blast radius and likelihood, not effort to fix.",
        ],
    }


def _headers():
    from agent_identity import agent_token

    token = agent_token(f"{ARM_ENDPOINT}/.default")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


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


def _run_graph(headers, query):
    import requests

    url = f"{ARM_ENDPOINT}/providers/Microsoft.ResourceGraph/resources?api-version=2022-10-01"
    rows = []
    skip_token = None
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
            break
    return rows


def main() -> dict:
    headers = _headers()
    notes = []
    try:
        subscription_names = _list_subscription_names(headers)
    except Exception as error:  # noqa: BLE001
        subscription_names = {}
        notes.append(f"Could not list subscription names ({error}). Showing subscription ids.")

    findings = []
    scanned = set()
    for rule in RULES:
        try:
            rows = _run_graph(headers, rule["kql"])
        except Exception as error:  # noqa: BLE001
            notes.append(f"Signal {rule['key']} not assessed ({error}).")
            continue
        for row in rows:
            sub = row.get("subscriptionId", "")
            scanned.add(sub)
            findings.append(
                {
                    "resource": row.get("name", ""),
                    "resource_type": rule["resource_type"],
                    "resource_id": row.get("id", ""),
                    "subscription": sub,
                    "resource_group": row.get("resourceGroup", ""),
                    "location": row.get("location", ""),
                    "issue": rule["issue"],
                    "recommendation": rule["recommendation"],
                    "severity": adjust_severity(rule["severity"], row.get("name", "")),
                }
            )

    subscriptions_scanned = len(scanned) if scanned else len(subscription_names)
    return build_report_data(findings, subscription_names, subscriptions_scanned, notes)


if __name__ == "__main__":
    print(json.dumps(main()))
