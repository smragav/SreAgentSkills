---
name: deprecation-retirement-tracker
description: Use when the user asks about deprecations, retirements, end of life runtimes or platforms, unsupported versions, retiring SKUs, old Kubernetes or AKS versions, legacy or classic resources, or upcoming forced migrations. Scans the resources the agent can read for end of life runtimes, retired service tiers, classic resources, and old platform versions, and produces a self contained HTML deprecation report.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# Deprecation and Retirement Tracker

This skill finds where the estate this agent can read is running on something Azure is retiring or has ended support for. It scans for end of life language runtimes, retired service tiers, classic resources, old Kubernetes versions, and end of life operating system images, and produces a single self contained HTML report. It turns surprise forced migrations and broken deployments into a planned backlog with lead time. It runs on demand or as a scheduled sweep.

## When to use this skill

Use this skill when the user asks to:

- Find deprecations, retirements, or end of life runtimes and platforms.
- Plan ahead of a forced migration or an unsupported version.
- Check for legacy or classic resources and retiring service tiers.

## Operating principles

- Read only. This skill reads resource configuration. It never migrates or upgrades anything; it reports what is retiring and the path off it.
- Default Reader scope. It reads inventory and versions across the subscriptions this agent can read. If a read is denied, it records the scope as not assessed and continues. See references/permissions-and-scope.md.
- Evidence first, and roadmap aware. Every finding names the resource, the deprecated element, and the recommended target. Retirement dates move, so corroborate the specifics against Azure Service Health planned retirements and the official roadmap before committing a date.

## Workflow

The scan tool (tools/deprecation_scan.py) and the shared report renderer (tools/report_render.py) are bundled with this skill. Run them with RunInTerminal using the Python in the agent runtime. Both authenticate with the agent managed identity.

### Phase 1: Scan for retiring elements

1. Run python tools/deprecation_scan.py with RunInTerminal. It queries Azure Resource Graph for the signals in references/checks-catalog.md (end of life App Service runtimes, retired database single servers, classic resources, old Kubernetes versions, end of life operating system images), assigns a category and severity, and prints a report_data object as JSON.
2. Corroborate the highest severity items against Azure Service Health planned retirements for the affected subscriptions, so the report reflects the current dates.

### Phase 2: Produce the report

1. Pipe the scan into the renderer: python tools/deprecation_scan.py | python tools/report_render.py with RunInTerminal. It writes the self contained HTML report and returns the path. Store it with SaveFileToBlob for a link.
2. Present the report, then a short inline summary: retired or end of life items, items by category, the highest severity three with their target, and any scope not assessed.

## Expected output

- Primary: a self contained HTML deprecation report, covering items by severity and by category, and the full table naming the deprecated element and the recommended target per resource.
- Inline: retired and end of life items, items by category, and the top items to plan first.
- Every finding names the resource, the deprecated element, and the recommended target. Nothing is migrated; recommendations are a backlog for a human to plan.
