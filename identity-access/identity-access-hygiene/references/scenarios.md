# Scenario coverage for identity-access-hygiene

Category: Identity and Access. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| RBAC redundancy & over-privilege assessment | Covered | Scheduled | Weekly | High |
| RBAC access audit (who has what) | Added | Scheduled | Weekly | High |
| Permissions required for an action | Added | On-demand | During access request | Medium |
| Stale RBAC assignments | Covered | Scheduled | Weekly | High |
| High-privilege operation tracking | Added | Scheduled | Daily | High |

## RBAC redundancy & over-privilege assessment

Status: Covered. Source category: Identity And Access Management.

Analyzes all role assignments across scopes to detect redundancies (e.g., same identity assigned Contributor at both subscription and child resource group level) and over-privileged assignments where a narrower role would suffice. Helps reduce attack surface and simplify access governance.

Sample prompt:

> Analyze all RBAC role assignments across subscriptions. Identify: (1) redundant assignments, same principal with the same or higher role at a parent scope making child-scope assignments unnecessary, (2) principals with Owner or Contributor that could operate with a narrower built-in role based on their Activity Log operations in the last 30 days, (3) multiple role assignments to the same principal at the same scope that could be consolidated. For each finding, show principal name, type, assigned roles, scopes, and recommended action.

Mode: Scheduled. Frequency: Weekly. Time saved: High.

## RBAC access audit (who has what)

Status: Added. Source category: Identity And Access Management.

Provides comprehensive visibility into access grants, highlighting over-privileged accounts and stale assignments.

Sample prompt:

> List all role assignments across subscription '{subscription_name}'. For each, show: principal name, principal type (user/group/SP), role, scope, assignment source (direct/inherited). Flag: (1) Owner/Contributor at subscription scope, (2) assignments to individual users (should be groups), (3) assignments where principal no longer exists in Entra ID.

Mode: Scheduled. Frequency: Weekly. Time saved: High.

## Permissions required for an action

Status: Added. Source category: Identity And Access Management.

Determines the minimum RBAC permissions required to perform a specific Azure operation, supporting least-privilege design.

Sample prompt:

> What is the minimum RBAC role or specific permissions needed to perform: '{operation_description}'? Show: (1) required resource provider operations (e.g., Microsoft.Compute/virtualMachines/start/action), (2) matching built-in role(s), (3) if no exact match, a custom role definition JSON with minimum permissions.

Mode: On-demand. Frequency: During access request. Time saved: Medium.

## Stale RBAC assignments

Status: Covered. Source category: Identity And Access Management.

Finds role assignments granted to principals that no longer exist or haven't signed in, reducing attack surface.

Sample prompt:

> List all role assignments where: (1) the principal object no longer exists in Entra ID (orphaned SIDs), (2) the user principal hasn't signed in for > 90 days, (3) the service principal has no recent activity. Show assignment scope, role, principal display name/ID, and last sign-in date. Recommend removal.

Mode: Scheduled. Frequency: Weekly. Time saved: High.

## High-privilege operation tracking

Status: Added. Source category: Identity And Access Management.

Monitors sensitive operations (role assignments, policy changes, key vault access) that could indicate security issues or excessive privilege use.

Sample prompt:

> Query Activity Log for the last 24 hours. Filter for high-privilege operations: role assignment create/delete, policy assignment create/delete, key vault secret access, subscription-level deployments, management group changes. Show caller, operation, target, and timestamp.

Mode: Scheduled. Frequency: Daily. Time saved: High.
