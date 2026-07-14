"""Unit tests for the pure helpers in identity_access (no Azure calls)."""

import identity_access as ia

OWNER = "8e3af657-a8ff-443c-a75c-2fe8c4bcb635"
CONTRIB = "b24988ac-6180-42a0-ab88-20f7382dd24c"


def _assignment(role_id, ptype, scope):
    return {"properties": {"roleDefinitionId": f"/subscriptions/a/providers/Microsoft.Authorization/roleDefinitions/{role_id}", "principalId": "p1234567890abc", "principalType": ptype, "scope": scope}}


def test_role_name_from_id():
    assert ia.role_name_from_id(f"/.../{OWNER}") == "Owner"
    assert ia.role_name_from_id("/.../unknownguid") is None


def test_scope_kind():
    assert ia.scope_kind("/subscriptions/a", "a") == "subscription"
    assert ia.scope_kind("/providers/Microsoft.Management/managementGroups/mg1", "a") == "management group"
    assert ia.scope_kind("/subscriptions/a/resourceGroups/rg1", "a") == "resource group"


def test_service_principal_owner_is_high():
    finding = ia.classify_assignment(_assignment(OWNER, "ServicePrincipal", "/subscriptions/a"), "a")
    assert finding["severity"] == "High"
    assert finding["role"] == "Owner"


def test_user_owner_is_medium():
    finding = ia.classify_assignment(_assignment(OWNER, "User", "/subscriptions/a"), "a")
    assert finding["severity"] == "Medium"


def test_unknown_principal_is_medium():
    finding = ia.classify_assignment(_assignment(CONTRIB, "Unknown", "/subscriptions/a"), "a")
    assert finding["severity"] == "Medium"


def test_non_privileged_role_ignored():
    assert ia.classify_assignment(_assignment("some-reader-guid", "User", "/subscriptions/a"), "a") is None


def test_owner_sprawl():
    assert ia.owner_sprawl_finding("a", 5, threshold=3)["severity"] == "High"
    assert ia.owner_sprawl_finding("a", 2, threshold=3) is None


def test_build_report_data_counts_sp():
    findings = [ia.classify_assignment(_assignment(OWNER, "ServicePrincipal", "/subscriptions/a"), "a")]
    data = ia.build_report_data(findings, 1, {"a": "Sub A"}, [])
    assert data["summary_cards"][1]["value"] == "1"


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"ok {name}")
    print("all identity_access tests passed")
