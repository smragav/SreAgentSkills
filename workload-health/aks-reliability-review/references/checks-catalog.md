# Checks catalog

AKS reliability and operational checks, read from the managed cluster configuration with Azure Resource Graph and covered by Reader. The scan tool evaluates each cluster; this catalog is the source of truth for each check and its fix.

For each finding the tool records: cluster, subscription, resource group, the check, a severity, and the recommended change.

## Enumerate clusters

```
az graph query -q "resources | where type =~ 'microsoft.containerservice/managedclusters' | project name, id, subscriptionId, resourceGroup, sku, properties" --first 1000
```

The tool reads the properties object for each cluster.

## Checks

1. Old Kubernetes version (High below minor 1.28, Medium just below). Fix: upgrade to a supported version and stay within the N minus two window.
2. Node pool without availability zones (Medium). A pool with no zones cannot survive a zone loss. Fix: recreate the pool across zones.
3. Single node pool node count below two (Medium). No node redundancy. Fix: run at least two nodes, and enable the cluster autoscaler.
4. No dedicated system node pool (Low). System pods share user workloads. Fix: add a system mode node pool so control components are isolated.
5. Control plane open to the internet (Medium). Neither a private cluster nor API server authorized IP ranges. Fix: enable a private cluster, or set authorized IP ranges.
6. No auto upgrade channel (Medium). Patches are not applied automatically. Fix: set an upgrade channel (for example patch or stable) with a maintenance window.
7. Container Insights not enabled (Medium). No cluster monitoring add on. Fix: enable Azure Monitor Container Insights.
8. No network policy (Low). Pod to pod traffic is unrestricted. Fix: enable a network policy (Azure or Calico) and default deny where practical.
9. Entra ID and Kubernetes RBAC not enabled (Medium). Fix: enable Entra ID integration and Kubernetes RBAC for authenticated, authorised access.
10. Free tier with no uptime SLA (Low, Medium for production). Fix: move to the Standard tier for the control plane uptime SLA on production clusters.

## Verify a cluster by hand

```
az aks show --resource-group <rg> --name <cluster> --subscription <id> -o jsonc
az aks nodepool list --resource-group <rg> --cluster-name <cluster> --subscription <id> --query "[].{name:name,count:count,zones:availabilityZones,mode:mode}"
```

## Severity

Blast radius and likelihood drive severity, as elsewhere. Raise a Free tier finding to Medium when the cluster name or tags mark it production; lower a single node finding to Low when it is a lab or sandbox.
