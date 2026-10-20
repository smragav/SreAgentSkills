# Scenario coverage for network-exposure-review

Category: Network. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| Private endpoint & public exposure audit | Covered | Scheduled | Weekly | High |
| Public IP inventory & justification | Partial | Scheduled | Weekly | Medium |
| Overly permissive NSG rules audit | Covered | Scheduled | Daily | High |
| DDoS protection coverage audit | Added | Scheduled | Monthly | Medium |

## Private endpoint & public exposure audit

Status: Covered. Source category: Network Topology And Connectivity.

Identifies PaaS resources still accessible over public internet that should use Private Endpoints, and inventories all publicly accessible resources for attack surface awareness.

Sample prompt:

> List all Storage Accounts, SQL Servers, Key Vaults, Cosmos DB, App Services, and other PaaS resources across subscriptions. For each, check: (1) is public network access enabled? (2) are there private endpoints configured? (3) what is the public FQDN/IP? Flag resources with public access enabled but no private endpoint. Show resource, public endpoint, and recommendation.

Mode: Scheduled. Frequency: Weekly. Time saved: High.

## Public IP inventory & justification

Status: Partial. Source category: Network Topology And Connectivity.

Inventories all public IP addresses, identifies orphaned ones, and validates that each attached PIP is justified.

Sample prompt:

> List all Public IP addresses across subscriptions. For each, show: resource name, IP address, SKU, associated resource (or 'unattached'), allocation method, and creation date. Flag PIPs that are: unattached, attached to stopped VMs, or attached to non-production resources.

Mode: Scheduled. Frequency: Weekly. Time saved: Medium.

## Overly permissive NSG rules audit

Status: Covered. Source category: Network Topology And Connectivity.

Identifies network security rules that are too broad, exposing resources to unnecessary risk.

Sample prompt:

> Scan all NSGs across subscriptions. Flag rules where: (1) source = 'Any' or '0.0.0.0/0' on non-load-balancer ports, (2) destination port = '*' (any), (3) priority allows wide port ranges (>100 ports). Show NSG name, rule name, direction, access, source, destination, and port range. Recommend tighter scoping.

Mode: Scheduled. Frequency: Daily. Time saved: High.

## DDoS protection coverage audit

Status: Added. Source category: Network Topology And Connectivity.

Identifies VNets hosting public-facing workloads without DDoS Protection Standard enabled.

Sample prompt:

> List all VNets containing subnets with public IP addresses or Application Gateways. Check whether DDoS Protection Standard is enabled on each VNet. Flag VNets with public-facing resources but no DDoS protection. Show VNet name, public resource count, and estimated DDoS plan cost.

Mode: Scheduled. Frequency: Monthly. Time saved: Medium.
