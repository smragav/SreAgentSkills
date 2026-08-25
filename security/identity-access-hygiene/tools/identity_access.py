"""
identity_access: Review privileged Azure role assignments for access hygiene.

Azure SRE Agent Python tool. Uses the agent managed identity (ARM scope) to read
role assignments and classic administrators across the accessible subscriptions,
keep the privileged roles, classify each into an access hygiene finding, and print
a report_data object as JSON ready to pipe into report_render.py.

    python identity_access.py | python report_render.py

Heavy imports (azure-identity, requests) are lazy so the pure classification
helpers can be unit tested without them. See references/checks-catalog.md.
"""

import json

ARM_ENDPOINT = "https://management.azure.com"
SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
OWNER_SPRAWL_THRESHOLD = 3

ROLE_BY_ID = {
    "8e3af657-a8ff-443c-a75c-2fe8c4bcb635": "Owner",
    "b24988ac-6180-42a0-ab88-20f7382dd24c": "Contributor",
    "18d7d88d-d35e-4fb5-a5c3-7773c20a72d9": "User Access Administrator",
    "f58310d9-a9f6-439a-9e8d-f62e7b41a168": "Role Based Access Control Administrator",
}
HIGH_PRIVILEGE = {"Owner", "User Access Administrator", "Role Based Access Control Administrator"}


def role_name_from_id(role_definition_id):
    """Return the privileged role name for a roleDefinitionId, or None. Pure."""
    guid = (role_definition_id or "").rstrip("/").split("/")[-1].lower()
    return ROLE_BY_ID.get(guid)


def scope_kind(scope, subscription):
    """Classify an assignment scope. Pure and testable."""
    value = (scope or "").lower()
    if "/managementgroups/" in value:
        return "management group"
    if value == f"/subscriptions/{subscription}".lower():
        return "subscription"
    if "/resourcegroups/" in value and "/providers/" not in value.split("/resourcegroups/", 1)[1]:
        return "resource group"
    return "resource"


def _short(principal_id):
    pid = principal_id or ""
    return pid if len(pid) <= 12 else pid[:8] + "..."


def classify_assignment(assignment, subscription):
    """Return a finding for a privileged assignment, or None. Pure and testable."""
    props = assignment.get("properties", assignment)
    role = role_name_from_id(props.get("roleDefinitionId"))
    if not role:
        return None
    ptype = props.get("principalType", "Unknown")
    scope = scope_kind(props.get("scope"), subscription)
    base = {
        "principal": _short(props.get("principalId")),
        "principal_type": ptype,
        "role": role,
        "scope": scope,
        "subscription": subscription,
        "_band": "Low",
        "severity": "Low",
    }

    def finish(severity, recommendation):
        base["severity"] = severity
        base["_band"] = severity
        base["recommendation"] = recommendation
        return base

    if ptype == "Unknown":
        return finish("Medium", "Remove this stale assignment; the principal appears to be deleted.")
    if role in HIGH_PRIVILEGE and scope == "management group":
        return finish("High", "Confirm this wide scope is intended and scope it down where possible.")
    if ptype == "ServicePrincipal" and role in HIGH_PRIVILEGE:
        return finish("High", "Scope the service principal down to least privilege; avoid subscription wide access administration.")
    if role == "Owner" and ptype == "User":
        return finish("Medium", "Move to just in time Owner through Privileged Identity Management.")
    if role == "Contributor" and ptype == "ServicePrincipal":
        return finish("Low", "Confirm the service principal needs Contributor breadth; scope it down where possible.")
    if role == "Owner":
        return finish("Medium", "Reduce standing Owners; grant Owner just in time through Privileged Identity Management.")
    return None


def owner_sprawl_finding(subscription, owner_count, threshold=OWNER_SPRAWL_THRESHOLD):
    """Return an Owner sprawl finding when over the threshold, else None. Pure."""
    if owner_count <= threshold:
        return None
    return {
        "principal": f"{owner_count} owners",
        "principal_type": "Multiple",
        "role": "Owner",
        "scope": "subscription",
        "subscription": subscription,
        "recommendation": "Reduce standing Owners; grant Owner just in time through Privileged Identity Management.",
        "severity": "High",
        "_band": "High",
    }


def build_report_data(findings, subs_scanned, sub_names, notes):
    for finding in findings:
        finding["subscription"] = sub_names.get(finding["subscription"], finding["subscription"])
    findings = sorted(findings, key=lambda f: SEVERITY_ORDER.get(f["severity"], 9))
    sp_high = sum(1 for f in findings if f["principal_type"] == "ServicePrincipal" and f["role"] in HIGH_PRIVILEGE)
    classic = sum(1 for f in findings if f["role"] == "Classic administrator")
    sev_counts, by_role = {}, {}
    for finding in findings:
        sev_counts[finding["severity"]] = sev_counts.get(finding["severity"], 0) + 1
        by_role[finding["role"]] = by_role.get(finding["role"], 0) + 1
    sev_items = [{"name": b, "value": sev_counts[b], "band": b} for b in ("Critical", "High", "Medium", "Low") if b in sev_counts]
    role_items = sorted(({"name": k, "value": v} for k, v in by_role.items()), key=lambda i: i["value"], reverse=True)
    return {
        "title": "Identity and Access Hygiene",
        "subtitle": "Privileged access across the estate.",
        "meta": {"window": "Point in time", "scope": f"{subs_scanned} subscription(s)", "source": "Azure role assignments"},
        "summary_cards": [
            {"label": "Privileged findings", "value": f"{len(findings):,}"},
            {"label": "High privilege SPs", "value": f"{sp_high:,}", "sub": "service principals"},
            {"label": "Classic admins", "value": f"{classic:,}"},
            {"label": "Subscriptions scanned", "value": str(subs_scanned)},
        ],
        "charts": [
            {"title": "Findings by severity", "unit": "findings", "items": sev_items},
            {"title": "Findings by role", "unit": "findings", "items": role_items},
        ],
        "findings": {
            "title": "Access hygiene findings",
            "columns": ["principal", "principal_type", "role", "scope", "subscription", "recommendation", "severity"],
            "rows": findings,
        },
        "method_notes": notes + [
            f"Owner sprawl threshold: more than {OWNER_SPRAWL_THRESHOLD} Owners at subscription scope.",
            "Principal display names and guest status need a Microsoft Entra read; the report shows the principal id and type.",
        ],
    }


def _headers():
    from agent_identity import agent_token

    token = agent_token(f"{ARM_ENDPOINT}/.default")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _get_all(headers, url):
    import requests

    items = []
    while url:
        response = requests.get(url, headers=headers, timeout=90)
        response.raise_for_status()
        body = response.json()
        items.extend(body.get("value", []))
        url = body.get("nextLink")
    return items


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
        notes.append(f"Could not list subscriptions ({error}).")

    findings = []
    for sub in (sub_names or {}):
        try:
            assignments = _get_all(headers, f"{ARM_ENDPOINT}/subscriptions/{sub}/providers/Microsoft.Authorization/roleAssignments?api-version=2022-04-01")
        except Exception:  # noqa: BLE001
            notes.append(f"Role assignments not read for subscription {sub}.")
            continue
        owner_count = 0
        for assignment in assignments:
            props = assignment.get("properties", {})
            if role_name_from_id(props.get("roleDefinitionId")) == "Owner" and scope_kind(props.get("scope"), sub) == "subscription":
                owner_count += 1
            finding = classify_assignment(assignment, sub)
            if finding:
                findings.append(finding)
        sprawl = owner_sprawl_finding(sub, owner_count)
        if sprawl:
            findings.append(sprawl)
        try:
            for admin in _get_all(headers, f"{ARM_ENDPOINT}/subscriptions/{sub}/providers/Microsoft.Authorization/classicAdministrators?api-version=2015-07-01"):
                props = admin.get("properties", {})
                findings.append({
                    "principal": props.get("emailAddress", "classic admin"), "principal_type": "User",
                    "role": "Classic administrator", "scope": "subscription", "subscription": sub,
                    "recommendation": "Migrate to Azure role based access control and remove the classic administrator.",
                    "severity": "High", "_band": "High",
                })
        except Exception:  # noqa: BLE001
            pass

    return build_report_data(findings, len(sub_names or {}), sub_names, notes)


if __name__ == "__main__":
    print(json.dumps(main()))
