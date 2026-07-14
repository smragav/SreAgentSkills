# Checks catalog

Recurring incident signals read from Azure Monitor alerts and the Activity Log resource health events, covered by Reader. The scan tool reads and aggregates these over the window.

For each repeat offender the tool records: resource, resource type, the incident count, the signals (alerts and health degradations), a severity from the count, and the recommended focus.

## Read the fired alerts

```
az rest --method GET --url "https://management.azure.com/subscriptions/<id>/providers/Microsoft.AlertsManagement/alerts?api-version=2019-05-05-preview&timeRange=30d"
```

Each alert carries an essentials block with the affected resource (targetResource) and its type. The tool counts alerts per resource.

## Read the resource health degradations

```
az rest --method GET --url "https://management.azure.com/subscriptions/<id>/providers/microsoft.insights/eventtypes/management/values?api-version=2015-04-01&$filter=eventTimestamp ge '<iso start>'"
```

The tool keeps the ResourceHealth events where the current health status is Unavailable or Degraded, and counts them per resource.

## Aggregate and rank

- Incident count per resource equals its alert count plus its health degradation count over the window.
- A resource at or above the repeat threshold (three by default) is a repeat offender.
- Severity by incident count: ten or more High, five to nine Medium, three to four Low.
- Offenders are grouped by resource type, so a pattern across many resources of one type is visible.

## Window and threshold

Thirty days is the default window, mapped to the Azure Monitor short ranges (1d, 7d, or 30d) for alerts. The repeat threshold is three incidents. Widen the window to see chronic patterns, or lower the threshold to catch emerging ones.

## Recommended focus

For each offender, the recommendation points at the durable fix rather than another alert: for a resource that keeps going Unavailable, review its redundancy and dependencies; for one that keeps firing the same alert, tune the workload or the threshold. The value is directing reliability investment to where it pays back.
