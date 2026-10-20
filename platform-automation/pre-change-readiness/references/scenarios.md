# Scenario coverage for pre-change-readiness

Category: Platform Automation. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| Failed deployments in last 24h | Added | Scheduled | Daily | High |
| Export existing resources to ARM/Bicep | Added | On-demand | During IaC adoption | High |

## Failed deployments in last 24h

Status: Added. Source category: Platform Automation And Devops.

Surfaces ARM deployment failures with error details to catch broken CI/CD pipelines or misconfigurations early.

Sample prompt:

> List all ARM deployments in 'Failed' state across all subscriptions in the last 24 hours. For each, show: resource group, deployment name, timestamp, error code, error message, and correlation ID. Group by error code to identify patterns.

Mode: Scheduled. Frequency: Daily. Time saved: High.

## Export existing resources to ARM/Bicep

Status: Added. Source category: Platform Automation And Devops.

Exports running infrastructure to IaC templates for adopting infrastructure-as-code on existing environments.

Sample prompt:

> Export resource group '{rg_name}' to {Bicep/ARM}. Clean up the export: (1) remove read-only and auto-generated properties, (2) parameterize names, SKUs, and locations, (3) add missing dependencies between resources, (4) organize into modules by resource type. Generate the parameter file with current values.

Mode: On-demand. Frequency: During IaC adoption. Time saved: High.
