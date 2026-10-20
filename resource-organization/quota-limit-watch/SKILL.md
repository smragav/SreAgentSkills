---
name: quota-limit-watch
description: Use when the user asks about quotas, service limits, capacity headroom, vCPU or core limits, public IP or network limits, "will a deployment or scale out fail", or approaching Azure limits. Reads Azure usage and quota counters for compute, network, and storage across the regions the agent's resources sit in, flags any counter close to its limit, and produces a self contained HTML quota headroom report.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# Quota and Limit Watch

This skill checks how close the subscriptions this agent can read are to their Azure quotas and service limits. It reads compute, network, and storage usage counters in every region where the agent has resources, flags any counter near its limit, and produces a single self contained HTML headroom report. Catching a quota before it is hit prevents the scale out and deployment failures that show up during traffic spikes. It runs on demand or as a scheduled sweep.

## When to use this skill

Use this skill when the user asks to:

- Check quota or service limit headroom before a launch, a migration, or a scale event.
- Understand why a deployment or a scale out failed, or might fail, with a quota error.
- Find regions and families that are close to their limits.

## Operating principles

- Read only. This skill reads usage and quota counters. It never requests or changes a quota; it recommends where to request an increase.
- Default Reader scope. It reads the usage endpoints for the subscriptions this agent can read, in the regions those subscriptions actually use. If a read is denied, it records the scope as not assessed and continues. See references/permissions-and-scope.md.
- Evidence first. Every finding carries the subscription, the region, the quota name, the used and limit values, the utilization percent, and a severity from that utilization.

## Workflow

The scan tool (tools/quota_scan.py) and the shared report renderer (tools/report_render.py) are bundled with this skill. Run them with RunInTerminal using the Python in the agent runtime. Both authenticate with the agent managed identity.

### Phase 1: Read usage counters

1. Run python tools/quota_scan.py with RunInTerminal. It finds the regions each subscription uses with Azure Resource Graph, reads the compute, network, and storage usage counters in those regions, and prints a report_data object as JSON.
2. It flags any counter at or above the threshold (80 percent by default) and assigns a severity from the utilization, following references/checks-catalog.md. Pass a lower threshold as an argument for an earlier warning.

### Phase 2: Produce the report

1. Pipe the scan into the renderer: python tools/quota_scan.py | python tools/report_render.py with RunInTerminal. It writes the self contained HTML report and returns the path. Store it with SaveFileToBlob for a link.
2. Present the report, then a short inline summary: counters at or above the threshold, the Critical count (95 percent or higher), the tightest three counters, and any scope not assessed.

## Scenario coverage

This skill also answers 1 customer scenario in the Resource Organization category (subscription limits approaching). Open references/scenarios.md when the ask matches it: it holds the sample prompt, the run mode, and whether the skill covers it with built in checks or a guided read only prompt.

## Expected output

- Primary: a self contained HTML headroom report, covering counters near their limit by severity, the tightest counters, and the full table with used, limit, and utilization per counter.
- Inline: counters near the limit, the Critical count, and the tightest counters with the region and the quota name.
- Every finding carries the subscription, region, quota name, used and limit values, utilization percent, and a severity. The skill requests no increase; it points to where an increase is needed.
