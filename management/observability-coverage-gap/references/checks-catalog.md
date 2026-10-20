# Checks catalog

Observability wiring signals, read with Azure Resource Graph where it can answer across every accessible subscription, and with a per resource read where it cannot. All are covered by Reader.

For each finding the tool records: resource id, resource type, subscription, resource group, the missing wiring, a severity, and the recommended fix.

## Important resource types

These are the types worth monitoring. The scan enumerates them; adjust the list in the tool if your estate leans on other services.

```
az graph query -q "resources | where type in~ ('microsoft.compute/virtualmachines','microsoft.web/sites','microsoft.sql/servers/databases','microsoft.storage/storageaccounts','microsoft.keyvault/vaults','microsoft.containerservice/managedclusters','microsoft.network/applicationgateways','microsoft.network/loadbalancers','microsoft.documentdb/databaseaccounts','microsoft.cache/redis','microsoft.servicebus/namespaces','microsoft.eventhub/namespaces','microsoft.dbforpostgresql/flexibleservers','microsoft.dbformysql/flexibleservers','microsoft.apimanagement/service','microsoft.containerregistry/registries','microsoft.network/azurefirewalls') | project name, id, type, resourceGroup, subscriptionId, location" --first 1000
```

## 1. No metric alert (Medium)

Build the set of resources covered by a metric alert from the alert scopes, then flag important resources not in it.

```
az graph query -q "resources | where type =~ 'microsoft.insights/metricalerts' | mv-expand scope = properties.scopes | project alert=name, scope=tolower(tostring(scope))" --first 1000
```

A resource is covered when its id, its resource group, or its subscription appears as an alert scope. Fix: add a metric alert on the key signals for the resource (for example CPU and availability), targeting an action group.

## 2. No diagnostic settings (High)

Diagnostic settings route resource logs and metrics to a workspace, storage, or Event Hub. Without them the resource is effectively blind.

Bulk check where Resource Graph can answer:

```
az graph query -q "resources | where type =~ 'microsoft.insights/diagnosticsettings' | extend parentId = tolower(substring(id, 0, indexof(id, '/providers/microsoft.insights/diagnosticsettings'))) | distinct parentId" --first 1000
```

If that returns nothing in your tenant, verify per resource instead:

```
az monitor diagnostic-settings list --resource <resource id>
```

Fix: add a diagnostic setting that sends the platform logs and metrics to the central Log Analytics workspace.

## 3. No action group in the subscription (High)

An alert with nowhere to send a notification is silent.

```
az graph query -q "resources | where type =~ 'microsoft.insights/actiongroups' | summarize count() by subscriptionId" --first 1000
```

A subscription that has resources but no action group gets one finding. Fix: create at least one action group so alerts can notify a team.

## 4. No Log Analytics workspace in the subscription (Medium)

```
az graph query -q "resources | where type =~ 'microsoft.operationalinsights/workspaces' | summarize count() by subscriptionId" --first 1000
```

A subscription with resources but no workspace has nowhere central to land logs. Fix: create a workspace and point diagnostic settings at it.

## Severity

- No diagnostic settings: High. The resource emits nothing to central logging.
- No action group in the subscription: High. Alerts cannot notify.
- No metric alert: Medium. The resource is logged but not actively watched.
- No workspace in the subscription: Medium. Structural gap that blocks central logging.

Combine per resource: a resource missing several pieces gets one finding listing them, at the highest severity among them.
