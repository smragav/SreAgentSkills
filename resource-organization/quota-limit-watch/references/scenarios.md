# Scenario coverage for quota-limit-watch

Category: Resource Organization. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| Subscription limits approaching | Covered | Scheduled | Weekly | High |

## Subscription limits approaching

Status: Covered. Source category: Resource Organization.

Monitors Azure subscription-level limits (resource counts, quotas) to prevent deployment failures from hitting limits.

Sample prompt:

> Check all subscriptions for resource quota usage. Show: (1) vCPU usage vs limit per family per region, (2) public IP count vs limit, (3) VNet count vs limit, (4) storage account count vs limit. Alert on any quota at > 80% utilization.

Mode: Scheduled. Frequency: Weekly. Time saved: High.
