"""Tests for the parts of agent_identity that do not touch Azure."""

import base64
import json
import unittest

from agent_identity import agent_resource_id, token_claims


def fake_token(claims):
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
    return "header.%s.signature" % payload


class TestTokenClaims(unittest.TestCase):
    def test_payload_is_decoded_without_padding(self):
        self.assertEqual(token_claims(fake_token({"oid": "abc"}))["oid"], "abc")

    def test_every_padding_length_decodes(self):
        for size in range(1, 9):
            claims = {"oid": "x" * size}
            self.assertEqual(token_claims(fake_token(claims))["oid"], claims["oid"])


class TestAgentResourceId(unittest.TestCase):
    """The agent resource is the route to the identity that holds the roles, so a token
    from anywhere else must not be mistaken for one."""

    def test_an_agent_token_yields_the_resource(self):
        mirid = "/subscriptions/s/resourcegroups/rg/providers/Microsoft.App/agents/a1"
        self.assertEqual(agent_resource_id(fake_token({"xms_mirid": mirid})), mirid)

    def test_a_user_token_has_no_agent_resource(self):
        self.assertIsNone(agent_resource_id(fake_token({"oid": "user"})))

    def test_a_non_agent_managed_identity_is_rejected(self):
        mirid = "/subscriptions/s/resourcegroups/rg/providers/Microsoft.Compute/virtualMachines/vm1"
        self.assertIsNone(agent_resource_id(fake_token({"xms_mirid": mirid})))

    def test_casing_of_the_resource_path_does_not_matter(self):
        mirid = "/subscriptions/s/resourceGroups/rg/providers/Microsoft.App/AGENTS/a1"
        self.assertEqual(agent_resource_id(fake_token({"xms_mirid": mirid})), mirid)


if __name__ == "__main__":
    unittest.main()
