# Report layout

This skill renders with the shared generator, tools/report_render.py, from a report_data object the scan tool prints, so the report is one pipe:

```
python tools/observability_gap.py | python tools/report_render.py
```

## report_data this skill emits

- title: "Observability Coverage Gap". subtitle: missing diagnostic settings, alerts, action groups, and workspaces.
- meta: window is "Point in time", scope is the count of subscriptions scanned, source is "Azure Resource Graph".
- summary_cards: resources with gaps, resources with no diagnostic settings, subscriptions with no action group, important resources scanned.
- charts: gaps by type (no diagnostic settings, no metric alert, no action group, no workspace), and gaps by subscription.
- findings: columns resource, resource_type, subscription, resource_group, missing, recommendation, severity. Each row carries a _band equal to its severity.
- method_notes: whether diagnostic settings could be read in bulk, and any scope not assessed.

## Sections the renderer produces

1. Header with title, scope, source, and generation time.
2. Summary cards led by resources with gaps.
3. Overview charts: gaps by type and by subscription.
4. Findings table, sortable and filterable, severity as a coloured pill.
5. Method and limits.

A resource missing more than one piece of wiring appears once, with all missing pieces listed and the severity set to the highest among them.
