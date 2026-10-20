---
name: incident-triage-rca
description: Use when the user reports an incident, an outage, an alert that fired, a resource that is down or degraded, or asks for triage, root cause analysis, or "what changed". Gathers Resource Health, recent Activity Log changes, and the neighbouring resources for the affected resource, builds a timeline, and helps reason to a probable cause and safe mitigations, then produces a self contained HTML incident report.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# Incident Triage and Root Cause Assist

This skill speeds up triage for a single affected resource or a fired alert. It gathers the resource's current health, the recent changes from the Activity Log, and the neighbouring resources, lays them on a timeline, and helps reason to a probable cause and a set of safe mitigations. The primary output is a single self contained HTML incident report. It shrinks time to mitigate by putting the "what changed" evidence in one place. It runs on demand or as an automatic first pass when an alert fires.

## When to use this skill

Use this skill when the user:

- Reports an incident, an outage, or a degraded or unavailable resource.
- Shares an alert and asks what is wrong or what changed.
- Asks for triage or a root cause analysis on a specific resource.

## Operating principles

- Read only. This skill reads health, changes, metrics, and logs. It never restarts, scales, or changes a resource. It proposes mitigations with the exact command, and a human runs them.
- Default Reader scope. It reads within the agent's access. If a read is denied, it records the gap and reasons from what it can read. See references/permissions-and-scope.md.
- Evidence first, and honest about uncertainty. Every hypothesis is tied to timeline evidence and carries a confidence. The most recent change before the symptom is a lead, not a verdict.

## Workflow

The context tool (tools/gather_context.py) and the shared report renderer (tools/report_render.py) are bundled with this skill. Run them with RunInTerminal using the Python in the agent runtime. Both authenticate with the agent managed identity.

### Phase 1: Gather context for the affected resource

1. Identify the affected resource id from the user or the alert. Run python tools/gather_context.py "<resource id>" [hours] with RunInTerminal. It reads Resource Health (current and recent), the Activity Log changes over the window (24 hours by default), and the neighbouring resources in the same resource group, and prints an evidence object as JSON.
2. Pull the signals the evidence points to with RunAzCliReadCommands, following references/triage-method.md: the metrics around the symptom start, and a focused Log Analytics query for errors on the resource.

### Phase 2: Correlate and reason

Lay the changes and health transitions on one timeline. Line up the symptom start with the nearest preceding change (a deployment, a configuration edit, a scale action, a failed operation). Form a small set of ranked hypotheses, each tied to an event on the timeline, each with a confidence and a next check that would confirm or rule it out. Keep the honest note that correlation is not proof.

### Phase 3: Produce the incident report

1. Assemble the report_data described in references/report-mapping.md: the timeline as the findings table, the ranked mitigations as the action candidates (each with the exact command the human runs), and the probable cause as the subtitle and the lead method note. Pipe it into python tools/report_render.py with RunInTerminal, and store it with SaveFileToBlob for a link.
2. Present the report, then a short inline summary: the symptom and impact, the probable cause with its confidence, the timeline highlights, and the top two mitigations with their commands and the check to run first.

## Scenario coverage

This skill also answers 5 customer scenarios in the Management category (Service Health incidents, planned maintenance, resource health summary, support ticket drafting, Logic Apps inspection). Open references/scenarios.md when the ask matches one of them: it holds the sample prompt, the run mode, and whether the skill covers it with built in checks or a guided read only prompt.

## Expected output

- Primary: a self contained HTML incident report with the timeline, the ranked hypotheses, and the proposed mitigations with commands.
- Inline: the symptom, the probable cause and confidence, the key timeline events, and the first mitigation to try with the check to confirm it.
- Every hypothesis is tied to timeline evidence and carries a confidence. Every mitigation is a proposal with a command a human runs; the agent runs none of them.
