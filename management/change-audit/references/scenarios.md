# Scenario coverage for change-audit

Category: Management. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| Changes in last 24h for a resource | Covered | On-demand | During incident | Medium |
| Changes by non-service-principal users | Partial | Scheduled | Daily | High |
| All write operations across subscription (24h) | Added | Scheduled | Daily digest | Medium |
| Identify who added a firewall/NSG rule | Added | Event-driven | On NSG change alert | High |
| Rollback command generation for bad changes | Added | Event-driven | On failed change | High |

## Changes in last 24h for a resource

Status: Covered. Source category: Management.

Shows all configuration changes to a specific resource during incident investigation, helping correlate changes with symptoms.

Sample prompt:

> Show all changes detected by Change Analysis and Activity Log for resource '{resource_id}' in the last 24 hours. For each change, show timestamp, property changed, old value, new value, and who initiated it.

Mode: On-demand. Frequency: During incident. Time saved: Medium.

## Changes by non-service-principal users

Status: Partial. Source category: Management.

Identifies manual changes made by human operators that bypassed automation pipelines, a common source of drift and incidents.

Sample prompt:

> Query the Activity Log for the last 24 hours across all subscriptions. Filter for write/delete operations where the caller is NOT a service principal or managed identity. Group by caller, show operation count, resources affected, and timestamps.

Mode: Scheduled. Frequency: Daily. Time saved: High.

## All write operations across subscription (24h)

Status: Added. Source category: Management.

Provides a daily digest of all infrastructure changes for operational awareness and audit trail.

Sample prompt:

> Summarize all write and delete operations in subscription '{subscription_name}' in the last 24 hours. Group by resource type, show total operations count, and flag any failed operations. Exclude read-only and diagnostic operations.

Mode: Scheduled. Frequency: Daily digest. Time saved: Medium.

## Identify who added a firewall/NSG rule

Status: Added. Source category: Management.

Traces network security rule changes to the specific user and timestamp for security investigation.

Sample prompt:

> Query the Activity Log for operations on NetworkSecurityGroups and AzureFirewall resources in the last 48 hours. For each rule addition or modification, show: timestamp, caller, resource name, rule name, source/destination configured, and ports.

Mode: Event-driven. Frequency: On NSG change alert. Time saved: High.

## Rollback command generation for bad changes

Status: Added. Source category: Management.

Automatically generates revert commands when a problematic change is identified, reducing MTTR.

Sample prompt:

> A problematic change was detected on resource '{resource_id}' at {timestamp}. Based on Change Analysis, identify what was modified. Generate the az CLI or ARM API command to revert the change to its previous value. Include a safety check (--what-if where available).

Mode: Event-driven. Frequency: On failed change. Time saved: High.
