---
name: change-audit
description: Use when the user asks what changed, a change audit, change review, "what changed and did it break something", recent deployments and their effect, or wants to correlate changes with incidents. Reads the Azure Activity Log across the subscriptions the agent can read, correlates each change with any resource health degradation that followed it, and produces a self contained HTML change audit report.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# Change Audit

This skill answers a question no portal blade does: what changed, and did it hurt. It reads the Azure Activity Log across the subscriptions this agent can read, lines up each change against the resource health degradations that followed it, and flags the changes that preceded a problem, along with deletes and failed changes worth a second look. The primary output is a single self contained HTML report. It runs on demand or as a scheduled sweep, and it makes incident triage faster because the suspect changes are already surfaced.

## When to use this skill

Use this skill when the user asks to:

- See what changed recently across the estate, and who changed it.
- Correlate changes with incidents or health degradations.
- Review deletes and failed changes after a rocky period.

## Operating principles

- Read only. This skill reads the Activity Log. It never rolls back or re applies a change; it surfaces the changes and their apparent effect.
- Default Reader scope. It reads the Activity Log across the subscriptions this agent can read. If a read is denied, it records the scope as not assessed and continues. See references/permissions-and-scope.md.
- Correlation is not proof. A change that preceded a degradation is a lead, not a verdict. Every correlation carries its timing evidence so a human can judge it.

## Workflow

The scan tool (tools/change_scan.py) and the shared report renderer (tools/report_render.py) are bundled with this skill. Run them with RunInTerminal using the Python in the agent runtime. Both authenticate with the agent managed identity.

### Phase 1: Read and correlate

1. Run python tools/change_scan.py [days] with RunInTerminal (seven days by default). It reads the Activity Log across accessible subscriptions, separates administrative changes from resource health events, and correlates each health degradation with the changes on the same resource or resource group in the preceding window, following references/checks-catalog.md.
2. It also surfaces deletes and failed changes that were not linked to a degradation, since those are worth a look on their own.

### Phase 2: Produce the report

1. Pipe the scan into the renderer: python tools/change_scan.py | python tools/report_render.py with RunInTerminal. It writes the self contained HTML report and returns the path. Store it with SaveFileToBlob for a link.
2. Present the report, then a short inline summary: changes linked to a degradation, deletes, failed changes, the busiest changers, and any scope not assessed.

## Expected output

- Primary: a self contained HTML change audit report, covering findings by severity and by subscription, and a table of the suspect changes with the degradation each one preceded, plus the deletes and failed changes.
- Inline: changes linked to a degradation, deletes, and failed changes, with the timing evidence.
- Every correlation carries the change, the caller, the degradation it preceded, and the time gap. Nothing is rolled back; the report is for a human to judge and act on.
