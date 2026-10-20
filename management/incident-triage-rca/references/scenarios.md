# Scenario coverage for incident-triage-rca

Category: Management. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| Service Health incidents & resource impact | Partial | Event-driven | On new incident | High |
| Planned maintenance awareness | Added | Scheduled | Daily | Low |
| Resource health status summary | Partial | Scheduled | Every 1h | Medium |
| Support ticket creation (pre-populated) | Added | On-demand | After auto-resolve fails | Medium |
| Logic Apps code/definition inspection | Added | On-demand | During debugging | Medium |

## Service Health incidents & resource impact

Status: Partial. Source category: Management.

Detects Azure platform incidents and maps them to specific customer resources to quantify blast radius during outages.

Sample prompt:

> Check Azure Service Health for any active incidents affecting resources in my subscriptions. Show incident title, affected services, impacted regions, status, and list my specific resources in those regions. For each impacted resource, show current health status and dependent workloads affected. Suggest mitigation actions if available.

Mode: Event-driven. Frequency: On new incident. Time saved: High.

## Planned maintenance awareness

Status: Added. Source category: Management.

Proactively surfaces upcoming Azure maintenance events to plan workload failovers.

Sample prompt:

> List all planned maintenance events from Azure Service Health for the next 7 days affecting my subscriptions. Show event name, affected service, scheduled window, impacted region, and my resources in that region.

Mode: Scheduled. Frequency: Daily. Time saved: Low.

## Resource health status summary

Status: Partial. Source category: Management.

Provides a real-time view of all resource health states to quickly identify degraded infrastructure.

Sample prompt:

> Query Azure Resource Health for all resources in subscriptions. Show summary: count by health status (Available, Degraded, Unavailable, Unknown). List all resources currently in 'Degraded' or 'Unavailable' state with reason and since-when timestamp.

Mode: Scheduled. Frequency: Every 1h. Time saved: Medium.

## Support ticket creation (pre-populated)

Status: Added. Source category: Management.

Generates a pre-filled support ticket with all relevant diagnostic context collected by SRE Agent to accelerate resolution.

Sample prompt:

> Prepare a support ticket for resource '{resource_id}' issue: '{issue_description}'. Collect and include: (1) resource config and SKU, (2) relevant metrics last 4h, (3) related errors in logs, (4) recent changes from Activity Log, (5) Resource Health status. Format as a support request with severity, category, and collected evidence.

Mode: On-demand. Frequency: After auto-resolve fails. Time saved: Medium.

## Logic Apps code/definition inspection

Status: Added. Source category: Management.

Examines the Logic App workflow definition to identify structural issues, deprecated connectors, or error-prone patterns.

Sample prompt:

> Retrieve the workflow definition for Logic App '{logic_app_name}'. Analyze for: (1) actions without error handling (no 'runAfter' failure paths), (2) deprecated connector versions, (3) hardcoded values that should be parameters, (4) loops without concurrency limits, (5) missing retry policies on HTTP actions.

Mode: On-demand. Frequency: During debugging. Time saved: Medium.
