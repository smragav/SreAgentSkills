# Report layout

This skill renders with the shared generator, tools/report_render.py, from a report_data object the scan tool prints, so the report is one pipe and matches the look and feel of every other report in this repository:

```
python tools/pattern_scan.py | python tools/report_render.py
```

## report_data this skill emits

- title: "Recurring Incident Patterns". subtitle: repeat offenders over the window.
- meta: window is the range read (for example 30d), scope is the count of subscriptions scanned, source is "Azure Monitor alerts and Resource Health".
- summary_cards: total incidents, repeat offenders, resources affected, window.
- charts: incidents by resource type, and the top repeat offenders by incident count.
- findings: columns resource, resource_type, incidents, signals, recommendation, severity. Each row carries a _band equal to its severity, and a numeric sort hint on incidents.
- method_notes: the window and the repeat threshold.

## Sections the renderer produces

1. Header with title, window, scope, and generation time.
2. Summary cards led by repeat offenders.
3. Overview charts: incidents by resource type and the top offenders.
4. Findings table, sortable and filterable, severity as a coloured pill, sorted by incident count.
5. Method and limits.

The signals column explains the count: how many alerts and how many health degradations make up each offender's total, so the ranking is transparent.
