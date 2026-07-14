# Checks catalog

Change and effect signals read from the Azure Activity Log, covered by Reader. The scan tool reads and correlates these; this catalog is the source of truth. Run the read by hand with the RunAzCliReadCommands tool to verify a finding.

For each finding the tool records: time, resource, the change (operation and caller), the outcome, a severity, and a note (the degradation it preceded, or why it stands out).

## Read the Activity Log

```
az rest --method GET --url "https://management.azure.com/subscriptions/<id>/providers/microsoft.insights/eventtypes/management/values?api-version=2015-04-01&$filter=eventTimestamp ge '<iso start>'"
```

Each event carries eventTimestamp, operationName, status, caller, resourceId, resourceGroupName, and a category. The tool splits events into two groups:

- Changes: category Administrative, where the operation is a write, delete, or action (not a read).
- Health events: category ResourceHealth, where the current health status is Unavailable or Degraded.

## Correlate change to effect

For each health degradation, the tool looks for changes on the same resource, or in the same resource group, within the preceding window (two hours by default). When it finds one, it emits a finding:

- Change preceded a health degradation (High): a change was applied to the resource (or its resource group) shortly before it went Unavailable or Degraded. Note records the degradation and the time gap. This is the headline signal.

Correlation is not proof. The time gap is the evidence; a human confirms cause.

## Standalone change signals

Changes not linked to a degradation are still worth a look when they are:

- A delete (Medium): a resource was deleted. Confirm it was intended.
- A failed change (Medium): a write or action returned Failed. A failed change can leave a resource half configured.

Other successful changes are counted in the summary but not listed individually, to keep the report focused on what matters.

## Window

Seven days is the default read window. The correlation window (how far before a degradation to look for a change) is two hours by default. Widen the read window for a broad audit, or narrow it to the hours around a known incident.
