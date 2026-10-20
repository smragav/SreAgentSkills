# Scenario coverage for tag-governance-compliance

Category: Governance. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| Naming & tagging convention compliance | Covered | Scheduled | Weekly | Medium |
| Custom Policy generation | Added | On-demand | During governance sprint | High |
| Find built-in policy for a requirement | Added | On-demand | During compliance planning | Medium |
| Policy compliance state monitoring | Added | Scheduled | Daily | Medium |
| Effective policies per scope | Added | On-demand | During audit | Medium |
| Policy exemptions review | Added | Scheduled | Weekly | Medium |
| Automated compliance remediation tasks | Added | Scheduled | Weekly | High |
| Azure Policy assignment assessment | Added | Scheduled | Monthly | High |

## Naming & tagging convention compliance

Status: Covered. Source category: Governance.

Detects resources that violate organizational naming standards and required tag policies, impacting automation, cost allocation, and operational clarity.

Sample prompt:

> Check all resources against: (1) naming convention regex per resource type: VMs='{vm_pattern}', RGs='{rg_pattern}', Storage='{storage_pattern}'; (2) required tags: 'Environment', 'CostCenter', 'Owner', 'Application'. Show resources not matching patterns and those missing required tags. Prioritize production resources and sort by monthly cost.

Mode: Scheduled. Frequency: Weekly. Time saved: Medium.

## Custom Policy generation

Status: Added. Source category: Governance.

Generates Azure Policy definitions for custom compliance requirements that aren't covered by built-in policies.

Sample prompt:

> Generate an Azure Policy definition that: {requirement_description}. Include the policy rule, parameters, effect (audit/deny/modify), and the az CLI command to deploy it at subscription scope. Follow Microsoft naming conventions.

Mode: On-demand. Frequency: During governance sprint. Time saved: High.

## Find built-in policy for a requirement

Status: Added. Source category: Governance.

Searches Azure's built-in policy catalog to find the best match for a compliance requirement before creating custom.

Sample prompt:

> I need to enforce that: '{requirement}'. Search Azure built-in policies for matching definitions. Show the top 5 matches with: display name, policy ID, effect type, and description. Indicate which one best fits the requirement and whether parameters need customization.

Mode: On-demand. Frequency: During compliance planning. Time saved: Medium.

## Policy compliance state monitoring

Status: Added. Source category: Governance.

Tracks compliance state trends and identifies resources falling out of compliance over time.

Sample prompt:

> Show policy compliance summary for subscription '{subscription_name}'. Include: (1) total policies assigned, (2) compliant vs non-compliant resource count, (3) top 10 policies by non-compliance count, (4) resources that became non-compliant in the last 7 days. Show trend vs previous week.

Mode: Scheduled. Frequency: Daily. Time saved: Medium.

## Effective policies per scope

Status: Added. Source category: Governance.

Shows all policies that actually apply to a specific scope, helping debug policy conflicts and understand cumulative governance.

Sample prompt:

> List all effective policies at scope '{scope}' (subscription/RG/resource). Show: policy name, assignment scope (inherited from where), effect, parameters, and exemptions if any. Identify conflicting policies (e.g., one audits and another denies the same condition).

Mode: On-demand. Frequency: During audit. Time saved: Medium.

## Policy exemptions review

Status: Added. Source category: Governance.

Audits policy exemptions to find expired ones and those without proper justification that may be covering non-compliance.

Sample prompt:

> List all policy exemptions across subscriptions. Show: exemption name, scope, exempted policy, category (waiver/mitigated), expiration date, and description. Flag: (1) exemptions past their expiration date, (2) exemptions without an expiration date, (3) exemptions with no description/justification.

Mode: Scheduled. Frequency: Weekly. Time saved: Medium.

## Automated compliance remediation tasks

Status: Added. Source category: Governance.

Triggers Azure Policy remediation tasks for resources that are non-compliant with 'DeployIfNotExists' or 'Modify' policies.

Sample prompt:

> List all non-compliant resources under policies with effect 'DeployIfNotExists' or 'Modify' that have a remediation task available. For each policy: (1) count of remediable resources, (2) create a remediation task if none exists or last task is > 7 days old, (3) check status of in-progress remediation tasks. Report: tasks created, in-progress, and completed.

Mode: Scheduled. Frequency: Weekly. Time saved: High.

## Azure Policy assignment assessment

Status: Added. Source category: Governance.

Performs a global assessment of all Azure Policy assignments across the management group hierarchy to detect redundancies (same policy assigned at parent and child scope), conflicts (contradictory effects on the same resource type), and shadow assignments (overridden by a higher-scope exemption or a conflicting deny). Provides a clean-sheet view of the effective policy posture.

Sample prompt:

> List all Azure Policy assignments across the full management group hierarchy. Analyze for: (1) redundant assignments, same policy definition assigned at both a management group and a child subscription/RG, (2) conflicting assignments, policies with contradictory effects (e.g., one enforces 'deny' on a resource type while another applies 'deployIfNotExists' for the same), (3) orphaned assignments referencing deleted or deprecated policy definitions, (4) assignments with parameters that override or negate the intended effect. For each finding, show policy name, assignment scope, effect, and recommended action (remove, consolidate, or fix). Summarize total assignments, redundancies found, and conflicts detected.

Mode: Scheduled. Frequency: Monthly. Time saved: High.
