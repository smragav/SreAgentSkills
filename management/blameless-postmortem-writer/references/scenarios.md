# Scenario coverage for blameless-postmortem-writer

Category: Management. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| Post-incident review automation | Covered | Event-driven | On incident closure | High |

## Post-incident review automation

Status: Covered. Source category: Management.

Auto-generates a post-incident review document with timeline, changes, metrics, and impact data.

Sample prompt:

> Incident on resource '{resource_id}' from {start_time} to {end_time} is now resolved. Generate a post-incident review: (1) timeline of events (first alert → detection → response → resolution), (2) changes made during and before incident, (3) metrics during impact window, (4) user/customer impact estimate, (5) action items to prevent recurrence.

Mode: Event-driven. Frequency: On incident closure. Time saved: High.
