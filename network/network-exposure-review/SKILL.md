---
name: network-exposure-review
description: Use when the user asks about internet exposure, public exposure, attack surface, open ports, NSG rules open to the internet, public IPs, storage public access, or PaaS resources reachable from the internet. Scans the resources the agent can read for network security group rules open to the internet, storage and PaaS with public access, scores each by severity, and produces a self contained HTML exposure report.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# Network Exposure Review

This skill maps the internet facing attack surface of the resources this agent can read. It finds network security group rules that open ports to the internet, storage accounts that allow anonymous or public access, and platform services reachable over the public internet, scores each by severity, and produces a single self contained HTML report. It answers the question a security team asks first: what is reachable from the internet. It runs on demand or as a scheduled sweep.

## When to use this skill

Use this skill when the user asks to:

- Review internet exposure, public attack surface, or open ports.
- Find network security group rules that allow the internet to management or database ports.
- Check which storage accounts and platform services accept public traffic.

## Operating principles

- Read only. This skill reads network and access configuration. It never changes a rule, a firewall, or a public access setting; it reports what is open and the change to close it.
- Default Reader scope. It reads across the subscriptions this agent can read. If a read is denied, it records the scope as not assessed and continues. See references/permissions-and-scope.md.
- Evidence first. Every finding names the resource, what is exposed (the ports and source, or the public access setting), a severity, and the recommended change.

## Workflow

The scan tool (tools/network_exposure.py) and the shared report renderer (tools/report_render.py) are bundled with this skill. Run them with RunInTerminal using the Python in the agent runtime. Both authenticate with the agent managed identity.

### Phase 1: Map the exposure

1. Run python tools/network_exposure.py with RunInTerminal. It queries Azure Resource Graph for inbound network security group rules open to the internet, storage accounts with public or anonymous access, and platform services with public network access, classifies each against references/checks-catalog.md, and prints a report_data object as JSON.
2. Management ports (SSH and RDP) or all ports open to the internet are the most serious; database ports open to the internet are next. Confirm severity with the evidence in the report.

### Phase 2: Produce the report

1. Pipe the scan into the renderer: python tools/network_exposure.py | python tools/report_render.py with RunInTerminal. It writes the self contained HTML report and returns the path. Store it with SaveFileToBlob for a link.
2. Present the report, then a short inline summary: critical exposures (management or all ports open), resources with public access, the top items, and any scope not assessed.

## Scenario coverage

This skill also answers 4 customer scenarios in the Network category (private endpoint and public exposure, public IP inventory, permissive NSG rules, DDoS coverage). Open references/scenarios.md when the ask matches one of them: it holds the sample prompt, the run mode, and whether the skill covers it with built in checks or a guided read only prompt.

## Expected output

- Primary: a self contained HTML exposure report, covering findings by severity and by exposure type, and the full table naming what is open and the recommended change per resource.
- Inline: critical exposures, resources with public access, and the top items to close first.
- Every finding names the resource, the exposure, a severity, and the recommended change. Nothing is changed; recommendations are for a human to apply.
