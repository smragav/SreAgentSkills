---
name: sql-cmdb-inventory
description: |
  Build a full SQL CMDB-style inventory across Azure SQL VM/IaaS, Arc-enabled SQL Server,
  SQL Managed Instance, and Azure SQL. Include SQL version plus Defender for Cloud finding
  counts by total, high, medium, and low. Supports one-off exports and daily scheduled reporting.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - CreateScheduledMonitoringTask
  - UpdateScheduledTask
  - ListScheduledTasks
  - PauseScheduledTask
  - ResumeScheduledTask
  - CancelScheduledTask
  - GetTaskExecutionHistory
  - SaveFileToBlob
---

# SQL CMDB Inventory Skill

Use this skill to produce a full SQL inventory for CMDB purposes across accessible Azure subscriptions.

## When to use

Use this skill when the user asks for any of the following:
- A full inventory of SQL Server resources across Azure
- A CMDB export for SQL estate coverage
- A list of SQL Server on Azure IaaS, Arc-enabled SQL Server, SQL Managed Instance, and Azure SQL
- A daily or scheduled SQL inventory report
- A CSV export with SQL version and Defender for Cloud counts
- A visual summary of SQL estate coverage
- A scalable SQL inventory process for a customer environment with many instances

## Core principle

This skill is inventory-first, not vulnerability-first.

The primary dataset is the discovered SQL resource inventory. Defender for Cloud data is enrichment only. Every discovered in-scope SQL resource must appear in the output whether it has findings or not.

If a resource has no matched Defender findings, emit:
- `DefenderTotal=0`
- `DefenderHigh=0`
- `DefenderMedium=0`
- `DefenderLow=0`

Do not drop resources because Defender data is missing, delayed, unmatched, or unavailable.

## In-scope resource types

Collect server or instance level inventory for these Azure resource types only:
1. `Microsoft.SqlVirtualMachine/sqlVirtualMachines`
2. `Microsoft.AzureArcData/sqlServerInstances`
3. `Microsoft.Sql/managedInstances`
4. `Microsoft.Sql/servers`

Do not expand to per-database rows unless the user explicitly asks for database-level scope.

## Inputs expected

This skill works best when you have:
- Subscription scope, or permission to query all accessible subscriptions
- Whether the user wants a one-off export or a recurring scheduled report
- Preferred delivery format such as CSV, visual summary, or both
- Preferred Defender export file format such as `csv`, `json`, or `parquet`
- Preferred schedule/time zone if recurring delivery is requested

If some details are missing, default to:
- all accessible subscriptions
- CSV export plus compact visual/thread summary
- `csv` as the Defender export file format
- server/instance-level scope
- full CMDB coverage

## Required workflow

1. Discover all in-scope SQL resources across accessible subscriptions.
2. Build the inventory first and treat it as authoritative for row coverage.
3. For each resource, capture:
   - `ResourceType`
   - `SubscriptionId`
   - `ResourceGroup`
   - `Name`
   - `Location`
   - `ResourceId`
4. Enrich each resource with a SQL version field.
5. Enrich each resource with Defender for Cloud counts:
   - `DefenderTotal`
   - `DefenderHigh`
   - `DefenderMedium`
   - `DefenderLow`
6. If Defender data is not found for a resource, set all four Defender fields to zero.
7. Validate that final output row count exactly matches discovered inventory row count.
8. Generate the full inventory artifact.
9. Generate a Defender-focused export and push it to `/cmdb/vulnerabilities/yyyy-mm-dd-sqlserver.<fileFormat>`.
10. Persist the inventory artifact and the Defender export before sharing them with the user.
11. Provide a compact summary that includes:
    - total resources discovered
    - counts by family
    - aggregated Defender totals
    - count of resources with zero Defender findings
    - the Defender export path and file format used
    - any version-normalization or enrichment caveats
12. If the user requests recurring delivery, create or update a scheduled task rather than asking the agent to loop.

## Version quality model

For customer environments with hundreds of SQL instances, do not attempt guest-level version verification for every resource on every run.

Use a two-tier model:

### Tier 1: daily full inventory
Use control-plane and discovered inventory to build the daily CMDB dataset for all resources.

This tier must scale to large estates and should run across the full SQL footprint.

### Tier 2: selective version verification
Use deeper guest or engine validation only for targeted rows such as:
- new resources
- changed resources
- low-confidence rows
- rows with conflicting metadata
- a rotating sample of older SQL on Azure IaaS resources

Do not require guest connectivity to produce the main daily CMDB export.

## Version rules

Normalize the SQL version as follows.

### SQL on Azure IaaS
Do not treat deployment image metadata as authoritative.

- `sqlImageOffer` or marketplace image details tell you how the VM was deployed, not necessarily the current engine version.
- An in-place SQL upgrade can make image metadata stale.
- Best source: guest engine state, such as SQL queries against `SERVERPROPERTY('ProductVersion')`, `SERVERPROPERTY('ProductLevel')`, and `SERVERPROPERTY('Edition')`.
- If guest validation is unavailable, do not present the version as fully verified.

Use these fields when possible:
- `SqlVersion`
- `VersionSource`
- `VersionConfidence`
- `VersionLastSeen`
- `ImageOffer`
- `ReportedProductVersion`
- `UpgradeMismatch`

If guest engine data is available, trust the guest result over image metadata.

If image metadata is all that exists, either:
- emit the inferred version with `VersionSource=ImageOffer` and `VersionConfidence=Low`, or
- emit `SqlVersion=Unverified` if the user wants a stricter CMDB posture

If image metadata and guest engine data disagree, set `UpgradeMismatch=true` and trust the guest value.

### Arc-enabled SQL Server
Use Arc inventory properties such as:
- `properties.version`
- `properties.currentVersion`
- `lastInventoryUploadTime`

These are generally the best source for Arc SQL version reporting and should typically be marked high confidence.

### SQL Managed Instance
Use platform metadata such as `databaseFormat` when available.

This is authoritative enough for CMDB use and should typically be marked high confidence.

### Azure SQL logical server
Use the service/platform version exposed by the resource, typically `12.0`.

Do not fabricate boxed SQL Server versions such as 2019 or 2022 for Azure SQL.

## Defender for Cloud rules

- Prefer Azure Resource Graph and Defender/Security resources for cross-subscription coverage.
- Match Defender findings to the SQL resource ID when possible.
- Aggregate counts by:
  - total
  - high
  - medium
  - low
- If no findings are matched, emit zeros.
- If Defender data for a resource family cannot be retrieved, still publish the full inventory and call out the data gap in the summary.
- In addition to the main inventory artifact, publish a Defender-focused export to `/cmdb/vulnerabilities/yyyy-mm-dd-sqlserver.<fileFormat>`.

## Defender export path and file format

Use this naming convention for the Defender-focused export:
- folder: `/cmdb/vulnerabilities`
- file name: `yyyy-mm-dd-sqlserver.<fileFormat>`
- example: `/cmdb/vulnerabilities/2026-06-22-sqlserver.csv`

Resolve `fileFormat` as follows:
- if the user specifies a format, use that extension exactly
- otherwise default to `csv`
- keep the extension lowercase and consistent with the actual artifact format

The Defender export may contain the same rows as the main inventory or a Defender-focused projection, but it must always preserve inventory-first row coverage and include zero-finding resources.

## Output columns

The CSV should contain exactly these columns at minimum:
- `ResourceType`
- `SubscriptionId`
- `ResourceGroup`
- `Name`
- `Location`
- `ResourceId`
- `SqlVersion`
- `DefenderTotal`
- `DefenderHigh`
- `DefenderMedium`
- `DefenderLow`

For higher-quality CMDB outputs, add these columns when available:
- `VersionSource`
- `VersionConfidence`
- `VersionLastSeen`
- `ImageOffer`
- `ReportedProductVersion`
- `UpgradeMismatch`

If the user explicitly wants more CMDB enrichment, optional fields may also be added, such as:
- `Environment`
- `Owner`
- `BusinessCriticality`
- `TagCoverage`
- `FQDN`
- `PowerState`
- `Sku`
- `Edition`

## Scheduling guidance

If the user requests recurring execution:
- Create a scheduled task instead of implementing an internal wait loop.
- Use a DST-safe approach when the user specifies local business time.
- For 09:00 Central Europe local time, a safe pattern is:
  - trigger at `07:00` and `08:00` UTC
  - continue only when current Europe local time is `09:00`
  - otherwise emit a no-op result and stop

The scheduled run should:
- collect the full inventory
- generate the main inventory artifact
- generate the Defender export at `/cmdb/vulnerabilities/yyyy-mm-dd-sqlserver.<fileFormat>`
- persist both artifacts
- post a compact summary

## Output expectations

The final response should include:
- a downloadable main inventory artifact
- the Defender export path `/cmdb/vulnerabilities/yyyy-mm-dd-sqlserver.<fileFormat>`
- total discovered resources
- counts by family:
  - IaaS SQL VM
  - Arc SQL Server
  - SQL Managed Instance
  - Azure SQL
- aggregated Defender counts across the full inventory
- how many resources have zero Defender findings
- a preview table of the first rows when useful
- version-confidence caveats when some rows were not guest-validated

## Execution guidance

- Prefer Azure Resource Graph for discovery across subscriptions.
- Use resource-specific detail lookups only when needed to retrieve version fields.
- Keep the inventory authoritative and the enrichment secondary.
- Avoid unnecessary repeated calls.
- Do not perform write operations against Azure resources unless the user explicitly requests scheduling changes.
- Always preserve full row coverage even when enrichment is incomplete.
- For large estates, keep the main report fast and use selective version verification instead of blanket guest inspection.

## Example user asks

- "Give me a full SQL CMDB inventory across my subscriptions."
- "List Azure SQL, SQL MI, Arc SQL, and SQL on Azure VMs with versions."
- "Export all SQL resources to CSV and include Defender counts."
- "Schedule this SQL inventory to run daily at 09:00 CET."
- "Show me which SQL resources are covered even if they have no vulnerabilities."
- "How can I handle in-place SQL upgrades without misreporting version?"
