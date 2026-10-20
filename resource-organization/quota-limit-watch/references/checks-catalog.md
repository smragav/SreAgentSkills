# Checks catalog

Quota and limit signals read from the Azure usage endpoints. The scan tool reads these across the regions each subscription uses. All are covered by Reader. Run any by hand with the RunAzCliReadCommands tool to verify a finding.

For each finding the tool records: subscription, region, quota name, used value, limit, utilization percent, and a severity from the utilization.

## Where to look

First find the regions each subscription actually uses, so the scan does not read every region in Azure:

```
az graph query -q "resources | where isnotempty(location) | summarize by subscriptionId, location" --first 1000
```

Then read the usage counters in those regions.

## 1. Compute quotas (per region)

```
az rest --method GET --url "https://management.azure.com/subscriptions/<id>/providers/Microsoft.Compute/locations/<region>/usages?api-version=2023-07-01"
```

Watch the total regional vCPUs, the per family vCPUs (for example Standard DSv5 Family vCPUs), availability sets, and virtual machine scale sets. A family at its limit blocks new machines of that size even when the regional total has room.

## 2. Network quotas (per region)

```
az rest --method GET --url "https://management.azure.com/subscriptions/<id>/providers/Microsoft.Network/locations/<region>/usages?api-version=2023-09-01"
```

Watch public IP addresses, static public IPs, network interfaces, load balancers, network security groups, virtual networks, and public IP prefixes. Public IP exhaustion is a common cause of a failed scale out.

## 3. Storage quota (per subscription)

```
az rest --method GET --url "https://management.azure.com/subscriptions/<id>/providers/Microsoft.Storage/usages?api-version=2018-07-01"
```

Watch the storage account count against the per subscription per region limit.

## Severity from utilization

- Critical: utilization at or above 95 percent. A deployment or scale out is likely to fail now.
- High: at or above 90 percent.
- Medium: at or above the threshold (80 percent by default) and below 90 percent.
- Below the threshold: not reported.

Recommendation for any finding: request a quota increase for that counter in that region before it blocks work, through Azure portal Quotas, the Microsoft.Quota API, or a support request. The skill never requests the increase itself.

## Tuning

The threshold argument sets the reporting floor. Lower it (for example 70) ahead of a known launch to get an earlier warning. Counters with a limit of zero or an unlimited limit are skipped.
