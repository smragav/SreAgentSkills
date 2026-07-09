"""
backup_coverage: Measure Azure Backup coverage for virtual machines.

Azure SRE Agent Python tool. Uses the agent managed identity (ARM scope) to
enumerate virtual machines and Azure Backup protected items with Azure Resource
Graph, matches them by resource id, classifies each machine as protected and
healthy, unprotected, unhealthy, or stale, and prints a report_data object as
JSON on standard output ready to pipe into report_render.py.

    python backup_coverage.py | python report_render.py

Heavy imports (azure-identity, requests) are lazy so the pure classification and
summary helpers can be unit tested without them. See references/checks-catalog.md.
"""

import json
import sys
from datetime import datetime, timezone

ARM_ENDPOINT = "https://management.azure.com"
STALE_DAYS_DEFAULT = 3
HEALTHY = ("passed", "healthy")


def _parse_time(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def classify_vm(vm, protected, stale_days, now):
    """Return a finding dict for a machine, or None when it is well protected.

    vm: {name, id, resourceGroup, subscriptionId, location}
    protected: {lowercased vm id: {lastBackup, health}}
    Pure and testable.
    """
    base = {
        "resource": vm.get("name", ""),
        "resource_id": vm.get("id", ""),
        "subscription": vm.get("subscriptionId", ""),
        "resource_group": vm.get("resourceGroup", ""),
        "last_backup": "",
    }
    info = protected.get((vm.get("id") or "").lower())
    if not info:
        base.update(
            state="Unprotected",
            severity="High",
            recommendation="Enable Azure Backup with a policy that meets the recovery point objective.",
        )
        return base

    base["last_backup"] = info.get("lastBackup", "") or ""
    health = (info.get("health") or "").lower()
    if health and health not in HEALTHY:
        base.update(
            state="Unhealthy",
            severity="High",
            recommendation="Investigate the failed backup job in the vault; the last backups did not succeed.",
        )
        return base

    last = _parse_time(info.get("lastBackup"))
    if last is None or (now - last).days > stale_days:
        base.update(
            state="Stale",
            severity="High",
            recommendation=f"No successful backup within {stale_days} day(s); check the schedule and the last job.",
        )
        return base

    return None


def coverage_summary(vms, protected, stale_days, now):
    """Return (findings, counts) where counts has total, protected_healthy,
    unprotected, at_risk, coverage_percent. Pure and testable."""
    findings = []
    for vm in vms:
        finding = classify_vm(vm, protected, stale_days, now)
        if finding:
            findings.append(finding)
    total = len(vms)
    unprotected = sum(1 for f in findings if f["state"] == "Unprotected")
    at_risk = sum(1 for f in findings if f["state"] in ("Unhealthy", "Stale"))
    healthy = total - unprotected - at_risk
    coverage = round(healthy / total * 100.0, 1) if total else 100.0
    return findings, {
        "total": total,
        "protected_healthy": healthy,
        "unprotected": unprotected,
        "at_risk": at_risk,
        "coverage_percent": coverage,
    }


def build_report_data(vms, protected, sub_names, stale_days, now, notes):
    findings, counts = coverage_summary(vms, protected, stale_days, now)
    for finding in findings:
        finding["_band"] = finding["severity"]
        finding["subscription"] = sub_names.get(finding["subscription"], finding["subscription"])
    by_sub = {}
    for finding in findings:
        by_sub[finding["subscription"]] = by_sub.get(finding["subscription"], 0) + 1
    sub_chart = [{"name": name, "value": value} for name, value in by_sub.items()]
    sub_chart.sort(key=lambda item: item["value"], reverse=True)
    return {
        "title": "Backup and Recovery Coverage",
        "subtitle": "Virtual machine backup protection and health from Azure Backup.",
        "meta": {
            "window": f"{stale_days} day staleness",
            "scope": f"{len({vm.get('subscriptionId') for vm in vms})} subscription(s)",
            "source": "Azure Resource Graph",
        },
        "summary_cards": [
            {"label": "Coverage", "value": f"{counts['coverage_percent']}%", "sub": "protected and healthy"},
            {"label": "Virtual machines", "value": f"{counts['total']:,}"},
            {"label": "Unprotected", "value": f"{counts['unprotected']:,}"},
            {"label": "At risk", "value": f"{counts['at_risk']:,}", "sub": "unhealthy or stale"},
        ],
        "charts": [
            {
                "title": "Backup state",
                "unit": "machines",
                "items": [
                    {"name": "Protected", "value": counts["protected_healthy"], "band": "Low"},
                    {"name": "At risk", "value": counts["at_risk"], "band": "High"},
                    {"name": "Unprotected", "value": counts["unprotected"], "band": "Critical"},
                ],
            },
            {"title": "Gaps by subscription", "unit": "gaps", "items": sub_chart},
        ],
        "findings": {
            "title": "Backup gaps",
            "columns": ["resource", "subscription", "resource_group", "state", "last_backup", "recommendation", "severity"],
            "rows": findings,
        },
        "method_notes": notes
        + [
            f"Staleness window: {stale_days} day(s). A machine with no successful backup in that window is flagged as stale.",
            "Azure SQL long term retention, Azure Files, and Cosmos DB backup are spot checked by hand; see references/checks-catalog.md.",
            "Coverage is protected and healthy machines divided by all machines in scope.",
        ],
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


PROTECTED_QUERY = (
    "recoveryservicesresources "
    "| where type =~ 'microsoft.recoveryservices/vaults/backupfabrics/protectioncontainers/protecteditems' "
    "| where properties.backupManagementType =~ 'AzureIaasVM' "
    "| extend srcId = tolower(tostring(coalesce(properties.virtualMachineId, properties.sourceResourceId))) "
    "| project srcId, lastBackup=tostring(properties.lastBackupTime), health=tostring(properties.healthStatus)"
)
VM_QUERY = "resources | where type =~ 'microsoft.compute/virtualmachines' | project name, id, resourceGroup, subscriptionId, location"


def main(stale_days: int = STALE_DAYS_DEFAULT) -> dict:
    headers = _headers()
    notes = []
    try:
        sub_names = _list_subscription_names(headers)
    except Exception as error:  # noqa: BLE001
        sub_names, _ = {}, notes.append(f"Could not list subscription names ({error}).")
    try:
        vms = _run_graph(headers, VM_QUERY)
    except Exception as error:  # noqa: BLE001
        return {"title": "Backup and Recovery Coverage", "method_notes": [f"Could not enumerate virtual machines ({error})."], "findings": {"rows": []}}
    protected = {}
    try:
        for row in _run_graph(headers, PROTECTED_QUERY):
            if row.get("srcId"):
                protected[row["srcId"]] = {"lastBackup": row.get("lastBackup"), "health": row.get("health")}
    except Exception as error:  # noqa: BLE001
        notes.append(f"Could not read protected items ({error}); coverage may read low.")
    return build_report_data(vms, protected, sub_names, int(stale_days), datetime.now(timezone.utc), notes)


if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else STALE_DAYS_DEFAULT
    print(json.dumps(main(days)))
