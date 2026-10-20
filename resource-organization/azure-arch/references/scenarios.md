# Scenario coverage for azure-arch

Category: Resource Organization. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| Management Group hierarchy audit | Added | Scheduled | Monthly | Medium |
| Subscription hygiene score | Added | Scheduled | Weekly | High |
| Resource group sprawl detection | Added | Scheduled | Weekly | Medium |
| Resource lock compliance audit | Added | Scheduled | Weekly | Medium |
| Move resources between subscriptions | Added | On-demand | During reorg | High |

## Management Group hierarchy audit

Status: Added. Source category: Resource Organization.

Validates the MG hierarchy structure, finding misplaced subscriptions or empty management groups.

Sample prompt:

> Show the full Management Group hierarchy tree. For each MG, show: child subscription count, policies assigned, and RBAC roles. Flag: (1) empty MGs with no children, (2) subscriptions directly under root MG, (3) MGs with conflicting policies compared to parent.

Mode: Scheduled. Frequency: Monthly. Time saved: Medium.

## Subscription hygiene score

Status: Added. Source category: Resource Organization.

Computes a composite health score per subscription measuring operational maturity across multiple dimensions.

Sample prompt:

> Calculate a hygiene score (0-100) for each subscription based on: (1) tag compliance (20%), (2) resource lock coverage (15%), (3) alert rule coverage (20%), (4) diagnostic settings coverage (15%), (5) policy compliance (15%), (6) Defender for Cloud score (15%). Show score breakdown and improvement recommendations for subscriptions scoring < 70.

Mode: Scheduled. Frequency: Weekly. Time saved: High.

## Resource group sprawl detection

Status: Added. Source category: Resource Organization.

Identifies resource group proliferation that increases management overhead and indicates organizational disorder.

Sample prompt:

> Analyze all resource groups across subscriptions. Flag: (1) empty RGs with 0 resources, (2) RGs with only 1 resource (consolidation candidate), (3) RGs with names suggesting temporary/test purpose in production, (4) RGs without required tags. Show RG name, resource count, total cost, and creation date.

Mode: Scheduled. Frequency: Weekly. Time saved: Medium.

## Resource lock compliance audit

Status: Added. Source category: Resource Organization.

Ensures production resources have appropriate delete locks to prevent accidental deletion.

Sample prompt:

> Check all resources in subscriptions tagged 'Environment=Production'. Identify resources of type VM, SQL Server, Storage Account, Key Vault, and AKS that do NOT have a CanNotDelete or ReadOnly lock. Show resource name, type, RG, and recommend lock type.

Mode: Scheduled. Frequency: Weekly. Time saved: Medium.

## Move resources between subscriptions

Status: Added. Source category: Resource Organization.

Validates and plans resource moves between subscriptions, checking for blockers and dependencies.

Sample prompt:

> Evaluate moving resources from resource group '{source_rg}' to subscription '{target_subscription}'. Run validation: (1) check resource types that support move, (2) identify resources that cannot be moved (locks, dependencies), (3) check quota in target subscription, (4) identify impacted RBAC and policies. Generate the move command with --validate-only first.

Mode: On-demand. Frequency: During reorg. Time saved: High.
