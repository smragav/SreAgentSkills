# Checks catalog

Deprecation and retirement signals detected with Azure Resource Graph, covered by Reader. The scan tool applies these; retirement dates move, so corroborate specifics against Azure Service Health planned retirements and the Azure roadmap.

For each finding the tool records: resource id, resource type, category, subscription, resource group, the deprecated element, a severity, and the recommended target.

## 1. End of life App Service runtimes (category: App Service runtime)

```
az graph query -q "resources | where type =~ 'microsoft.web/sites' | extend fx = tostring(properties.siteConfig.linuxFxVersion) | where isnotempty(fx) | project name, id, subscriptionId, resourceGroup, fx" --first 1000
```

The tool matches the linuxFxVersion against an end of life runtime list (older Python, Node, PHP, .NET, and Java stacks). High for a stack already out of support, Medium for one approaching it. Fix: move the app to a supported runtime version. Windows stacks are not parsed here; check them by hand.

## 2. Retired database single servers (category: Retired service)

Azure Database for PostgreSQL and MySQL Single Server are retired in favour of Flexible Server.

```
az graph query -q "resources | where type in~ ('microsoft.dbforpostgresql/servers','microsoft.dbformysql/servers') | project name, id, type, subscriptionId, resourceGroup" --first 1000
```

Severity High. Fix: migrate to Flexible Server.

## 3. Classic resources (category: Classic)

Classic (Azure Service Manager) resources are retired.

```
az graph query -q "resources | where type startswith 'microsoft.classiccompute' or type startswith 'microsoft.classicstorage' or type startswith 'microsoft.classicnetwork' | project name, id, type, subscriptionId, resourceGroup" --first 1000
```

Severity High. Fix: migrate to the Azure Resource Manager equivalent.

## 4. Old Kubernetes versions (category: AKS version)

```
az graph query -q "resources | where type =~ 'microsoft.containerservice/managedclusters' | project name, id, subscriptionId, resourceGroup, kubernetesVersion=tostring(properties.kubernetesVersion)" --first 1000
```

The tool flags clusters below the supported floor (minor 1.28 by default). High when well below the floor, Medium when just below. Fix: upgrade to a supported version and stay on the N minus two window.

## 5. End of life operating system images (category: VM OS)

```
az graph query -q "resources | where type =~ 'microsoft.compute/virtualmachines' | extend img = properties.storageProfile.imageReference | project name, id, subscriptionId, resourceGroup, publisher=tostring(img.publisher), offer=tostring(img.offer), sku=tostring(img.sku)" --first 1000
```

The tool matches the image against an end of life list (older Windows Server, older Ubuntu, CentOS). High for an image already out of support, Medium for one approaching it. Fix: rebuild on a supported image, or move to a managed platform where possible. Custom images have no image reference and are skipped.

## Beyond Resource Graph

- Deprecated API versions used by deployments are not stored on the resource; scan your infrastructure as code and pipeline logs for those, and watch Azure Service Health health advisories.
- Basic tier public IP and Basic Load Balancer retirements are reported by the reliability-posture-review skill; they are not duplicated here.

## Severity

- High: already retired or out of support.
- Medium: approaching end of support within roughly a year, or just below the supported floor.
- Low: reserved for a soft deprecation with a long runway.
