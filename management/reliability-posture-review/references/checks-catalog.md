# Checks catalog

Reliability signals detected with Azure Resource Graph, which reads across every accessible subscription in one query and is covered by Reader. The scan tool runs these; this catalog is the source of truth for what each signal means and how to fix it. Run any command by hand with the RunAzCliReadCommands tool when you want to verify a finding.

For each finding the tool records: resource id, resource type, subscription, resource group, the signal that fired, a severity, and the recommended change. Severity reflects blast radius and likelihood, per references/scoring-method.md.

If a query returns access denied for a scope, record it as not assessed and continue. Signals that Resource Graph cannot answer alone (backup protection, live idle metrics) are out of scope for this skill.

## 1. Compute with no zone or set redundancy (High)

Standalone virtual machines with no availability zone and no availability set are a single point of failure.

```
az graph query -q "resources | where type =~ 'microsoft.compute/virtualmachines' | where isnull(zones) or array_length(zones) == 0 | where isnull(properties.availabilitySet) | project name, id, resourceGroup, subscriptionId, location" --first 1000
```

Fix: deploy across availability zones, or place the virtual machine in an availability set for rack level redundancy.

## 2. Single instance scale set (Medium)

A scale set running fewer than two instances has no instance level redundancy.

```
az graph query -q "resources | where type =~ 'microsoft.compute/virtualmachinescalesets' | extend capacity = toint(sku.capacity) | where capacity < 2 | project name, id, resourceGroup, subscriptionId, location, capacity" --first 1000
```

Fix: run at least two instances, ideally spread across availability zones.

## 3. Basic SKU public IP (High)

Basic public IP addresses are retiring and offer no zone redundancy.

```
az graph query -q "resources | where type =~ 'microsoft.network/publicipaddresses' | where tostring(sku.name) =~ 'Basic' | project name, id, resourceGroup, subscriptionId, location" --first 1000
```

Fix: migrate to a Standard SKU public IP, which is zone redundant by default.

## 4. Basic load balancer (High)

Basic Load Balancer is retiring and has no availability zone support or SLA.

```
az graph query -q "resources | where type =~ 'microsoft.network/loadbalancers' | where tostring(sku.name) =~ 'Basic' | project name, id, resourceGroup, subscriptionId, location" --first 1000
```

Fix: migrate to Standard Load Balancer.

## 5. Premium SQL database without zone redundancy (High)

Premium and Business Critical databases support zone redundant failover; without it a zone outage takes the database down.

```
az graph query -q "resources | where type =~ 'microsoft.sql/servers/databases' | where tostring(properties.zoneRedundant) =~ 'false' | where tostring(sku.tier) in~ ('Premium','BusinessCritical') | project name, id, resourceGroup, subscriptionId, location, tier=tostring(sku.tier)" --first 1000
```

Fix: enable zoneRedundant on the database.

## 6. Locally redundant storage (Medium)

LRS keeps three copies in one datacentre with no zone or regional protection.

```
az graph query -q "resources | where type =~ 'microsoft.storage/storageaccounts' | where tostring(sku.name) endswith 'LRS' | project name, id, resourceGroup, subscriptionId, location, sku=tostring(sku.name)" --first 1000
```

Fix: use ZRS for zone redundancy, or GRS and RA-GRS for regional redundancy where the data warrants it.

## 7. Application Gateway not zone redundant (Medium)

```
az graph query -q "resources | where type =~ 'microsoft.network/applicationgateways' | where isnull(zones) or array_length(zones) == 0 | project name, id, resourceGroup, subscriptionId, location" --first 1000
```

Fix: redeploy the gateway across availability zones (v2 SKU).

## 8. AKS node pool without zones or a single node (Medium)

```
az graph query -q "resources | where type =~ 'microsoft.containerservice/managedclusters' | mv-expand pool = properties.agentPoolProfiles | extend zones = pool.availabilityZones, nodes = toint(pool['count']) | where isnull(zones) or array_length(zones) == 0 or nodes < 2 | project name, id, resourceGroup, subscriptionId, location, pool=tostring(pool.name)" --first 1000
```

Fix: spread node pools across availability zones and run at least two nodes.

## 9. Single region Cosmos DB account (Medium)

```
az graph query -q "resources | where type =~ 'microsoft.documentdb/databaseaccounts' | extend regions = properties.locations | where array_length(regions) < 2 | project name, id, resourceGroup, subscriptionId, location" --first 1000
```

Fix: add a second region and enable automatic failover for regional resilience.

## Beyond Resource Graph

- Backup protection coverage: check Azure Backup Center.
- Live idle or underused resources: use the cost skill's idle detection.
- Service level objective attainment: read Azure Resource Health history and Service Health for the affected resources when a finding needs corroboration.
