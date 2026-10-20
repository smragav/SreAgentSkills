# Scenario coverage for sql-cmdb-inventory

Category: Resource Organization. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| Resources created yesterday | Added | Scheduled | Daily | Medium |
| Resource age tracking | Added | Scheduled | Weekly | Medium |
| Extension health across VMs | Added | Scheduled | Daily | Medium |

## Resources created yesterday

Status: Added. Source category: Resource Organization.

Detects new resources provisioned in the last 24 hours, catching shadow IT and unauthorized deployments early.

Sample prompt:

> List all resources created in the last 24 hours across all subscriptions. Show: resource name, type, resource group, subscription, who created it (from Activity Log), and whether it was created via ARM template/pipeline or manual portal action. Flag resources not matching naming conventions.

Mode: Scheduled. Frequency: Daily. Time saved: Medium.

## Resource age tracking

Status: Added. Source category: Resource Organization.

Identifies long-running resources that may be forgotten, orphaned, or candidates for modernization.

Sample prompt:

> Find all resources older than {X} months (default 12) that have had no write operations in their Activity Log in the last 90 days. Show resource name, type, creation date, last activity date, and monthly cost. Flag as potential candidates for decommission review.

Mode: Scheduled. Frequency: Weekly. Time saved: Medium.

## Extension health across VMs

Status: Added. Source category: Resource Organization.

Monitors VM extension status to catch failed deployments or stuck provisioning that blocks updates and monitoring.

Sample prompt:

> Check all VM extensions across subscriptions. Identify: (1) extensions in 'Failed' provisioning state, (2) extensions in 'Transitioning' state for > 1 hour, (3) extensions with handler status errors, (4) VMs with conflicting extensions. Show VM name, extension, status, and error message.

Mode: Scheduled. Frequency: Daily. Time saved: Medium.
