"""agent_identity: authenticate as the identity that actually holds the roles.

An Azure SRE Agent commonly carries both a system assigned and a user assigned managed
identity. The runtime resolves to the system assigned one, which is frequently created
with no role assignments at all. Azure Resource Graph answers such a caller with HTTP
200 and a nearly empty result rather than an error, so a skill renders a confident
report on an estate it never saw. Measured on one agent: 15 resources visible where the
user assigned identity saw 1140.

The token the runtime issues names the agent resource in its `xms_mirid` claim, and that
resource lists the identities attached to it, so the right client id is discovered
rather than configured. Outside an agent there is no such claim and the ambient
credential is used unchanged.

Bundled with every skill by shared/iac/deploy-skill.ps1, which flattens shared/tools and
the skill's own tools into one directory.
"""

import base64
import json
import os

ARM_ENDPOINT = "https://management.azure.com"
AGENT_API_VERSION = "2025-05-01-preview"

_UNRESOLVED = object()
_cached_client_id = _UNRESOLVED


def token_claims(token):
    """The payload of a token this process already holds. Not a validation step."""
    body = token.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))


def agent_resource_id(token):
    """The agent resource a managed identity token was issued for, or None."""
    resource = token_claims(token).get("xms_mirid") or ""
    return resource if "/agents/" in resource.lower() else None


def resolve_agent_identity():
    """Client id of the user assigned identity attached to this agent, or None.

    Best effort by design. A failure here means the caller falls back to the ambient
    credential, which is the behaviour on a workstation, so it must never raise.
    """
    global _cached_client_id
    if _cached_client_id is not _UNRESOLVED:
        return _cached_client_id

    _cached_client_id = None
    try:
        import requests
        from azure.identity import DefaultAzureCredential

        token = DefaultAzureCredential().get_token(f"{ARM_ENDPOINT}/.default").token
        resource = agent_resource_id(token)
        if resource:
            response = requests.get(
                f"{ARM_ENDPOINT}{resource}?api-version={AGENT_API_VERSION}",
                headers={"Authorization": f"Bearer {token}"}, timeout=60)
            if response.status_code == 200:
                identities = (response.json().get("identity") or {}).get("userAssignedIdentities") or {}
                for details in identities.values():
                    if details.get("clientId"):
                        _cached_client_id = details["clientId"]
                        break
    except Exception:
        _cached_client_id = None
    return _cached_client_id


def agent_credential(client_id=None):
    """A credential pinned to the identity that holds the roles."""
    from azure.identity import DefaultAzureCredential

    client_id = client_id or os.environ.get("AZURE_CLIENT_ID") or resolve_agent_identity()
    if client_id:
        return DefaultAzureCredential(managed_identity_client_id=client_id)
    return DefaultAzureCredential()


def agent_token(scope=None, client_id=None):
    return agent_credential(client_id).get_token(scope or f"{ARM_ENDPOINT}/.default").token


def arm_headers(client_id=None):
    return {"Authorization": f"Bearer {agent_token(client_id=client_id)}",
            "Content-Type": "application/json"}


def identity_report(client_id=None, scopes=None):
    """Which principal each audience resolves to. Answers 'authorization failed' fast."""
    client_id = client_id or os.environ.get("AZURE_CLIENT_ID") or resolve_agent_identity()
    report = {"client_id_in_use": client_id or "(none, implicit)"}
    for label, scope in (scopes or (("resource_manager", f"{ARM_ENDPOINT}/.default"),)):
        try:
            claims = token_claims(agent_token(scope, client_id))
            report[label] = {
                "object_id": claims.get("oid", ""),
                "app_id": claims.get("appid", ""),
                "identity_resource": claims.get("xms_mirid", ""),
            }
        except Exception as error:
            report[label] = {"error": str(error)[:300]}
    return report
