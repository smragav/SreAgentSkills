# Scenario coverage for finops-cost-optimizer

Category: Billing and Cost. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| Cost anomaly detection | Partial | Hybrid | Daily + event >20% spike | High |
| 6-month cost summary & trends | Partial | Scheduled | Monthly | Medium |
| Top consumer services identification | Partial | Scheduled | Weekly | Low |
| Cost analysis by tag/environment | Partial | Scheduled | Weekly | Medium |
| Cross-period cost comparison (MG level) | Added | Scheduled | Monthly | Medium |
| Consolidated cost reporting | Added | Scheduled | Monthly | Medium |
| Resources with highest cost increase | Partial | Hybrid | Daily + alert >30% WoW | High |
| Underutilized resources detection | Covered | Scheduled | Weekly | High |
| Disk tier-down opportunities | Added | Scheduled | Bi-weekly | Medium |
| Orphaned resources & cost impact analysis | Covered | Scheduled | Daily | High |
| Log Analytics workspace ingestion cost analysis | Added | Scheduled | Weekly | High |
| Budget alerts configuration audit | Added | Scheduled | Monthly | Medium |

## Cost anomaly detection

Status: Partial. Source category: Azure Billing And Active Directory Tenant.

Continuously monitors spending patterns to detect unusual spikes or drops that may indicate misconfigurations, runaway resources, or billing errors.

Sample prompt:

> Analyze the cost data for the last 7 days across all subscriptions. Identify any resource or service where daily cost deviates more than 20% from the 30-day rolling average. Provide the resource ID, cost delta, and likely root cause.

Mode: Hybrid. Frequency: Daily + event >20% spike. Time saved: High.

## 6-month cost summary & trends

Status: Partial. Source category: Azure Billing And Active Directory Tenant.

Provides medium-term cost trend visibility, helping teams understand seasonal patterns and growth trajectory.

Sample prompt:

> Show me a 6-month cost trend summary for subscription '{subscription_name}'. Break down by month, show total and per-service spend, and identify the top 3 services driving growth.

Mode: Scheduled. Frequency: Monthly. Time saved: Medium.

## Top consumer services identification

Status: Partial. Source category: Azure Billing And Active Directory Tenant.

Identifies which Azure services drive the most cost, enabling targeted optimization efforts on highest-impact areas.

Sample prompt:

> List the top 10 Azure services by cost in the last 30 days across all subscriptions. For each, show current month cost, previous month cost, percentage change, and number of instances.

Mode: Scheduled. Frequency: Weekly. Time saved: Low.

## Cost analysis by tag/environment

Status: Partial. Source category: Azure Billing And Active Directory Tenant.

Breaks down Azure spending grouped by environment tags (dev, staging, prod), identifies which environments consume disproportionate budget, and tracks the cost ratio between environments over time.

Sample prompt:

> Show me the cost breakdown for the last month grouped by the 'Environment' tag across all subscriptions. Show the ratio of each environment's cost to production. Highlight any environment where spend exceeds the previous month by more than 15% or where dev/test exceeds 30% of production cost.

Mode: Scheduled. Frequency: Weekly. Time saved: Medium.

## Cross-period cost comparison (MG level)

Status: Added. Source category: Azure Billing And Active Directory Tenant.

Compares cost across billing periods at Management Group level for executive budget reviews.

Sample prompt:

> Compare total cost for management group 'Enterprise' between the current month and the same month last year. Break down by subscription, show absolute and percentage change, and highlight any subscription with >25% increase.

Mode: Scheduled. Frequency: Monthly. Time saved: Medium.

## Consolidated cost reporting

Status: Added. Source category: Azure Billing And Active Directory Tenant.

Produces executive-ready cost reports summarizing spend across management groups, subscriptions, and services for leadership reviews.

Sample prompt:

> Generate a consolidated monthly cost report for all subscriptions under management group 'Production'. Include total spend, month-over-month change, top 10 services by cost, and top 5 fastest-growing resources. Format as a summary suitable for leadership.

Mode: Scheduled. Frequency: Monthly. Time saved: Medium.

## Resources with highest cost increase

Status: Partial. Source category: Azure Billing And Active Directory Tenant.

Identifies individual resources with the sharpest cost growth, catching runaway spending early.

Sample prompt:

> Identify the top 20 resources with the highest absolute cost increase week-over-week across all subscriptions. For each, show resource name, type, previous week cost, current week cost, delta, and percentage increase.

Mode: Hybrid. Frequency: Daily + alert >30% WoW. Time saved: High.

## Underutilized resources detection

Status: Covered. Source category: Azure Billing And Active Directory Tenant.

Finds resources consuming budget but delivering minimal value based on utilization metrics.

Sample prompt:

> Scan all VMs, App Services, SQL Databases, and Redis Caches across subscriptions. Flag resources where average CPU < 5%, average connections < 10, or average requests < 100/hour over the last 7 days. Show monthly cost of each underutilized resource.

Mode: Scheduled. Frequency: Weekly. Time saved: High.

## Disk tier-down opportunities

Status: Added. Source category: Azure Billing And Active Directory Tenant.

Identifies managed disks provisioned at a higher tier than their actual IOPS/throughput demands.

Sample prompt:

> List all Premium SSD and Ultra Disk managed disks. Compare their actual P95 IOPS and throughput over the last 14 days against provisioned tier limits. Recommend tier-down to Standard SSD where actual usage is below Standard SSD limits. Show savings estimate.

Mode: Scheduled. Frequency: Bi-weekly. Time saved: Medium.

## Orphaned resources & cost impact analysis

Status: Covered. Source category: Azure Billing And Active Directory Tenant.

Finds all types of orphaned resources, unattached disks, unused public IPs, orphaned NICs, empty NSGs, idle Load Balancers, zombie snapshots, unused App Gateways/Front Door backends, and empty App Service Plans, in a single consolidated scan.

Sample prompt:

> Query all subscriptions for orphaned resources: (1) managed disks not attached to any VM, (2) public IPs not associated with any resource, (3) NICs not attached to a VM, (4) NSGs not associated with any subnet or NIC, (5) Load Balancers with 0 healthy backend instances or 0 bytes processed in 7 days, (6) disk snapshots older than 90 days whose source disk no longer exists, (7) App Gateway/Front Door backend pools with 0 requests in 14 days, (8) App Service Plans hosting 0 apps or only stopped apps. For each, show resource name, type, RG, age, and monthly cost. Summarize total waste.

Mode: Scheduled. Frequency: Daily. Time saved: High.

## Log Analytics workspace ingestion cost analysis

Status: Added. Source category: Azure Billing And Active Directory Tenant.

Analyzes which data tables and solutions drive the highest log ingestion volume and cost.

Sample prompt:

> For each Log Analytics workspace, show ingestion volume by table for the last 30 days. Identify top 5 tables by GB ingested. Show daily trend, cost per table, and recommend tables that could be moved to Basic tier or have shorter retention.

Mode: Scheduled. Frequency: Weekly. Time saved: High.

## Budget alerts configuration audit

Status: Added. Source category: Azure Billing And Active Directory Tenant.

Ensures every subscription and critical resource group has properly configured budget alerts to prevent surprise overruns.

Sample prompt:

> Check all subscriptions and resource groups tagged 'CostCenter'. Identify those without a budget configured or where budget alerts are set above 100% only. Recommend budget amounts based on 3-month average spend + 20% buffer.

Mode: Scheduled. Frequency: Monthly. Time saved: Medium.
