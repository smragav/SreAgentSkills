---
name: observability-coverage-gap
description: Use when the user asks about monitoring coverage, observability gaps, "where are we blind", missing diagnostic settings, resources with no alerts, no action groups, or no Log Analytics. Cross references the resources the agent can read against their diagnostic settings, metric alerts, action groups, and Log Analytics workspaces, flags the wiring that is missing, and produces a self contained HTML coverage gap report.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# Observability Coverage Gap

This skill finds where monitoring is missing across the resources this agent can read. It cross references important resources against their diagnostic settings, metric alerts, action groups, and Log Analytics workspaces, flags the wiring that is not there, and produces a single self contained HTML report. Closing these gaps is what stops a small incident becoming a long one, because you cannot respond to what you cannot see. It runs on demand or as a scheduled sweep.

## When to use this skill

Use this skill when the user asks to:

- Find monitoring or observability gaps, or answer "where are we blind".
- Check which resources have no diagnostic settings, no alerts, or nowhere to send them.
- Prepare an environment for on call by confirming the telemetry and alerting wiring is in place.

## Operating principles

- Read only. This skill reads monitoring configuration. It never creates a diagnostic setting, an alert, or an action group; it reports what is missing and the wiring to add.
- Default Reader scope. It reads resource inventory and monitoring configuration across the subscriptions this agent can read. If a read is denied, it records the scope as not assessed and continues. See references/permissions-and-scope.md.
- Evidence first. Every finding names the resource, the specific wiring that is missing (diagnostic settings, a metric alert, an action group, or a workspace), and the recommended fix.

## Workflow

The scan tool (tools/observability_gap.py) and the shared report renderer (tools/report_render.py) are bundled with this skill. Run them with RunInTerminal using the Python in the agent runtime. Both authenticate with the agent managed identity.

### Phase 1: Map the wiring

1. Run python tools/observability_gap.py with RunInTerminal. It enumerates the important resource types with Azure Resource Graph, builds the set of resources already covered by a metric alert, counts action groups and Log Analytics workspaces per subscription, checks diagnostic settings where Resource Graph can answer, and prints a report_data object as JSON.
2. It records a gap per resource for each missing piece of wiring, following references/checks-catalog.md, and a subscription level gap when there is no action group to notify or no workspace to land logs.

### Phase 2: Verify anything Resource Graph could not answer

Where the tool notes that diagnostic settings could not be read in bulk, spot check a sample with the per resource command in references/checks-catalog.md, and treat a denied read as not assessed.

### Phase 3: Produce the report

1. Pipe the scan into the renderer: python tools/observability_gap.py | python tools/report_render.py with RunInTerminal. It writes the self contained HTML report and returns the path. Store it with SaveFileToBlob for a link.
2. Present the report, then a short inline summary: resources with gaps, resources with no diagnostic settings, subscriptions with no action group, and the top gaps by subscription.

## Expected output

- Primary: a self contained HTML coverage gap report, covering gaps by type, gaps by subscription, and the full table naming the missing wiring per resource.
- Inline: resources with gaps, the blind resources (no diagnostic settings), subscriptions with no action group, and the top gaps.
- Every finding names the resource, the missing wiring, and the recommended fix. Nothing is created; recommendations are for a human to apply.
