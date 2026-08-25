"""
expiry_scan: Rank Azure certificates, secrets, and credentials by days to expiry.

Azure SRE Agent Python tool. Uses the agent managed identity to read App Service
certificates (Azure Resource Graph), Key Vault certificates and secrets (vault
data plane), and application credentials (Microsoft Graph), computes the days to
expiry for each, and prints a report_data object as JSON ready to pipe into
report_render.py.

    python expiry_scan.py [horizon_days] | python report_render.py

Heavy imports (azure-identity, requests) are lazy so the pure classification
helpers can be unit tested without them. See references/checks-catalog.md.
"""

import json
import sys
from datetime import datetime, timezone

ARM_ENDPOINT = "https://management.azure.com"
VAULT_AUDIENCE = "https://vault.azure.net"
GRAPH_ENDPOINT = "https://graph.microsoft.com"
HORIZON_DEFAULT = 60
SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def days_to_expiry(expiry, now):
    """Whole days until expiry; negative when already expired. Pure."""
    if expiry is None:
        return None
    return (expiry - now).days


def severity_for_days(days):
    """Severity band from days remaining. Pure and testable."""
    if days is None:
        return None
    if days < 0:
        return "Critical"
    if days <= 14:
        return "High"
    if days <= 30:
        return "Medium"
    return "Low"


def time_bucket(days):
    if days is None:
        return "Unknown"
    if days < 0:
        return "Expired"
    if days <= 14:
        return "Within 14 days"
    if days <= 30:
        return "15 to 30 days"
    return "31 days to horizon"


def classify_item(item, now, horizon):
    """Turn a raw item into a finding, or None when outside the horizon. Pure.

    item: {name, kind, source, subscription, resource_group, expiry(datetime)}.
    """
    expiry = item.get("expiry")
    days = days_to_expiry(expiry, now)
    if days is None or days > horizon:
        return None
    severity = severity_for_days(days)
    return {
        "item": item.get("name", ""),
        "kind": item.get("kind", ""),
        "source": item.get("source", ""),
        "subscription": item.get("subscription", ""),
        "expires": expiry.strftime("%Y-%m-%d") if expiry else "",
        "days_left": days,
        "recommendation": item.get("recommendation", "Renew or rotate before expiry and update the consumers."),
        "severity": severity,
        "_band": severity,
        "_sort": days,
    }


def build_report_data(items, horizon, subs_scanned, notes, now=None):
    now = now or datetime.now(timezone.utc)
    findings = [f for f in (classify_item(item, now, horizon) for item in items) if f]
    findings.sort(key=lambda f: f["_sort"])
    expired = sum(1 for f in findings if f["days_left"] < 0)
    certs = sum(1 for f in findings if "cert" in f["kind"].lower())
    secrets = len(findings) - certs
    sev_counts, bucket_counts = {}, {}
    for f in findings:
        sev_counts[f["severity"]] = sev_counts.get(f["severity"], 0) + 1
        bucket = time_bucket(f["days_left"])
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
    sev_items = [{"name": b, "value": sev_counts[b], "band": b} for b in ("Critical", "High", "Medium", "Low") if b in sev_counts]
    bucket_order = ["Expired", "Within 14 days", "15 to 30 days", "31 days to horizon"]
    bucket_items = [{"name": b, "value": bucket_counts[b]} for b in bucket_order if b in bucket_counts]
    return {
        "title": "Certificate and Secret Expiry",
        "subtitle": "Certificates, secrets, and credentials by days to expiry.",
        "meta": {"window": f"{horizon} day horizon", "scope": f"{subs_scanned} subscription(s)", "source": "Key Vault, App Service, Graph"},
        "summary_cards": [
            {"label": "Expiring within horizon", "value": f"{len(findings):,}"},
            {"label": "Already expired", "value": f"{expired:,}"},
            {"label": "Certificates", "value": f"{certs:,}"},
            {"label": "Secrets and credentials", "value": f"{secrets:,}"},
        ],
        "charts": [
            {"title": "Items by urgency", "unit": "items", "items": sev_items},
            {"title": "Items by time bucket", "unit": "items", "items": bucket_items},
        ],
        "findings": {
            "title": "Expiring items",
            "columns": ["item", "kind", "source", "subscription", "expires", "days_left", "recommendation", "severity"],
            "rows": findings,
        },
        "method_notes": notes + [
            f"Horizon: {horizon} days. Items expiring later are not shown; anything already expired is always shown.",
            "Certificates embedded in an Application Gateway or Front Door listener are not enumerated; prefer Key Vault referenced certificates.",
        ],
    }


def _credential():
    from agent_identity import agent_credential

    return agent_credential()


def _from_unix(value):
    if value in (None, ""):
        return None
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        return None


def _from_iso(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


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


def _read_vault_list(token, base_url):
    import requests

    items, url = [], f"{base_url}?api-version=7.4"
    headers = {"Authorization": f"Bearer {token}"}
    while url:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        body = response.json()
        items.extend(body.get("value", []))
        url = body.get("nextLink")
    return items


def _collect(headers, credential):
    """Gather raw items from all sources. Returns (items, notes)."""
    import requests

    items, notes = [], []

    try:
        for cert in _run_graph(headers, "resources | where type =~ 'microsoft.web/certificates' | project name, subscriptionId, resourceGroup, expirationDate=tostring(properties.expirationDate)"):
            items.append({
                "name": cert.get("name", ""), "kind": "App Service certificate", "source": "App Service",
                "subscription": cert.get("subscriptionId", ""), "resource_group": cert.get("resourceGroup", ""),
                "expiry": _from_iso(cert.get("expirationDate")),
                "recommendation": "Renew or replace the certificate and update the binding.",
            })
    except Exception as error:  # noqa: BLE001
        notes.append(f"App Service certificates not read ({error}).")

    try:
        vaults = _run_graph(headers, "resources | where type =~ 'microsoft.keyvault/vaults' | project name, subscriptionId, vaultUri=tostring(properties.vaultUri)")
    except Exception as error:  # noqa: BLE001
        vaults = []
        notes.append(f"Key Vault list not read ({error}).")
    denied_vaults = 0
    if vaults:
        try:
            vault_token = credential.get_token(f"{VAULT_AUDIENCE}/.default").token
        except Exception as error:  # noqa: BLE001
            vault_token = None
            notes.append(f"Could not acquire a Key Vault data plane token ({error}).")
        for vault in vaults:
            uri = (vault.get("vaultUri") or "").rstrip("/")
            if not uri or not vault_token:
                continue
            try:
                for cert in _read_vault_list(vault_token, f"{uri}/certificates"):
                    items.append({
                        "name": (cert.get("id", "").rstrip("/").split("/")[-1]) or vault.get("name"),
                        "kind": "Key Vault certificate", "source": vault.get("name", ""),
                        "subscription": vault.get("subscriptionId", ""),
                        "expiry": _from_unix((cert.get("attributes") or {}).get("exp")),
                        "recommendation": "Renew the certificate; enable autorotation where the issuer supports it.",
                    })
                for secret in _read_vault_list(vault_token, f"{uri}/secrets"):
                    if (secret.get("managed")):
                        continue
                    exp = (secret.get("attributes") or {}).get("exp")
                    if exp is None:
                        continue
                    items.append({
                        "name": (secret.get("id", "").rstrip("/").split("/")[-1]) or vault.get("name"),
                        "kind": "Key Vault secret", "source": vault.get("name", ""),
                        "subscription": vault.get("subscriptionId", ""),
                        "expiry": _from_unix(exp),
                        "recommendation": "Rotate the secret before expiry and update the consumers.",
                    })
            except Exception:  # noqa: BLE001
                denied_vaults += 1
    if denied_vaults:
        notes.append(f"{denied_vaults} vault(s) denied the data plane read and were not assessed. Grant a Key Vault read permission to include them.")

    try:
        graph_token = credential.get_token(f"{GRAPH_ENDPOINT}/.default").token
        url = f"{GRAPH_ENDPOINT}/v1.0/applications?$select=displayName,appId,passwordCredentials,keyCredentials&$top=100"
        gh = {"Authorization": f"Bearer {graph_token}"}
        pages = 0
        while url and pages < 40:
            response = requests.get(url, headers=gh, timeout=90)
            response.raise_for_status()
            body = response.json()
            for app in body.get("value", []):
                name = app.get("displayName", app.get("appId", ""))
                for credkind, key in (("client secret", "passwordCredentials"), ("certificate credential", "keyCredentials")):
                    for cred in app.get(key, []) or []:
                        items.append({
                            "name": f"{name}: {cred.get('displayName') or credkind}", "kind": f"App {credkind}",
                            "source": "Entra ID application", "subscription": "",
                            "expiry": _from_iso(cred.get("endDateTime")),
                            "recommendation": "Roll the credential before expiry and update the consumers.",
                        })
            url = body.get("@odata.nextLink")
            pages += 1
    except Exception as error:  # noqa: BLE001
        notes.append(f"Application credentials from Microsoft Graph not assessed ({error}). Grant a directory read such as Application.Read.All to include them.")

    return items, notes


def _arm_headers(credential):
    return {"Authorization": f"Bearer {credential.get_token(f'{ARM_ENDPOINT}/.default').token}", "Content-Type": "application/json"}


def main(horizon: int = HORIZON_DEFAULT) -> dict:
    credential = _credential()
    headers = _arm_headers(credential)
    items, notes = _collect(headers, credential)
    subs = {item.get("subscription") for item in items if item.get("subscription")}
    return build_report_data(items, int(horizon), len(subs), notes)


if __name__ == "__main__":
    value = int(sys.argv[1]) if len(sys.argv) > 1 else HORIZON_DEFAULT
    print(json.dumps(main(value)))
