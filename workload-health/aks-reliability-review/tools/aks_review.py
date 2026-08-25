"""
aks_review: Review AKS clusters for reliability and operational best practices.

Azure SRE Agent Python tool. Uses the agent managed identity (ARM scope) to read
the managed cluster configuration with Azure Resource Graph, evaluate each
cluster against the checks in references/checks-catalog.md, and print a
report_data object as JSON ready to pipe into report_render.py.

    python aks_review.py | python report_render.py

Heavy imports (azure-identity, requests) are lazy so evaluate_cluster and the
report builder can be unit tested without them.
"""

import json

ARM_ENDPOINT = "https://management.azure.com"
SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
K8S_FLOOR_MINOR = 28


def _minor(version):
    parts = (version or "").split(".")
    return int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else None


def evaluate_cluster(cluster):
    """Return a list of finding dicts for one cluster. Pure and testable.

    cluster: {name, subscriptionId, resourceGroup, sku, properties}.
    """
    props = cluster.get("properties", {}) or {}
    sku = cluster.get("sku", {}) or {}
    base = {
        "cluster": cluster.get("name", ""),
        "subscription": cluster.get("subscriptionId", ""),
        "resource_group": cluster.get("resourceGroup", ""),
    }
    findings = []

    def add(check, recommendation, severity):
        findings.append({**base, "check": check, "recommendation": recommendation, "severity": severity, "_band": severity})

    minor = _minor(props.get("kubernetesVersion"))
    if minor is not None and minor < K8S_FLOOR_MINOR:
        sev = "High" if minor <= K8S_FLOOR_MINOR - 3 else "Medium"
        add(f"Kubernetes {props.get('kubernetesVersion')} below the supported floor", "Upgrade to a supported version and stay within N minus two.", sev)

    pools = props.get("agentPoolProfiles", []) or []
    has_system_pool = any((pool.get("mode") or "").lower() == "system" for pool in pools)
    for pool in pools:
        zones = pool.get("availabilityZones") or []
        if not zones:
            add(f"Node pool {pool.get('name', '')} has no availability zones", "Recreate the pool across availability zones.", "Medium")
        if (pool.get("count") or 0) < 2:
            add(f"Node pool {pool.get('name', '')} runs fewer than two nodes", "Run at least two nodes and enable the cluster autoscaler.", "Medium")
    if pools and not has_system_pool:
        add("No dedicated system node pool", "Add a system mode node pool so control components are isolated.", "Low")

    access = props.get("apiServerAccessProfile", {}) or {}
    if not access.get("enablePrivateCluster") and not (access.get("authorizedIpRanges") or access.get("authorizedIPRanges")):
        add("Control plane open to the internet", "Enable a private cluster, or set API server authorized IP ranges.", "Medium")

    channel = ((props.get("autoUpgradeProfile", {}) or {}).get("upgradeChannel") or "none").lower()
    if channel in ("none", "", "null"):
        add("No auto upgrade channel", "Set an upgrade channel (patch or stable) with a maintenance window.", "Medium")

    addons = props.get("addonProfiles", {}) or {}
    oms = addons.get("omsagent") or addons.get("omsAgent") or {}
    if not oms.get("enabled"):
        add("Container Insights monitoring not enabled", "Enable Azure Monitor Container Insights.", "Medium")

    if not (props.get("networkProfile", {}) or {}).get("networkPolicy"):
        add("No network policy", "Enable a network policy (Azure or Calico) and default deny where practical.", "Low")

    if not props.get("aadProfile") or props.get("enableRBAC") is False:
        add("Entra ID and Kubernetes RBAC not fully enabled", "Enable Entra ID integration and Kubernetes RBAC.", "Medium")

    if (sku.get("tier") or "Free").lower() == "free":
        add("Free tier control plane has no uptime SLA", "Move production clusters to the Standard tier for the uptime SLA.", "Low")

    return findings


def build_report_data(clusters, notes):
    findings = []
    for cluster in clusters:
        findings.extend(evaluate_cluster(cluster))
    findings.sort(key=lambda f: SEVERITY_ORDER.get(f["severity"], 9))
    with_findings = len({f["cluster"] for f in findings})
    high = sum(1 for f in findings if f["severity"] in ("Critical", "High"))
    sev_counts, by_sub = {}, {}
    for finding in findings:
        sev_counts[finding["severity"]] = sev_counts.get(finding["severity"], 0) + 1
        by_sub[finding["subscription"]] = by_sub.get(finding["subscription"], 0) + 1
    sev_items = [{"name": b, "value": sev_counts[b], "band": b} for b in ("Critical", "High", "Medium", "Low") if b in sev_counts]
    sub_items = sorted(({"name": k, "value": v} for k, v in by_sub.items()), key=lambda i: i["value"], reverse=True)
    return {
        "title": "AKS Reliability Review",
        "subtitle": "Kubernetes cluster reliability and operational best practices.",
        "meta": {"window": "Point in time", "scope": f"{len({c.get('subscriptionId') for c in clusters})} subscription(s)", "source": "Azure Resource Graph"},
        "summary_cards": [
            {"label": "Clusters reviewed", "value": f"{len(clusters):,}"},
            {"label": "Clusters with findings", "value": f"{with_findings:,}"},
            {"label": "High findings", "value": f"{high:,}"},
            {"label": "Total findings", "value": f"{len(findings):,}"},
        ],
        "charts": [
            {"title": "Findings by severity", "unit": "findings", "items": sev_items},
            {"title": "Findings by subscription", "unit": "findings", "items": sub_items},
        ],
        "findings": {
            "title": "AKS findings",
            "columns": ["cluster", "subscription", "resource_group", "check", "recommendation", "severity"],
            "rows": findings,
        },
        "method_notes": notes + [
            f"Kubernetes floor: minor {K8S_FLOOR_MINOR}. Clusters below it are flagged.",
            "A cluster with several gaps appears as several rows, one per check.",
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


def main() -> dict:
    headers = _headers()
    notes = []
    try:
        clusters = _run_graph(headers, "resources | where type =~ 'microsoft.containerservice/managedclusters' | project name, id, subscriptionId, resourceGroup, sku, properties")
    except Exception as error:  # noqa: BLE001
        return build_report_data([], [f"Could not read AKS clusters ({error})."])
    return build_report_data(clusters, notes)


if __name__ == "__main__":
    print(json.dumps(main()))
