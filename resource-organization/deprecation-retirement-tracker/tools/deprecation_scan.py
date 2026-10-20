"""
deprecation_scan: Find retiring and end of life Azure elements with Resource Graph.

Azure SRE Agent Python tool. Uses the agent managed identity (ARM scope) to query
Azure Resource Graph for end of life App Service runtimes, retired database single
servers, classic resources, old Kubernetes versions, and end of life operating
system images, assigns a category and severity, and prints a report_data object
as JSON ready to pipe into report_render.py.

    python deprecation_scan.py | python report_render.py

Heavy imports (azure-identity, requests) are lazy so the pure predicates can be
unit tested without them. Retirement dates move; corroborate specifics against
Azure Service Health. See references/checks-catalog.md.
"""

import json

ARM_ENDPOINT = "https://management.azure.com"
SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
K8S_FLOOR_MINOR = 28  # supported floor: below 1.28 is flagged

# App Service Linux runtimes. Match is startswith on the uppercased linuxFxVersion.
EOL_RUNTIMES = [
    ("PYTHON|3.6", "Python 3.6", "High"), ("PYTHON|3.7", "Python 3.7", "High"), ("PYTHON|3.8", "Python 3.8", "Medium"),
    ("NODE|12", "Node 12", "High"), ("NODE|14", "Node 14", "High"), ("NODE|16", "Node 16", "High"), ("NODE|18", "Node 18", "Medium"),
    ("PHP|7", "PHP 7.x", "High"), ("PHP|8.0", "PHP 8.0", "High"), ("PHP|8.1", "PHP 8.1", "Medium"),
    ("DOTNETCORE|2", "ASP.NET Core 2.x", "High"), ("DOTNETCORE|3.1", "ASP.NET Core 3.1", "High"),
    ("DOTNET|5", ".NET 5", "High"), ("DOTNET|6", ".NET 6", "Medium"), ("DOTNET|7", ".NET 7", "High"),
    ("JAVA|8", "Java 8", "Medium"),
]

# End of life OS images. Each entry: (offer_contains, sku_contains, label, severity).
EOL_IMAGES = [
    ("WindowsServer", "2008", "Windows Server 2008", "High"),
    ("WindowsServer", "2012", "Windows Server 2012", "High"),
    ("UbuntuServer", "16.04", "Ubuntu 16.04", "High"),
    ("UbuntuServer", "18.04", "Ubuntu 18.04", "High"),
    ("0001-com-ubuntu-server-focal", "", "Ubuntu 20.04 (nearing end of support)", "Medium"),
    ("CentOS", "", "CentOS (end of life)", "Medium"),
]


def k8s_minor(version):
    """Return the minor version integer from a Kubernetes version, or None. Pure."""
    parts = (version or "").split(".")
    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        return int(parts[1])
    return None


def k8s_severity(minor, floor=K8S_FLOOR_MINOR):
    """Severity for a Kubernetes minor version, or None when supported. Pure."""
    if minor is None or minor >= floor:
        return None
    return "High" if minor <= floor - 3 else "Medium"


def eol_runtime(linux_fx_version):
    """Return (label, severity) for an end of life runtime, or None. Pure."""
    value = (linux_fx_version or "").upper()
    for prefix, label, severity in EOL_RUNTIMES:
        if value.startswith(prefix):
            return label, severity
    return None


def eol_image(offer, sku):
    """Return (label, severity) for an end of life OS image, or None. Pure."""
    offer_l = (offer or "").lower()
    sku_l = (sku or "").lower()
    for offer_match, sku_match, label, severity in EOL_IMAGES:
        if offer_match.lower() in offer_l and (not sku_match or sku_match.lower() in sku_l):
            return label, severity
    return None


def _finding(row, category, deprecated, recommendation, severity, resource_type):
    return {
        "resource": row.get("name", ""),
        "resource_type": resource_type,
        "category": category,
        "resource_id": row.get("id", ""),
        "subscription": row.get("subscriptionId", ""),
        "resource_group": row.get("resourceGroup", ""),
        "deprecated": deprecated,
        "recommendation": recommendation,
        "severity": severity,
        "_band": severity,
    }


def scan_app_service(rows):
    findings = []
    for row in rows:
        match = eol_runtime(row.get("fx"))
        if match:
            label, severity = match
            findings.append(_finding(row, "App Service runtime", f"{label} runtime", "Move the app to a supported runtime version.", severity, "App Service"))
    return findings


def scan_retired_types(rows):
    findings = []
    for row in rows:
        rtype = (row.get("type") or "").lower()
        if rtype.startswith("microsoft.classic"):
            findings.append(_finding(row, "Classic", "Classic (Azure Service Manager) resource", "Migrate to the Azure Resource Manager equivalent.", "High", row.get("type", "Classic")))
        elif rtype in ("microsoft.dbforpostgresql/servers", "microsoft.dbformysql/servers"):
            engine = "PostgreSQL" if "postgres" in rtype else "MySQL"
            findings.append(_finding(row, "Retired service", f"{engine} Single Server (retired)", "Migrate to Flexible Server.", "High", f"{engine} Single Server"))
    return findings


def scan_aks(rows, floor=K8S_FLOOR_MINOR):
    findings = []
    for row in rows:
        version = row.get("kubernetesVersion")
        severity = k8s_severity(k8s_minor(version), floor)
        if severity:
            findings.append(_finding(row, "AKS version", f"Kubernetes {version} (below the supported floor)", "Upgrade to a supported version and stay within the N minus two window.", severity, "AKS cluster"))
    return findings


def scan_vm_os(rows):
    findings = []
    for row in rows:
        match = eol_image(row.get("offer"), row.get("sku"))
        if match:
            label, severity = match
            findings.append(_finding(row, "VM OS", f"{label} image", "Rebuild on a supported image, or move to a managed platform.", severity, "Virtual machine"))
    return findings


def build_report_data(findings, subs_scanned, notes):
    findings = sorted(findings, key=lambda f: SEVERITY_ORDER.get(f["severity"], 9))
    high = sum(1 for f in findings if f["severity"] in ("Critical", "High"))
    categories = {}
    sev_counts = {}
    for finding in findings:
        categories[finding["category"]] = categories.get(finding["category"], 0) + 1
        sev_counts[finding["severity"]] = sev_counts.get(finding["severity"], 0) + 1
    sev_items = [{"name": b, "value": sev_counts[b], "band": b} for b in ("Critical", "High", "Medium", "Low") if b in sev_counts]
    cat_items = sorted(({"name": k, "value": v} for k, v in categories.items()), key=lambda i: i["value"], reverse=True)
    return {
        "title": "Deprecation and Retirement Tracker",
        "subtitle": "End of life runtimes, retired tiers, and old platform versions.",
        "meta": {"window": "Point in time", "scope": f"{subs_scanned} subscription(s)", "source": "Azure Resource Graph"},
        "summary_cards": [
            {"label": "Deprecations found", "value": f"{len(findings):,}"},
            {"label": "Retired or end of life", "value": f"{high:,}", "sub": "plan these first"},
            {"label": "Categories affected", "value": str(len(categories))},
            {"label": "Subscriptions scanned", "value": str(subs_scanned)},
        ],
        "charts": [
            {"title": "Findings by severity", "unit": "items", "items": sev_items},
            {"title": "Findings by category", "unit": "items", "items": cat_items},
        ],
        "findings": {
            "title": "Deprecations and retirements",
            "columns": ["resource", "resource_type", "category", "subscription", "deprecated", "recommendation", "severity"],
            "rows": findings,
        },
        "method_notes": notes + [
            f"Kubernetes floor: minor {K8S_FLOOR_MINOR}. Clusters below it are flagged.",
            "Retirement dates move. Corroborate the specifics against Azure Service Health planned retirements.",
            "Deprecated API versions and Basic tier retirements are covered elsewhere; see the checks catalog.",
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
    findings = []
    scanned = set()
    queries = [
        ("resources | where type =~ 'microsoft.web/sites' | extend fx = tostring(properties.siteConfig.linuxFxVersion) | where isnotempty(fx) | project name, id, subscriptionId, resourceGroup, fx", scan_app_service),
        ("resources | where type startswith 'microsoft.classic' or type in~ ('microsoft.dbforpostgresql/servers','microsoft.dbformysql/servers') | project name, id, type, subscriptionId, resourceGroup", scan_retired_types),
        ("resources | where type =~ 'microsoft.containerservice/managedclusters' | project name, id, subscriptionId, resourceGroup, kubernetesVersion=tostring(properties.kubernetesVersion)", scan_aks),
        ("resources | where type =~ 'microsoft.compute/virtualmachines' | extend img = properties.storageProfile.imageReference | project name, id, subscriptionId, resourceGroup, offer=tostring(img.offer), sku=tostring(img.sku), publisher=tostring(img.publisher)", scan_vm_os),
    ]
    for query, scanner in queries:
        try:
            rows = _run_graph(headers, query)
        except Exception as error:  # noqa: BLE001
            notes.append(f"A deprecation query could not be read ({error}).")
            continue
        for row in rows:
            scanned.add(row.get("subscriptionId"))
        findings.extend(scanner(rows))
    return build_report_data(findings, len({s for s in scanned if s}), notes)


if __name__ == "__main__":
    print(json.dumps(main()))
