# Checks catalog

Backup coverage signals. The scan tool answers the virtual machine coverage with Azure Resource Graph, which reads across every accessible subscription and is covered by Reader. The data service checks below need a per resource read and are run by hand with the RunAzCliReadCommands tool.

For each finding the tool records: resource id, resource type, subscription, resource group, the backup state, the last backup time where known, a severity, and the recommended action. If a read is denied, record it as not assessed and continue.

## 1. Virtual machine backup coverage (Resource Graph)

Protected items across Recovery Services vaults and Backup vaults:

```
az graph query -q "recoveryservicesresources | where type =~ 'microsoft.recoveryservices/vaults/backupfabrics/protectioncontainers/protecteditems' | where properties.backupManagementType =~ 'AzureIaasVM' | extend srcId = tolower(tostring(coalesce(properties.virtualMachineId, properties.sourceResourceId))) | project srcId, friendly=tostring(properties.friendlyName), lastBackup=tostring(properties.lastBackupTime), health=tostring(properties.healthStatus), status=tostring(properties.protectionStatus)" --first 1000
```

All virtual machines:

```
az graph query -q "resources | where type =~ 'microsoft.compute/virtualmachines' | project name, id, resourceGroup, subscriptionId, location" --first 1000
```

Classification:

- Unprotected (High): the machine id is not in the protected set.
- Unhealthy (High): the protected item health is not Passed or Healthy.
- Stale (High): the last backup is older than the staleness window (three days by default), or there is no recorded last backup.
- Protected and healthy: not a finding; it counts towards coverage.

Recommendation for a gap: enable Azure Backup on the machine and set a policy that meets the recovery point objective; for an unhealthy or stale item, investigate the failed job in the vault.

## 2. Azure SQL long term retention (manual)

Point in time restore is always on, so the real gap is missing long term retention.

```
az sql db ltr-policy show --resource-group <rg> --server <server> --name <db> --subscription <id>
```

Flag a database with no weekly, monthly, or yearly retention as Medium where the data warrants longer retention.

## 3. Azure Files backup (manual)

```
az backup item list --resource-group <rg> --vault-name <vault> --backup-management-type AzureStorage --subscription <id>
```

Flag file shares that hold important data and are not in the protected item list as Medium.

## 4. Cosmos DB backup mode (manual)

```
az cosmosdb show --resource-group <rg> --name <account> --subscription <id> --query backupPolicy
```

Note the mode. Periodic backup with a long interval is weaker than continuous backup for a critical account; record as Low to Medium depending on the data.

## Staleness window

Three days is the default. Lower it for machines that must back up daily, raise it for machines on a weekly policy. The tool accepts a stale_days argument.
