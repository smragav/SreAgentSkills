"""
network_exposure: Map the internet facing attack surface with Resource Graph.

Azure SRE Agent Python tool. Uses the agent managed identity (ARM scope) to query
Azure Resource Graph for inbound network security group rules open to the
internet, storage accounts with public or anonymous access, and platform services
with public network access, classifies each by severity, and prints a report_data
object as JSON ready to pipe into report_render.py.

    python network_exposure.py | python report_render.py

Heavy imports (azure-identity, requests) are lazy so the pure classification
helpers can be unit tested without them. See references/checks-catalog.md.
"""

import json

ARM_ENDPOINT = "https://management.azure.com"
SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}

INTERNET_SOURCES = {"*", "internet", "0.0.0.0/0"}
MGMT_PORTS = {22, 3389, 5985, 5986}
DB_PORTS = {1433, 3306, 5432, 6379, 27017, 1521}

TYPE_LABEL = {
    "microsoft.sql/servers": "SQL server",
    "microsoft.keyvault/vaults": "Key Vault",
    "microsoft.documentdb/databaseaccounts": "Cosmos DB",
    "microsoft.dbforpostgresql/flexibleservers": "PostgreSQL",
    "microsoft.dbformysql/flexibleservers": "MySQL",
}


def source_is_internet(source, sources):
    """True when a rule source is the open internet. Pure and testable."""
    values = [source] + list(sources or [])
    return any((value or "").strip().lower() in INTERNET_SOURCES for value in values)


def port_in_spec(port, spec):
    """True when a port falls within a port spec ('22', '*', '1000-2000'). Pure."""
    spec = (spec or "").strip()
    if not spec:
        return False
    if spec == "*":
        return True
    if "-" in spec:
        try:
            low, high = spec.split("-", 1)
            return int(low) <= port <= int(high)
        except ValueError:
            return False
    return spec.isdigit() and int(spec) == port


def classify_open_ports(specs):
    """Return (severity, label) for a set of destination port specs. Pure."""
    specs = [s for s in specs if s]
    if any(s.strip() in ("*", "0-65535") for s in specs):
        return "Critical", "all ports open to the internet"
    if any(any(port_in_spec(p, s) for s in specs) for p in MGMT_PORTS):
        return "Critical", "management ports (SSH/RDP) open to the internet"
    if any(any(port_in_spec(p, s) for s in specs) for p in DB_PORTS):
        return "High", "database ports open to the internet"
    return "Medium", "ports open to the internet"


def classify_nsg_rule(row):
    """Return a finding for an internet facing NSG rule, or None. Pure."""
    if not source_is_internet(row.get("src"), row.get("srcs")):
        return None
    specs = [row.get("portRange")] + list(row.get("portRanges") or [])
    specs = [s for s in specs if s]
    if not specs:
        return None
    severity, label = classify_open_ports(specs)
    ports = ", ".join(specs)
    return {
        "resource": row.get("name", ""),
        "exposure": "Open ports",
        "resource_id": row.get("id", ""),
        "subscription": row.get("subscriptionId", ""),
        "resource_group": row.get("resourceGroup", ""),
        "detail": f"{row.get('ruleName', '')}: {label} (ports {ports})",
        "recommendation": "Restrict the source to known ranges, or use a bastion, load balancer, or Private Link.",
        "severity": severity,
        "_band": severity,
    }


def _finding(row, exposure, detail, recommendation, severity, name=None, rtype=None):
    return {
        "resource": name or row.get("name", ""),
        "exposure": exposure,
        "resource_id": row.get("id", ""),
        "subscription": row.get("subscriptionId", ""),
        "resource_group": row.get("resourceGroup", ""),
        "detail": detail,
        "recommendation": recommendation,
        "severity": severity,
        "_band": severity,
    }


def build_report_data(findings, subs_scanned, notes):
    findings = sorted(findings, key=lambda f: SEVERITY_ORDER.get(f["severity"], 9))
    critical = sum(1 for f in findings if f["severity"] == "Critical")
    public_access = sum(1 for f in findings if f["exposure"] in ("Storage public access", "PaaS public access"))
    sev_counts, by_type = {}, {}
    for finding in findings:
        sev_counts[finding["severity"]] = sev_counts.get(finding["severity"], 0) + 1
        by_type[finding["exposure"]] = by_type.get(finding["exposure"], 0) + 1
    sev_items = [{"name": b, "value": sev_counts[b], "band": b} for b in ("Critical", "High", "Medium", "Low") if b in sev_counts]
    type_items = sorted(({"name": k, "value": v} for k, v in by_type.items()), key=lambda i: i["value"], reverse=True)
    return {
        "title": "Network Exposure Review",
        "subtitle": "Internet facing attack surface: open ports and public access.",
        "meta": {"window": "Point in time", "scope": f"{subs_scanned} subscription(s)", "source": "Azure Resource Graph"},
        "summary_cards": [
            {"label": "Exposed resources", "value": f"{len({f['resource'] for f in findings}):,}"},
            {"label": "Critical exposures", "value": f"{critical:,}", "sub": "management or all ports"},
            {"label": "Public access", "value": f"{public_access:,}", "sub": "storage or PaaS"},
            {"label": "Subscriptions scanned", "value": str(subs_scanned)},
        ],
        "charts": [
            {"title": "Findings by severity", "unit": "findings", "items": sev_items},
            {"title": "Findings by exposure type", "unit": "findings", "items": type_items},
        ],
        "findings": {
            "title": "Exposure findings",
            "columns": ["resource", "exposure", "subscription", "resource_group", "detail", "recommendation", "severity"],
            "rows": findings,
        },
        "method_notes": notes + [
            "A rule is internet facing when its source is *, Internet, or 0.0.0.0/0.",
            "A resource can appear more than once when it is exposed in more than one way.",
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


NSG_QUERY = (
    "resources | where type =~ 'microsoft.network/networksecuritygroups' "
    "| mv-expand rule = properties.securityRules | extend p = rule.properties "
    "| where tostring(p.direction) =~ 'Inbound' and tostring(p.access) =~ 'Allow' "
    "| project name, id, resourceGroup, subscriptionId, ruleName=tostring(rule.name), "
    "src=tostring(p.sourceAddressPrefix), srcs=p.sourceAddressPrefixes, "
    "portRange=tostring(p.destinationPortRange), portRanges=p.destinationPortRanges"
)


def main() -> dict:
    headers = _headers()
    notes, findings, scanned = [], [], set()

    def scan(query, handler):
        try:
            rows = _run_graph(headers, query)
        except Exception as error:  # noqa: BLE001
            notes.append(f"A query could not be read ({error}).")
            return
        for row in rows:
            scanned.add(row.get("subscriptionId"))
            handler(row)

    scan(NSG_QUERY, lambda row: (lambda f: findings.append(f) if f else None)(classify_nsg_rule(row)))
    scan(
        "resources | where type =~ 'microsoft.storage/storageaccounts' | where tostring(properties.allowBlobPublicAccess) =~ 'true' | project name, id, resourceGroup, subscriptionId",
        lambda row: findings.append(_finding(row, "Storage public access", "Anonymous blob public access allowed", "Set allowBlobPublicAccess to false unless anonymous access is a reviewed requirement.", "High")),
    )
    scan(
        "resources | where type =~ 'microsoft.storage/storageaccounts' | where tostring(properties.publicNetworkAccess) =~ 'Enabled' and tostring(properties.networkAcls.defaultAction) =~ 'Allow' | project name, id, resourceGroup, subscriptionId",
        lambda row: findings.append(_finding(row, "Storage public access", "Open to all networks (no firewall)", "Set the network default action to Deny and allow only known networks, or use Private Link.", "Medium")),
    )
    scan(
        "resources | where type in~ ('microsoft.sql/servers','microsoft.keyvault/vaults','microsoft.documentdb/databaseaccounts','microsoft.dbforpostgresql/flexibleservers','microsoft.dbformysql/flexibleservers') | extend pna = tostring(properties.publicNetworkAccess) | where pna =~ 'Enabled' | project name, id, type, resourceGroup, subscriptionId",
        lambda row: findings.append(_finding(row, "PaaS public access", f"{TYPE_LABEL.get((row.get('type') or '').lower(), row.get('type', ''))}: public network access enabled", "Disable public network access and use Private Link, or restrict to known networks.", "Medium")),
    )

    return build_report_data(findings, len({s for s in scanned if s}), notes)


if __name__ == "__main__":
    print(json.dumps(main()))
