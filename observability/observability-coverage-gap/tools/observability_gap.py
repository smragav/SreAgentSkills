"""
observability_gap: Find monitoring wiring gaps with Azure Resource Graph.

Azure SRE Agent Python tool. Uses the agent managed identity (ARM scope) to
enumerate important resources, build the set already covered by a metric alert,
count action groups and Log Analytics workspaces per subscription, check
diagnostic settings where Resource Graph can answer, and print a report_data
object as JSON ready to pipe into report_render.py.

    python observability_gap.py | python report_render.py

Heavy imports (azure-identity, requests) are lazy so the pure classification
helpers can be unit tested without them. See references/checks-catalog.md.
"""

import json

ARM_ENDPOINT = "https://management.azure.com"
SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}

IMPORTANT_TYPES = [
    "microsoft.compute/virtualmachines",
    "microsoft.web/sites",
    "microsoft.sql/servers/databases",
    "microsoft.storage/storageaccounts",
    "microsoft.keyvault/vaults",
    "microsoft.containerservice/managedclusters",
    "microsoft.network/applicationgateways",
    "microsoft.network/loadbalancers",
    "microsoft.documentdb/databaseaccounts",
    "microsoft.cache/redis",
    "microsoft.servicebus/namespaces",
    "microsoft.eventhub/namespaces",
    "microsoft.dbforpostgresql/flexibleservers",
    "microsoft.dbformysql/flexibleservers",
    "microsoft.apimanagement/service",
    "microsoft.containerregistry/registries",
    "microsoft.network/azurefirewalls",
]

TYPE_LABEL = {
    "microsoft.compute/virtualmachines": "Virtual machine",
    "microsoft.web/sites": "App Service",
    "microsoft.sql/servers/databases": "SQL database",
    "microsoft.storage/storageaccounts": "Storage account",
    "microsoft.keyvault/vaults": "Key Vault",
    "microsoft.containerservice/managedclusters": "AKS cluster",
    "microsoft.network/applicationgateways": "Application Gateway",
    "microsoft.network/loadbalancers": "Load balancer",
    "microsoft.documentdb/databaseaccounts": "Cosmos DB",
    "microsoft.cache/redis": "Redis",
    "microsoft.servicebus/namespaces": "Service Bus",
    "microsoft.eventhub/namespaces": "Event Hub",
    "microsoft.dbforpostgresql/flexibleservers": "PostgreSQL",
    "microsoft.dbformysql/flexibleservers": "MySQL",
    "microsoft.apimanagement/service": "API Management",
    "microsoft.containerregistry/registries": "Container Registry",
    "microsoft.network/azurefirewalls": "Azure Firewall",
}


def is_alert_covered(resource, covered_ids, covered_rgs, covered_subs):
    """A resource is covered when its id, its resource group, or its subscription
    appears in an alert scope. Pure and testable."""
    rid = (resource.get("id") or "").lower()
    sub = (resource.get("subscriptionId") or "").lower()
    rg = (resource.get("resourceGroup") or "").lower()
    rg_scope = f"/subscriptions/{sub}/resourcegroups/{rg}"
    sub_scope = f"/subscriptions/{sub}"
    return rid in covered_ids or rg_scope in covered_rgs or sub_scope in covered_subs


def classify_resource(resource, diag_parents, diag_available, covered_ids, covered_rgs, covered_subs):
    """Return a combined gap finding for a resource, or None. Pure and testable."""
    rid = (resource.get("id") or "").lower()
    missing = []
    severity = "Low"
    if diag_available and rid not in diag_parents:
        missing.append("diagnostic settings")
        severity = "High"
    if not is_alert_covered(resource, covered_ids, covered_rgs, covered_subs):
        missing.append("metric alert")
        severity = "High" if severity == "High" else "Medium"
    if not missing:
        return None
    return {
        "resource": resource.get("name", ""),
        "resource_type": TYPE_LABEL.get(resource.get("type", ""), resource.get("type", "")),
        "resource_id": resource.get("id", ""),
        "subscription": resource.get("subscriptionId", ""),
        "resource_group": resource.get("resourceGroup", ""),
        "missing": "; ".join("no " + item for item in missing),
        "recommendation": "Add " + " and ".join(missing) + " routing telemetry to the central workspace and an action group.",
        "severity": severity,
        "_band": severity,
    }


def subscription_findings(sub_ids_with_resources, action_group_subs, workspace_subs, sub_names):
    """One finding per subscription that has resources but no action group or no
    workspace. Pure and testable."""
    findings = []
    for sub in sub_ids_with_resources:
        name = sub_names.get(sub, sub)
        if sub not in action_group_subs:
            findings.append({
                "resource": name, "resource_type": "Subscription", "resource_id": f"/subscriptions/{sub}",
                "subscription": sub, "resource_group": "", "missing": "no action group",
                "recommendation": "Create at least one action group so alerts can notify a team.",
                "severity": "High", "_band": "High",
            })
        if sub not in workspace_subs:
            findings.append({
                "resource": name, "resource_type": "Subscription", "resource_id": f"/subscriptions/{sub}",
                "subscription": sub, "resource_group": "", "missing": "no Log Analytics workspace",
                "recommendation": "Create a workspace and point diagnostic settings at it.",
                "severity": "Medium", "_band": "Medium",
            })
    return findings


def build_report_data(findings, resources_scanned, subs_scanned, diag_available, sub_names, notes):
    for finding in findings:
        finding["subscription"] = sub_names.get(finding["subscription"], finding["subscription"])
    findings = sorted(findings, key=lambda f: SEVERITY_ORDER.get(f["severity"], 9))
    blind = sum(1 for f in findings if "diagnostic settings" in f["missing"])
    no_ag = sum(1 for f in findings if "action group" in f["missing"])
    gap_types = {}
    for finding in findings:
        for piece in finding["missing"].split("; "):
            gap_types[piece] = gap_types.get(piece, 0) + 1
    type_items = [{"name": k, "value": v} for k, v in sorted(gap_types.items(), key=lambda kv: kv[1], reverse=True)]
    by_sub = {}
    for finding in findings:
        by_sub[finding["subscription"]] = by_sub.get(finding["subscription"], 0) + 1
    sub_items = sorted(({"name": k, "value": v} for k, v in by_sub.items()), key=lambda i: i["value"], reverse=True)
    if not diag_available:
        notes = notes + ["Diagnostic settings could not be read in bulk from Resource Graph; that gap is not counted. Spot check per resource with the checks catalog command."]
    return {
        "title": "Observability Coverage Gap",
        "subtitle": "Missing diagnostic settings, alerts, action groups, and workspaces.",
        "meta": {"window": "Point in time", "scope": f"{subs_scanned} subscription(s)", "source": "Azure Resource Graph"},
        "summary_cards": [
            {"label": "Resources with gaps", "value": f"{len([f for f in findings if f['resource_type'] != 'Subscription']):,}"},
            {"label": "No diagnostic settings", "value": f"{blind:,}", "sub": "effectively blind"},
            {"label": "Subs with no action group", "value": f"{no_ag:,}"},
            {"label": "Resources scanned", "value": f"{resources_scanned:,}"},
        ],
        "charts": [
            {"title": "Gaps by type", "unit": "gaps", "items": type_items},
            {"title": "Gaps by subscription", "unit": "gaps", "items": sub_items},
        ],
        "findings": {
            "title": "Observability gaps",
            "columns": ["resource", "resource_type", "subscription", "resource_group", "missing", "recommendation", "severity"],
            "rows": findings,
        },
        "method_notes": notes + ["A resource missing several pieces of wiring appears once, at the highest severity among them."],
    }


def _headers():
    from azure.identity import DefaultAzureCredential

    token = DefaultAzureCredential().get_token(f"{ARM_ENDPOINT}/.default").token
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


def main() -> dict:
    headers = _headers()
    notes = []
    try:
        sub_names = _list_subscription_names(headers)
    except Exception as error:  # noqa: BLE001
        sub_names = {}
        notes.append(f"Could not list subscription names ({error}).")

    types_list = "','".join(IMPORTANT_TYPES)
    resources = _run_graph(headers, f"resources | where type in~ ('{types_list}') | project name, id, type, resourceGroup, subscriptionId, location")

    alert_rows = _run_graph(headers, "resources | where type =~ 'microsoft.insights/metricalerts' | mv-expand scope = properties.scopes | project scope=tolower(tostring(scope))")
    covered_ids, covered_rgs, covered_subs = set(), set(), set()
    for row in alert_rows:
        scope = row.get("scope", "")
        if "/providers/" in scope or scope.count("/") > 4:
            covered_ids.add(scope)
        elif "/resourcegroups/" in scope:
            covered_rgs.add(scope)
        elif scope.startswith("/subscriptions/"):
            covered_subs.add(scope)

    ag_rows = _run_graph(headers, "resources | where type =~ 'microsoft.insights/actiongroups' | distinct subscriptionId")
    ws_rows = _run_graph(headers, "resources | where type =~ 'microsoft.operationalinsights/workspaces' | distinct subscriptionId")
    action_group_subs = {r.get("subscriptionId") for r in ag_rows}
    workspace_subs = {r.get("subscriptionId") for r in ws_rows}

    diag_rows = _run_graph(headers, "resources | where type =~ 'microsoft.insights/diagnosticsettings' | extend parentId = tolower(substring(id, 0, indexof(id, '/providers/microsoft.insights/diagnosticsettings'))) | distinct parentId")
    diag_parents = {r.get("parentId") for r in diag_rows if r.get("parentId")}
    diag_available = len(diag_parents) > 0

    findings = []
    for resource in resources:
        finding = classify_resource(resource, diag_parents, diag_available, covered_ids, covered_rgs, covered_subs)
        if finding:
            findings.append(finding)

    subs_with_resources = {r.get("subscriptionId") for r in resources}
    findings += subscription_findings(subs_with_resources, action_group_subs, workspace_subs, sub_names)
    return build_report_data(findings, len(resources), len(subs_with_resources), diag_available, sub_names, notes)


if __name__ == "__main__":
    print(json.dumps(main()))
