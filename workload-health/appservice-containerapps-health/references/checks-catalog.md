# Checks catalog

Web tier reliability and security checks, read from configuration with Azure Resource Graph and covered by Reader. The scan tool evaluates each site, plan, and app; this catalog is the source of truth for each check and its fix. A check is skipped when the configuration field it needs is not present, to avoid false positives.

For each finding the tool records: resource, category, subscription, resource group, the check, a severity, and the recommended change.

## App Service sites (category: App Service)

```
az graph query -q "resources | where type =~ 'microsoft.web/sites' | project name, id, subscriptionId, resourceGroup, kind, properties" --first 1000
```

- HTTPS not enforced (Medium): httpsOnly is false. Fix: set HTTPS Only so HTTP is redirected.
- Minimum TLS below 1.2 (Medium): siteConfig.minTlsVersion is 1.0 or 1.1. Fix: set the minimum TLS version to 1.2.
- Always On disabled (Low, non function apps): siteConfig.alwaysOn is false, so the app cold starts. Fix: enable Always On for a warm app.
- No health check path (Low): siteConfig.healthCheckPath is empty, so unhealthy instances are not removed. Fix: set a health check path.

## App Service plans (category: App Service plan)

```
az graph query -q "resources | where type =~ 'microsoft.web/serverfarms' | project name, id, subscriptionId, resourceGroup, sku, properties" --first 1000
```

- Free or Shared tier (Medium): no SLA and no scale out. Fix: move production workloads to Standard or higher.
- Plan not zone redundant (Low, Standard and above): properties.zoneRedundant is false. Fix: enable zone redundancy for the plan where the workload warrants it.

## Container Apps (category: Container Apps)

```
az graph query -q "resources | where type =~ 'microsoft.app/containerapps' | project name, id, subscriptionId, resourceGroup, properties" --first 1000
```

- Insecure ingress allowed (Medium): configuration.ingress.allowInsecure is true. Fix: disallow insecure ingress so HTTP is not accepted.
- No scale out (Low): template.scale.maxReplicas is 1, so the app cannot scale under load. Fix: raise maxReplicas and set a scale rule.
- No health probes (Low): no container defines a liveness or readiness probe. Fix: add probes so unhealthy replicas are restarted and traffic is held back until ready.

## Verify by hand

```
az webapp show --resource-group <rg> --name <site> --subscription <id> -o jsonc
az webapp config show --resource-group <rg> --name <site> --subscription <id> --query "{alwaysOn:alwaysOn,minTls:minTlsVersion,health:healthCheckPath}"
az containerapp show --resource-group <rg> --name <app> --subscription <id> -o jsonc
```

## Severity

Blast radius and likelihood drive severity. Raise a Free or Shared tier finding when the resource is clearly production; lower a finding when naming or tags mark it non production.
