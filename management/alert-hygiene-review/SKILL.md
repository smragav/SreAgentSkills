---
name: alert-hygiene-review
description: Use when the user asks about alert noise, alert fatigue, flapping alerts, too many alerts, noisy alert rules, alerts nobody acts on, alert tuning, or severity misconfiguration. Aggregates fired alerts over a window by rule, finds the noisy rules, the ones that auto resolve without anyone acting, and the disabled rules, and produces a self contained HTML alert hygiene report.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# Alert Hygiene Review

This skill reduces alert fatigue for the subscriptions this agent can read. It aggregates fired alerts over a window by rule, finds the rules that fire too often, the rules whose alerts auto resolve without anyone acting, the high severity rules that cry wolf, and the alert rules that are disabled, and produces a single self contained HTML report. Cutting alert noise is one of the highest value things an on call team can do, because a quiet, trustworthy pager is one people act on. It runs on demand or as a scheduled sweep.

## When to use this skill

Use this skill when the user asks to:

- Reduce alert noise, alert fatigue, or pager toil.
- Find noisy, flapping, or never actioned alert rules.
- Tune alert severities or find disabled alert rules.

## Operating principles

- Read only. This skill reads fired alerts and alert rule configuration. It never changes, disables, or creates an alert rule; it recommends the tuning.
- Default Reader scope. It reads the alert history and rules for the subscriptions this agent can read. If a read is denied, it records the scope as not assessed and continues. See references/permissions-and-scope.md.
- Evidence first. Every finding names the rule, its fire count over the window, the share that auto resolved without action, and the recommended tuning.

## Workflow

The scan tool (tools/alert_hygiene.py) and the shared report renderer (tools/report_render.py) are bundled with this skill. Run them with RunInTerminal using the Python in the agent runtime. Both authenticate with the agent managed identity.

### Phase 1: Aggregate the alert history

1. Run python tools/alert_hygiene.py with RunInTerminal. It reads fired alerts over the window (seven days by default) from Azure Monitor, groups them by rule, computes the fire count, the auto resolved share, and the unacknowledged share per rule, reads the disabled rules with Azure Resource Graph, and prints a report_data object as JSON. Pass a window of 1, 7, or 30 days as an argument.
2. It classifies each rule against the thresholds in references/checks-catalog.md: noisy, cries wolf, alerts not acknowledged, or disabled.

### Phase 2: Produce the report

1. Pipe the scan into the renderer: python tools/alert_hygiene.py | python tools/report_render.py with RunInTerminal. It writes the self contained HTML report and returns the path. Store it with SaveFileToBlob for a link.
2. Present the report, then a short inline summary: alerts fired in the window, the noisiest rules, rules that cry wolf, disabled rules, and the top tuning actions.

## Scenario coverage

This skill also answers 3 customer scenarios in the Management category (alert rule audit, alert fatigue, fired alerts summary). Open references/scenarios.md when the ask matches one of them: it holds the sample prompt, the run mode, and whether the skill covers it with built in checks or a guided read only prompt.

## Expected output

- Primary: a self contained HTML alert hygiene report, covering alerts by severity, the noisiest rules, and the full table with the fire count, auto resolved share, and recommended tuning per rule.
- Inline: alerts fired, the noisiest rules, cry wolf rules, and disabled rules.
- Every finding names the rule, its fire count and auto resolved share over the window, and the recommended tuning. Nothing is changed; recommendations are for a human to apply.
