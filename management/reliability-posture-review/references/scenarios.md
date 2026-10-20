# Scenario coverage for reliability-posture-review

Category: Management. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| RTO/RPO gap analysis | Added | Scheduled | Monthly | High |
| Backup policy compliance & gap detection | Partial | Scheduled | Daily | High |
| SKU reliability assessment | Added | On-demand | Architecture review | High |

## RTO/RPO gap analysis

Status: Added. Source category: Management.

Validates that disaster recovery configurations meet stated RTO/RPO targets for each critical workload.

Sample prompt:

> For all resources tagged 'Tier=Critical', assess DR posture: (1) is backup configured? frequency vs RPO target, (2) is geo-replication enabled? (3) replication lag vs RPO, (4) is there a failover plan? last DR drill date. Flag workloads where configured RPO > stated RPO target or no DR mechanism exists.

Mode: Scheduled. Frequency: Monthly. Time saved: High.

## Backup policy compliance & gap detection

Status: Partial. Source category: Management.

Verifies that all critical resources have backup configured and that backup jobs are completing successfully.

Sample prompt:

> Audit backup coverage: (1) VMs without Azure Backup enabled, (2) SQL databases without backup (PITR or long-term), (3) Cosmos DB accounts without continuous backup, (4) File shares without backup. Also check: failed backup jobs in last 7 days, backup items not backed up in > 24h. Show resource, backup status, last successful backup, and RPO gap.

Mode: Scheduled. Frequency: Daily. Time saved: High.

## SKU reliability assessment

Status: Added. Source category: Management.

Evaluates resource SKUs against availability requirements, identifying single points of failure or SLA gaps.

Sample prompt:

> For resources in production tagged 'SLA=99.99%', check: (1) VM, is it using Availability Zones or VMSS? (2) SQL, is it Zone-redundant? (3) Storage, is it GRS/GZRS? (4) App Service, is it Premium or in ASE? Flag any resource where SKU SLA is below the stated target.

Mode: On-demand. Frequency: Architecture review. Time saved: High.
