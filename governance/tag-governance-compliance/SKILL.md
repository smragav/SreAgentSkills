---
name: tag-governance-compliance
description: Use when the user asks about tagging compliance, tag governance, resources missing tags, untagged resources, ownership tags, missing owner or environment or cost center tags, or chargeback readiness. Checks the resources the agent can read against a required tag standard, flags what is missing, and produces a self contained HTML tag compliance report.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# Tag Governance Compliance

This skill measures how well the resources this agent can read meet a required tag standard. It checks each resource for the required tags (owner, environment, and cost center by default), flags what is missing, and produces a single self contained HTML report. Good tagging is what makes accountability, environment filtering, and cost chargeback work, so this both improves governance and feeds cleaner cost attribution. It runs on demand or as a scheduled sweep.

## When to use this skill

Use this skill when the user asks to:

- Check tagging compliance or find untagged resources.
- Confirm ownership tags are in place before an audit or a chargeback cycle.
- Measure how close the estate is to a required tag standard.

## Operating principles

- Read only. This skill reads tags. It never sets, changes, or removes a tag; it reports what is missing and the standard to meet.
- Default Reader scope. It reads resource inventory and tags across the subscriptions this agent can read. If a read is denied, it records the scope as not assessed and continues. See references/permissions-and-scope.md.
- Evidence first, and tolerant of key style. Tag key matching is case insensitive and ignores separators, so cost-center, CostCenter, and cost_center all satisfy the same requirement. Every finding names the resource and the exact tags it is missing.

## Workflow

The scan tool (tools/tag_compliance.py) and the shared report renderer (tools/report_render.py) are bundled with this skill. Run them with RunInTerminal using the Python in the agent runtime. Both authenticate with the agent managed identity.

### Phase 1: Check against the standard

1. Run python tools/tag_compliance.py [required tags] with RunInTerminal, where required tags is an optional comma separated list. It defaults to owner,environment,cost-center. It enumerates resources with Azure Resource Graph, checks each against the required tags with tolerant key matching, and prints a report_data object as JSON.
2. It marks a resource compliant when every required tag is present, and records the missing tags otherwise, with a severity that treats a missing owner as the most serious, following references/checks-catalog.md.

### Phase 2: Produce the report

1. Pipe the scan into the renderer: python tools/tag_compliance.py | python tools/report_render.py with RunInTerminal. It writes the self contained HTML report and returns the path. Store it with SaveFileToBlob for a link.
2. Present the report, then a short inline summary: compliance percent, resources missing an owner tag, the most common missing tag, and the top subscriptions by gap.

## Scenario coverage

This skill also answers 8 customer scenarios in the Governance category (naming and tagging, policy authoring and lookup, compliance state, effective policies, exemptions, remediation, assignment assessment). Open references/scenarios.md when the ask matches one of them: it holds the sample prompt, the run mode, and whether the skill covers it with built in checks or a guided read only prompt.

## Expected output

- Primary: a self contained HTML tag compliance report, covering compliance percent, missing tags by type, non compliance by subscription, and the full table naming the missing tags per resource.
- Inline: compliance percent, resources with no owner, the most common missing tag, and the top gaps.
- Every finding names the resource and the exact missing tags, with the recommended values to set. Nothing is tagged; recommendations are for a human to apply, ideally through Azure Policy for durable enforcement.
