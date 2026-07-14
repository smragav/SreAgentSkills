# Checks catalog

Readiness checks scoped to one target (a subscription, and optionally a resource group), read with Azure Resource Graph and the usage endpoints, all covered by Reader. The scan tool runs these across three categories and turns the severities into a verdict.

For each finding the tool records: category, resource, subscription, resource group, the issue, a severity, and the recommended change.

## Scope

Every query is filtered to the target: `subscriptionId == '<id>'`, and `resourceGroup =~ '<rg>'` when a resource group is passed. The verdict is about that scope only.

## Reliability

- Virtual machines with no availability zone and no availability set (High). Fix: deploy across zones or an availability set.
- Locally redundant storage (Medium). Fix: use ZRS or GRS where the data warrants it.
- Premium or Business Critical SQL databases without zone redundancy (High). Fix: enable zoneRedundant.

## Internet exposure

- Network security group rules that open management (SSH 22, RDP 3389) or all ports to the internet (Critical), or database ports to the internet (High). Fix: restrict the source or use Private Link.
- Storage accounts allowing anonymous blob access (High). Fix: set allowBlobPublicAccess to false.
- Platform services with public network access enabled (Medium). Fix: use Private Link or restrict to known networks.

## Capacity

- Compute and network usage counters at or above 80 percent of their quota in the regions the scope uses (severity by utilization: 95 percent or higher Critical, 90 or higher High, else Medium). Fix: request a quota increase before the change so scale out does not fail.

## Verdict

Per category, and overall:

- No-go: any Critical or High finding.
- Caution: only Medium findings.
- Go: no findings.

Overall is the worst category verdict. Clear the blocking findings, then run the check again before shipping.
