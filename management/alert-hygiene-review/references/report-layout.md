# Report layout

This skill renders with the shared generator, tools/report_render.py, from a report_data object the scan tool prints, so the report is one pipe:

```
python tools/alert_hygiene.py | python tools/report_render.py
```

## report_data this skill emits

- title: "Alert Hygiene Review". subtitle: alert noise and tuning over the window.
- meta: window is the range read (1d, 7d, or 30d), scope is the count of subscriptions scanned, source is "Azure Monitor alerts".
- summary_cards: alerts fired, noisy rules, rules analyzed, disabled rules.
- charts: alerts by severity, and the noisiest rules by fire count.
- findings: columns rule, fired, auto_resolved, unacknowledged, issue, recommendation, severity. Each row carries a _band equal to its finding severity.
- method_notes: the window used, the thresholds, and any scope not assessed.

## Sections the renderer produces

1. Header with title, window, scope, and generation time.
2. Summary cards led by alerts fired and noisy rules.
3. Overview charts: alerts by severity and the noisiest rules.
4. Findings table, sortable and filterable, the finding severity as a coloured pill.
5. Method and limits.

Fired is the count over the window. Auto resolved is the share that resolved on their own. Unacknowledged is the share still in the New state. A rule that trips more than one signal appears once, at the highest severity among them.
