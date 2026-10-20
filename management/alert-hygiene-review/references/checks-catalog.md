# Checks catalog

Alert hygiene signals from Azure Monitor. The scan tool reads the fired alert history and the alert rules; all reads are covered by Reader. Run any by hand with the RunAzCliReadCommands tool to verify.

For each finding the tool records: rule name, the fire count over the window, the auto resolved share, the unacknowledged share, the highest severity seen, the issue, a severity for the finding, and the recommended tuning.

## Read the fired alerts

```
az rest --method GET --url "https://management.azure.com/subscriptions/<id>/providers/Microsoft.AlertsManagement/alerts?api-version=2019-05-05-preview&timeRange=7d"
```

Each alert carries an essentials block with the rule (alertRule), severity (Sev0 to Sev4), monitorCondition (Fired or Resolved), and alertState (New, Acknowledged, or Closed). Group by rule and count.

## Read the disabled rules

```
az graph query -q "resources | where type in~ ('microsoft.insights/metricalerts','microsoft.insights/scheduledqueryrules') | extend enabled = tostring(properties.enabled) | where enabled =~ 'false' | project name, id, type, resourceGroup, subscriptionId" --first 1000
```

## Signals and thresholds

- Noisy (Medium, or High at twice the threshold): the rule fired at or above the noisy threshold over the window (20 by default). A single rule generating a large share of the pages is the first thing to tune. Fix: widen the threshold, add a dynamic threshold, lengthen the aggregation window, or split the scope.
- Cries wolf (Medium): the highest severity is Sev0 or Sev1, yet at least 80 percent of its alerts auto resolved without anyone acting, over five or more fires. Fix: lower the severity to match the real urgency, or make the condition more specific.
- Alerts not acknowledged (Medium): at least half of the rule's alerts are still in the New state over five or more fires. Fix: confirm the rule routes to an action group a team watches, or retire it if it is not useful.
- Disabled rule (Medium): the rule exists but is turned off, so its signal is not watched. Fix: re enable it or delete it so the intent is clear.

Combine per rule: a rule that trips more than one signal appears once, listing them, at the highest severity among them.

## Window

Seven days is the default and matches the Azure Monitor short ranges. Use 1d for a quick look after an incident, or 30d for a broad tuning pass. The tool maps the window argument to the nearest allowed range (1d, 7d, or 30d).
