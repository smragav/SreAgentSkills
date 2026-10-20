# Scenario coverage for alert-hygiene-review

Category: Management. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| Alert rules best-practice audit | Partial | Scheduled | Monthly | Medium |
| Alert fatigue analysis | Covered | Scheduled | Weekly | High |
| Fired alerts summary (last 24h) | Added | Scheduled | Daily morning | Low |

## Alert rules best-practice audit

Status: Partial. Source category: Management.

Evaluates existing alert rules against SRE best practices to find gaps, misconfigurations, or noise generators.

Sample prompt:

> Audit all alert rules across subscriptions. Identify: (1) rules that fired > 20 times in 7 days (noisy), (2) rules in 'Disabled' state, (3) resources without any alert rule, (4) rules without an action group, (5) rules using static thresholds where dynamic would be better.

Mode: Scheduled. Frequency: Monthly. Time saved: Medium.

## Alert fatigue analysis

Status: Covered. Source category: Management.

Identifies noisy, low-value alerts that contribute to alert fatigue and reduce team responsiveness.

Sample prompt:

> Analyze all alert rules that fired in the last 30 days. Identify: (1) alerts that fired > 50 times, (2) alerts that auto-resolved within 5 minutes > 80% of the time, (3) alerts where no action was taken (no comments, no state change). Recommend suppression, threshold adjustment, or consolidation.

Mode: Scheduled. Frequency: Weekly. Time saved: High.

## Fired alerts summary (last 24h)

Status: Added. Source category: Management.

Provides a daily operational summary of all alerts that fired, grouped by severity and resolution status.

Sample prompt:

> List all alerts that fired in the last 24 hours across all subscriptions. Group by severity (Sev0-Sev4), show count per severity, average time to resolution, and list unresolved alerts with resource name, alert rule, and time fired.

Mode: Scheduled. Frequency: Daily morning. Time saved: Low.
