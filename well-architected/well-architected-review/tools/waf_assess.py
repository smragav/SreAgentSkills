"""
waf_assess: Score the five Well-Architected pillars into one scorecard.

Azure SRE Agent Python tool. Uses the agent managed identity (ARM scope) to run a
curated set of Azure Resource Graph checks across accessible subscriptions, count
applicable and failing resources per check, score each pillar as a weighted pass
ratio, and print a report_data object as JSON ready to pipe into report_render.py.

    python waf_assess.py | python report_render.py

Heavy imports (azure-identity, requests) are lazy so the pure scoring helpers can
be unit tested without them. See references/checks-catalog.md.
"""

import json

ARM_ENDPOINT = "https://management.azure.com"
SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
WEIGHTS = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
PILLARS = ["Reliability", "Security", "Cost Optimization", "Operational Excellence", "Performance Efficiency"]

# Each check counts applicable and failing resources with a single summarize query.
CHECKS = [
    {"pillar": "Reliability", "name": "VMs without zone or availability set", "severity": "High",
     "recommendation": "Deploy across availability zones or an availability set. Deep dive: reliability-posture-review.",
     "kql": "resources | where type =~ 'microsoft.compute/virtualmachines' | summarize applicable=count(), failing=countif((isnull(zones) or array_length(zones)==0) and isnull(properties.availabilitySet))"},
    {"pillar": "Reliability", "name": "Locally redundant storage", "severity": "Medium",
     "recommendation": "Use ZRS or GRS where the data warrants it.",
     "kql": "resources | where type =~ 'microsoft.storage/storageaccounts' | summarize applicable=count(), failing=countif(tostring(sku.name) endswith 'LRS')"},
    {"pillar": "Reliability", "name": "Premium SQL without zone redundancy", "severity": "High",
     "recommendation": "Enable zoneRedundant on Premium and Business Critical databases.",
     "kql": "resources | where type =~ 'microsoft.sql/servers/databases' | where tostring(sku.tier) in~ ('Premium','BusinessCritical') | summarize applicable=count(), failing=countif(tostring(properties.zoneRedundant) =~ 'false')"},
    {"pillar": "Reliability", "name": "Single region Cosmos DB", "severity": "Medium",
     "recommendation": "Add a second region and enable automatic failover.",
     "kql": "resources | where type =~ 'microsoft.documentdb/databaseaccounts' | summarize applicable=count(), failing=countif(array_length(properties.locations) < 2)"},

    {"pillar": "Security", "name": "Storage with anonymous blob access", "severity": "High",
     "recommendation": "Set allowBlobPublicAccess to false. Deep dive: network-exposure-review.",
     "kql": "resources | where type =~ 'microsoft.storage/storageaccounts' | summarize applicable=count(), failing=countif(tostring(properties.allowBlobPublicAccess) =~ 'true')"},
    {"pillar": "Security", "name": "PaaS with public network access", "severity": "Medium",
     "recommendation": "Disable public network access and use Private Link.",
     "kql": "resources | where type in~ ('microsoft.sql/servers','microsoft.keyvault/vaults','microsoft.documentdb/databaseaccounts','microsoft.dbforpostgresql/flexibleservers','microsoft.dbformysql/flexibleservers') | summarize applicable=count(), failing=countif(tostring(properties.publicNetworkAccess) =~ 'Enabled')"},
    {"pillar": "Security", "name": "Key Vaults without purge protection", "severity": "Medium",
     "recommendation": "Enable purge protection on Key Vaults.",
     "kql": "resources | where type =~ 'microsoft.keyvault/vaults' | summarize applicable=count(), failing=countif(tostring(properties.enablePurgeProtection) !~ 'true')"},

    {"pillar": "Cost Optimization", "name": "Unattached managed disks", "severity": "Medium",
     "recommendation": "Delete or snapshot unattached disks. Deep dive: finops-cost-optimizer.",
     "kql": "resources | where type =~ 'microsoft.compute/disks' | summarize applicable=count(), failing=countif(tostring(properties.diskState) == 'Unattached')"},
    {"pillar": "Cost Optimization", "name": "Unassociated public IPs", "severity": "Low",
     "recommendation": "Release public IPs with no association.",
     "kql": "resources | where type =~ 'microsoft.network/publicipaddresses' | summarize applicable=count(), failing=countif(isnull(properties.ipConfiguration) and isnull(properties.natGateway))"},

    {"pillar": "Operational Excellence", "name": "Resources with no owner tag", "severity": "Medium",
     "recommendation": "Apply an owner tag; enforce with Azure Policy. Deep dive: tag-governance-compliance.",
     "kql": "resources | summarize applicable=count(), failing=countif(isempty(tostring(tags['owner'])) and isempty(tostring(tags['Owner'])))"},
    {"pillar": "Operational Excellence", "name": "AKS below the supported version floor", "severity": "Medium",
     "recommendation": "Upgrade AKS to a supported version. Deep dive: deprecation-retirement-tracker.",
     "kql": "resources | where type =~ 'microsoft.containerservice/managedclusters' | extend minor = toint(split(tostring(properties.kubernetesVersion), '.')[1]) | summarize applicable=count(), failing=countif(minor < 28)"},

    {"pillar": "Performance Efficiency", "name": "App Service plans on Free, Shared, or Basic", "severity": "Medium",
     "recommendation": "Move production workloads to Standard or higher. Deep dive: appservice-containerapps-health.",
     "kql": "resources | where type =~ 'microsoft.web/serverfarms' | summarize applicable=count(), failing=countif(tostring(sku.tier) in~ ('Free','Shared','Basic'))"},
    {"pillar": "Performance Efficiency", "name": "Container Apps that cannot scale out", "severity": "Low",
     "recommendation": "Raise maxReplicas and set a scale rule.",
     "kql": "resources | where type =~ 'microsoft.app/containerapps' | summarize applicable=count(), failing=countif(toint(properties.template.scale.maxReplicas) == 1)"},
]


def rating(score):
    """Rating label for a pillar score. Pure and testable."""
    if score is None:
        return "Not assessed"
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 50:
        return "Fair"
    return "Poor"


def score_pillars(assessed):
    """Return {pillar: score or None} from assessed checks. Pure and testable.

    assessed: list of {pillar, severity, applicable, failing}.
    """
    weighted, total = {}, {}
    for check in assessed:
        if not check.get("applicable"):
            continue
        weight = WEIGHTS.get(check["severity"], 1)
        pass_ratio = (check["applicable"] - check["failing"]) / check["applicable"]
        weighted[check["pillar"]] = weighted.get(check["pillar"], 0.0) + weight * pass_ratio
        total[check["pillar"]] = total.get(check["pillar"], 0.0) + weight
    scores = {}
    for pillar in PILLARS:
        scores[pillar] = round(100 * weighted[pillar] / total[pillar]) if total.get(pillar) else None
    return scores


def build_report_data(assessed, subs_scanned, notes):
    scores = score_pillars(assessed)
    findings = []
    for check in assessed:
        if check.get("applicable") and check.get("failing"):
            applicable, failing = check["applicable"], check["failing"]
            pass_rate = round(100 * (applicable - failing) / applicable)
            findings.append({
                "pillar": check["pillar"], "check": check["name"], "applicable": applicable, "failing": failing,
                "pass_rate": f"{pass_rate}%", "recommendation": check["recommendation"],
                "severity": check["severity"], "_band": check["severity"],
            })
    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f["severity"], 9), f["pillar"]))

    cards = []
    for pillar in PILLARS:
        score = scores.get(pillar)
        cards.append({"label": pillar, "value": (str(score) if score is not None else "n/a"), "sub": rating(score)})
    score_items = [{"name": pillar, "value": scores[pillar]} for pillar in PILLARS if scores.get(pillar) is not None]
    sev_counts = {}
    for finding in findings:
        sev_counts[finding["severity"]] = sev_counts.get(finding["severity"], 0) + 1
    sev_items = [{"name": b, "value": sev_counts[b], "band": b} for b in ("Critical", "High", "Medium", "Low") if b in sev_counts]

    return {
        "title": "Well-Architected Review",
        "subtitle": "Azure Well-Architected Framework scorecard across five pillars.",
        "meta": {"window": "Point in time", "scope": f"{subs_scanned} subscription(s)", "source": "Azure Resource Graph"},
        "summary_cards": cards,
        "charts": [
            {"title": "Pillar scores", "unit": "score", "items": score_items},
            {"title": "Findings by severity", "unit": "checks", "items": sev_items},
        ],
        "findings": {
            "title": "What pulled the scores down",
            "columns": ["pillar", "check", "applicable", "failing", "pass_rate", "recommendation", "severity"],
            "rows": findings,
        },
        "method_notes": notes + [
            "Score is the weighted pass ratio per pillar. Weights: Critical 4, High 3, Medium 2, Low 1.",
            "Ratings: Excellent 90 and above, Good 75 to 89, Fair 50 to 74, Poor below 50.",
            "This is a roll up; each check names the dedicated skill with the full detail.",
        ],
    }


def _headers():
    from azure.identity import DefaultAzureCredential

    token = DefaultAzureCredential().get_token(f"{ARM_ENDPOINT}/.default").token
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _run_graph(headers, query):
    import requests

    url = f"{ARM_ENDPOINT}/providers/Microsoft.ResourceGraph/resources?api-version=2022-10-01"
    payload = {"query": query, "options": {"resultFormat": "objectArray"}}
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    return response.json().get("data", [])


def _count_subscriptions(headers):
    import requests

    url = f"{ARM_ENDPOINT}/subscriptions?api-version=2022-12-01"
    total = 0
    while url:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        body = response.json()
        total += len([s for s in body.get("value", []) if s.get("state") in (None, "Enabled")])
        url = body.get("nextLink")
    return total


def main() -> dict:
    headers = _headers()
    notes = []
    try:
        subs = _count_subscriptions(headers)
    except Exception:  # noqa: BLE001
        subs = 0

    assessed = []
    for check in CHECKS:
        try:
            rows = _run_graph(headers, check["kql"])
            row = rows[0] if rows else {}
            assessed.append({**check, "applicable": int(row.get("applicable", 0) or 0), "failing": int(row.get("failing", 0) or 0)})
        except Exception:  # noqa: BLE001
            notes.append(f"Check skipped (not readable): {check['name']}.")
    return build_report_data(assessed, subs, notes)


if __name__ == "__main__":
    print(json.dumps(main()))
