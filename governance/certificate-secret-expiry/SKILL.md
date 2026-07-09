---
name: certificate-secret-expiry
description: Use when the user asks about expiring certificates, expiring secrets, certificate or secret rotation, "what is about to expire", Key Vault expiry, TLS certificate expiry, or service principal or app registration credential expiry. Enumerates Key Vault certificates and secrets, App Service certificates, and application credentials, ranks them by days to expiry, and produces a self contained HTML expiry report.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# Certificate and Secret Expiry

This skill finds the certificates, secrets, and credentials that are about to expire across what this agent can read. It enumerates Key Vault certificates and secrets, App Service certificates, and application (service principal) credentials, ranks them by days to expiry, and produces a single self contained HTML report. It removes one of the most common and most avoidable outage classes, the certificate that expired at two in the morning. It runs on demand and, most usefully, as a scheduled sweep with enough lead time to renew.

## When to use this skill

Use this skill when the user asks to:

- Find certificates, secrets, or credentials that are expiring or expired.
- Plan certificate and secret rotation with enough lead time.
- Check Key Vault, App Service, or application credential expiry.

## Operating principles

- Read only. This skill reads expiry metadata. It never renews, rotates, or changes a certificate or secret; it reports what needs renewing and by when.
- Default Reader scope, with honest data plane notes. Key Vault item expiry is data plane metadata that needs a Key Vault read permission, and application credentials come from Microsoft Graph. Where a read is denied, the skill records that source as not assessed and continues. See references/permissions-and-scope.md.
- Evidence first. Every finding names the item, its kind, where it lives, the expiry date, the days remaining, and the recommended action.

## Workflow

The scan tool (tools/expiry_scan.py) and the shared report renderer (tools/report_render.py) are bundled with this skill. Run them with RunInTerminal using the Python in the agent runtime. Both authenticate with the agent managed identity.

### Phase 1: Enumerate expiring items

1. Run python tools/expiry_scan.py [horizon_days] with RunInTerminal. It reads App Service certificates with Azure Resource Graph, Key Vault certificates and secrets from the vault data plane, and application credentials from Microsoft Graph, computes the days to expiry for each, and prints a report_data object as JSON. The horizon defaults to 60 days; everything expiring within it, plus anything already expired, is reported.
2. For any source the tool notes it could not read (a vault that denied the data plane read, or Graph without the directory permission), record it as not assessed rather than a failure.

### Phase 2: Produce the report

1. Pipe the scan into the renderer: python tools/expiry_scan.py | python tools/report_render.py with RunInTerminal. It writes the self contained HTML report and returns the path. Store it with SaveFileToBlob for a link.
2. Present the report, then a short inline summary: items already expired, items expiring within 14 days, the soonest five with their dates, and any source not assessed.

## Expected output

- Primary: a self contained HTML expiry report, covering items by urgency and by time bucket, and the full table sorted soonest first with the days remaining and the recommended action per item.
- Inline: expired items, items expiring within 14 days, and the soonest five.
- Every finding names the item, its kind, its location, the expiry date, the days remaining, and the recommended action. Nothing is renewed or rotated; recommendations are for a human to act on.
