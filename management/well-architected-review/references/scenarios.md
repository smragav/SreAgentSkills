# Scenario coverage for well-architected-review

Category: Management. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| Executive operational report generation (PDF) | Partial | Scheduled | Monthly | High |

## Executive operational report generation (PDF)

Status: Partial. Source category: Management.

Generates a comprehensive, executive-ready operational report consolidating key metrics across cost, security, compliance, and availability into a single formatted document (PDF or HTML). Combines data from multiple sources, Cost Management, Defender for Cloud, Resource Health, alert history, and policy compliance, into a structured narrative with charts, tables, and recommendations that can be shared with leadership without further editing.

Sample prompt:

> Generate a monthly executive operational report for management group 'Production' covering the last 30 days. Include sections for: (1) Cost summary, total spend, MoM change, top 5 cost drivers, anomalies detected, (2) Security posture, Defender secure score trend, new high-severity findings, (3) Availability, resource health summary, SLA breaches, top 5 incidents by duration, (4) Compliance, policy compliance %, top non-compliant policies, (5) Operational hygiene, orphaned resources count and cost, stale RBAC assignments found, alert noise ratio. Format as a structured PDF-ready report with an executive summary, key metrics dashboard table, and per-section details with recommendations.

Mode: Scheduled. Frequency: Monthly. Time saved: High.
