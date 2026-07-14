---
name: pre-change-readiness
description: Use before a launch, a migration, a deployment, or a big change, or when the user asks for a readiness check, a go or no-go, or "are we ready to ship". Runs reliability, internet exposure, and capacity checks scoped to one target subscription or resource group and returns a go, caution, or no-go verdict per category, as a self contained HTML readiness report.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# Pre-Change Readiness

This skill gives a single go or no-go readiness view for a specific target before a launch, a migration, or a large change. It runs reliability, internet exposure, and capacity checks scoped to one subscription or resource group, returns a verdict per category and an overall verdict, and produces one self contained HTML report. It is a workflow no portal blade offers: it joins the checks that matter right before a change into one answer for the scope you are about to touch. It runs on demand.

## When to use this skill

Use this skill when the user asks to:

- Check readiness before a launch, a migration, or a major deployment.
- Get a go, caution, or no-go for a specific scope.
- Confirm reliability, exposure, and capacity are in order before shipping.

## Operating principles

- Read only. This skill reads configuration and usage. It never changes anything; it reports whether the scope is ready.
- Scoped and explicit. It checks exactly the subscription (and optional resource group) you pass, so the verdict is about the thing you are changing, not the whole estate.
- Evidence first. Every finding names the resource, the category, the issue, a severity, and the recommended change. The verdict follows from the severities, not from a feeling.

## Workflow

The scan tool (tools/readiness_check.py) and the shared report renderer (tools/report_render.py) are bundled with this skill. Run them with RunInTerminal using the Python in the agent runtime. Both authenticate with the agent managed identity.

### Phase 1: Check the target

1. Run python tools/readiness_check.py "<subscription id>" [resource group] with RunInTerminal. It runs the reliability, exposure, and capacity checks in references/checks-catalog.md scoped to that target, assigns a severity to each finding, and prints a report_data object as JSON.
2. It computes a verdict per category and overall: no-go when any Critical or High finding is present, caution when only Medium findings are present, go when the category is clean.

### Phase 2: Produce the report

1. Pipe the scan into the renderer: python tools/readiness_check.py "<subscription id>" [resource group] | python tools/report_render.py with RunInTerminal. It writes the self contained HTML report and returns the path. Store it with SaveFileToBlob for a link.
2. Present the report, then a short inline summary: the overall verdict, the verdict per category, and the blocking findings to clear before shipping.

## Expected output

- Primary: a self contained HTML readiness report, with the overall and per category verdicts as cards, findings by category and severity, and the full table of what to clear.
- Inline: the overall go, caution, or no-go, the per category verdicts, and the blocking findings.
- Every finding names the resource, category, issue, severity, and recommended change. The skill reports readiness; it changes nothing.
