# Checks catalog

Internet exposure signals detected with Azure Resource Graph, covered by Reader. The scan tool runs these; this catalog is the source of truth for each signal and its fix. Run any command by hand with the RunAzCliReadCommands tool to verify a finding.

For each finding the tool records: resource, exposure type, subscription, resource group, what is open, a severity, and the recommended change.

## 1. Network security group rules open to the internet

Pull inbound allow rules, then classify the ports in the tool.

```
az graph query -q "resources | where type =~ 'microsoft.network/networksecuritygroups' | mv-expand rule = properties.securityRules | extend p = rule.properties | where tostring(p.direction) =~ 'Inbound' and tostring(p.access) =~ 'Allow' | project name, id, resourceGroup, subscriptionId, ruleName=tostring(rule.name), src=tostring(p.sourceAddressPrefix), srcs=p.sourceAddressPrefixes, portRange=tostring(p.destinationPortRange), portRanges=p.destinationPortRanges" --first 1000
```

A rule counts as internet facing when its source is *, Internet, or 0.0.0.0/0. Severity by what is open:

- Critical: all ports (*), or management ports (SSH 22, RDP 3389, WinRM 5985 and 5986) open to the internet.
- High: database ports (1433 SQL, 3306 MySQL, 5432 PostgreSQL, 6379 Redis, 27017 Mongo, 1521 Oracle) open to the internet.
- Medium: other specific ports open to the internet.

Fix: restrict the source to known address ranges, put the resource behind a bastion or a load balancer, or use Private Link. Never leave management ports open to the internet.

## 2. Storage with anonymous or public access

```
az graph query -q "resources | where type =~ 'microsoft.storage/storageaccounts' | where tostring(properties.allowBlobPublicAccess) =~ 'true' | project name, id, resourceGroup, subscriptionId" --first 1000
```

Severity High. Fix: set allowBlobPublicAccess to false unless anonymous access is a deliberate, reviewed requirement.

Open network access (no firewall):

```
az graph query -q "resources | where type =~ 'microsoft.storage/storageaccounts' | where tostring(properties.publicNetworkAccess) =~ 'Enabled' and tostring(properties.networkAcls.defaultAction) =~ 'Allow' | project name, id, resourceGroup, subscriptionId" --first 1000
```

Severity Medium. Fix: set the network default action to Deny and allow only known networks, or use Private Link.

## 3. Platform services with public network access

```
az graph query -q "resources | where type in~ ('microsoft.sql/servers','microsoft.keyvault/vaults','microsoft.documentdb/databaseaccounts','microsoft.dbforpostgresql/flexibleservers','microsoft.dbformysql/flexibleservers') | extend pna = tostring(properties.publicNetworkAccess) | where pna =~ 'Enabled' | project name, id, type, resourceGroup, subscriptionId" --first 1000
```

Severity Medium (raise to High when the resource holds sensitive data and has no firewall rules). Fix: disable public network access and use Private Link, or restrict to known networks with firewall rules.

## Severity summary

- Critical: management or all ports open to the internet.
- High: database ports open to the internet, or anonymous blob access allowed.
- Medium: other open ports, open storage network access, or PaaS public network access.

A resource can produce more than one finding when it is exposed in more than one way.
