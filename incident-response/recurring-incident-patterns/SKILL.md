---
name: recurring-incident-patterns
description: Use when the user asks about recurring incidents, repeat offenders, chronic problems, "what keeps breaking", flaky resources, or wants to find the workloads that generate the most incidents over time. Aggregates fired alerts and resource health degradations by resource over a window, ranks the repeat offenders, and produces a self contained HTML patterns report.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# Recurring Incident Patterns

This skill finds the workloads that keep breaking. It aggregates fired alerts and resource health degradations by resource over a window (thirty days by default), ranks the repeat offenders, groups them by resource type, and produces a single self contained HTML report. It answers a question the portal does not: not what is broken right now, but what has been unreliable over time and is worth a durable investment. It runs on demand or as a scheduled sweep.

## When to use this skill

Use this skill when the user asks to:

- Find recurring incidents, repeat offenders, or chronic problems.
- See which workloads or resource types generate the most incidents over time.
- Decide where reliability investment will pay back the most.

## Operating principles

- Read only. This skill reads alert history and resource health events. It changes nothing.
- Default Reader scope. It reads across the subscriptions this agent can read. If a read is denied, it records the scope as not assessed and continues. See references/permissions-and-scope.md.
- Evidence first. Every repeat offender carries its incident count and the signals behind it (how many alerts and how many health degradations), so the ranking is explainable.

## Workflow

The scan tool (tools/pattern_scan.py) and the shared report renderer (tools/report_render.py) are bundled with this skill. Run them with RunInTerminal using the Python in the agent runtime. Both authenticate with the agent managed identity.

### Phase 1: Aggregate the history

1. Run python tools/pattern_scan.py [days] with RunInTerminal (thirty days by default). It reads the fired alerts and the resource health degradations across accessible subscriptions, aggregates them by resource, and ranks the resources by total incident count, following references/checks-catalog.md.
2. A resource at or above the repeat threshold (three incidents by default) is a repeat offender. The report groups offenders by resource type so the pattern is visible.

### Phase 2: Produce the report

1. Pipe the scan into the renderer: python tools/pattern_scan.py | python tools/report_render.py with RunInTerminal. It writes the self contained HTML report and returns the path. Store it with SaveFileToBlob for a link.
2. Present the report, then a short inline summary: the top repeat offenders with their counts, the resource types that break most, and where a reliability investment would pay back.

## Expected output

- Primary: a self contained HTML patterns report, covering incidents by resource type, the top repeat offenders, and a table of every offender with its incident count and the signals behind it.
- Inline: the top repeat offenders, the worst resource types, and the suggested focus.
- Every offender carries its incident count and the signals (alerts and health degradations) behind it. The report points at where to invest; a human decides and acts.
