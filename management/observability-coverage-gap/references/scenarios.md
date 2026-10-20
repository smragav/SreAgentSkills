# Scenario coverage for observability-coverage-gap

Category: Management. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| Diagnostic settings coverage audit | Covered | Scheduled | Weekly | High |
| Data collection rules audit | Added | Scheduled | Weekly | Medium |
| Agent health monitoring | Added | Scheduled | Daily | Medium |
| KQL log queries (common patterns) | Added | On-demand | During troubleshooting | Medium |
| Resource metrics analysis | Added | On-demand | During incident | Medium |
| VM performance anomaly detection | Added | Hybrid | Every 15 min + alert | High |
| Operations dashboard generation | Added | On-demand | On workload onboarding | High |
| Workbook auto-generation | Added | On-demand | On workload onboarding | Medium |

## Diagnostic settings coverage audit

Status: Covered. Source category: Management.

Finds resources that lack diagnostic settings, leaving operational blind spots in monitoring.

Sample prompt:

> Query all resources across subscriptions that support diagnostic settings. Identify those with no diagnostic settings configured, or where settings don't include all available log categories. Group by resource type and show coverage percentage.

Mode: Scheduled. Frequency: Weekly. Time saved: High.

## Data collection rules audit

Status: Added. Source category: Management.

Validates that Data Collection Rules (DCRs) are correctly configured and associated with target resources.

Sample prompt:

> List all Data Collection Rules. For each, show: associated resources count, data sources configured, destinations, and transformation status. Flag DCRs with 0 associated resources, DCRs referencing deleted workspaces, or DCRs with no data flowing in the last 24h.

Mode: Scheduled. Frequency: Weekly. Time saved: Medium.

## Agent health monitoring

Status: Added. Source category: Management.

Monitors the health of monitoring agents (AMA) to ensure telemetry pipeline continuity.

Sample prompt:

> Check all VMs and Arc machines for monitoring agent health. Identify: (1) machines with no heartbeat in the last 15 minutes, (2) agents in 'Not Ready' or 'Error' state, (3) extension provisioning failures. Show machine name, last heartbeat, agent version, and status.

Mode: Scheduled. Frequency: Daily. Time saved: Medium.

## KQL log queries (common patterns)

Status: Added. Source category: Management.

Generates or executes KQL queries for common operational scenarios to speed up log investigations.

Sample prompt:

> Run the following investigation on Log Analytics workspace '{workspace}': show all errors (severity >= 3) in the last 2 hours, grouped by source resource, error code, and count. Include sample error messages for the top 5 patterns.

Mode: On-demand. Frequency: During troubleshooting. Time saved: Medium.

## Resource metrics analysis

Status: Added. Source category: Management.

Deep-dives into performance metrics for a specific resource during troubleshooting or capacity planning.

Sample prompt:

> Pull the key metrics for resource '{resource_id}' over the last 4 hours with 5-minute granularity. Include CPU, memory, disk IOPS, network in/out, and any resource-specific metrics. Highlight any values exceeding 80% of the resource limit.

Mode: On-demand. Frequency: During incident. Time saved: Medium.

## VM performance anomaly detection

Status: Added. Source category: Management.

Continuously baselines VM performance metrics and alerts when behavior deviates from historical normal.

Sample prompt:

> For all production VMs, compare current 15-minute CPU, memory, disk queue length, and network metrics against the 7-day baseline for the same time window. Flag any VM where current values exceed 2 standard deviations from baseline.

Mode: Hybrid. Frequency: Every 15 min + alert. Time saved: High.

## Operations dashboard generation

Status: Added. Source category: Management.

Auto-generates Azure Monitor dashboards for new workloads with standard SRE metrics panels.

Sample prompt:

> Generate an Azure Monitor dashboard JSON for resource group '{rg_name}'. Include panels for: VM CPU/memory/disk, App Service requests/errors/response time, SQL DTU/connections, and a service health tile. Use best-practice layout.

Mode: On-demand. Frequency: On workload onboarding. Time saved: High.

## Workbook auto-generation

Status: Added. Source category: Management.

Creates ready-to-use Azure Workbooks tailored to a specific workload's monitoring needs.

Sample prompt:

> Generate an Azure Workbook for workload in resource group '{rg_name}'. Auto-detect resource types and include relevant panels: (1) resource health overview, (2) key performance metrics per resource type, (3) error/exception trends, (4) cost trend, (5) recent changes. Export as ARM template for deployment.

Mode: On-demand. Frequency: On workload onboarding. Time saved: Medium.
