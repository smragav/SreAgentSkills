---
name: reliability-posture-review
description: Use when the user asks for a reliability review, resilience assessment, high availability check, single points of failure, a Well-Architected reliability review, or "will we survive a zone or region outage". Scans the resources the agent can read for missing availability zones, single instance workloads, retiring Basic tiers, and single region data services, scores each finding by severity, and produces a self contained HTML resilience scorecard.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# Reliability Posture Review

This skill reviews the resilience posture of the Azure resources this agent can read. It finds single points of failure and redundancy gaps (no availability zones, single instance compute, retiring Basic tiers, single region data services), scores each finding by severity, and produces a single self contained HTML scorecard as the primary output. It is the Well-Architected reliability pillar counterpart to the cost optimizer, and it runs on demand or as a scheduled sweep.

## When to use this skill

Use this skill when the user asks to:

- Review reliability, resilience, or high availability posture.
- Find single points of failure or redundancy gaps before an outage.
- Run a Well-Architected reliability assessment across a subscription or resource group.

## Operating principles

- Read only. This skill never changes a resource. It proposes recommendations with the exact configuration change, but a human reviews and applies them.
- Default Reader scope. It analyzes the subscriptions and resource groups this agent can already read. If a read returns access denied, it may ask the user to grant temporary access, but it never assigns roles itself. If the user declines, it records the scope as not assessed and continues. See references/permissions-and-scope.md.
- Evidence first. Every finding carries the resource id, the reliability signal that fired, a severity, and the recommended change. Severity reflects blast radius and likelihood, not effort.

## Workflow

The scan tool (tools/reliability_scan.py) and the shared report renderer (tools/report_render.py) are bundled with this skill. Run them with the RunInTerminal tool using the Python in the agent runtime, which already has azure-identity and requests. The renderer uses only the standard library. Both authenticate with the agent managed identity. Follow three phases.

### Phase 1: Scan for reliability signals

1. Run python tools/reliability_scan.py with RunInTerminal. It queries Azure Resource Graph across every accessible subscription for the reliability signals in references/checks-catalog.md, assigns a severity to each, and prints a ready to render report_data object as JSON on standard output.
2. For any signal the tool could not evaluate (for example a subscription that denied Resource Graph), it records a method note rather than failing the run.
3. If the user wants deeper checks that Resource Graph cannot answer alone, backup coverage and idle detection have their own skills; point to them rather than duplicating the work here.

### Phase 2: Confirm severity and scope

Review the findings the tool returned against references/scoring-method.md. Severity bands are Critical, High, Medium, and Low. Promote or lower a finding only with evidence, for example lowering a single instance virtual machine to Low when its name marks it as a lab or sandbox.

### Phase 3: Produce the scorecard

1. Pipe the scan output straight into the renderer: python tools/reliability_scan.py | python tools/report_render.py with RunInTerminal. The renderer writes a self contained HTML scorecard and returns the path. If the user wants a shareable link, store it with the SaveFileToBlob tool.
2. Present the report, then a short inline summary: resources with findings, findings by severity, the top subscriptions by finding count, the three highest severity items, and any scope not assessed because of insufficient access.

## Optional follow up

Only if the user asks, file tracking issues from the highest severity findings. This is off by default and read only until the user requests it.

## Scenario coverage

This skill also answers 3 customer scenarios in the Management category (RTO and RPO gaps, backup policy compliance, SKU reliability). Open references/scenarios.md when the ask matches one of them: it holds the sample prompt, the run mode, and whether the skill covers it with built in checks or a guided read only prompt.

## Expected output

- Primary: a single self contained HTML resilience scorecard delivered as a file link, covering findings by severity, findings by subscription, and the full finding table with the recommended change per resource.
- Inline: a short summary with resources affected, findings by severity, and the top recommendations.
- Every finding includes the resource id, the reliability signal, a severity, and the exact recommended configuration change. Nothing is changed; recommendations are proposals for a human to apply.
