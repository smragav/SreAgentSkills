# Report layout

This skill renders with the shared generator, tools/report_render.py, from a report_data object the scan tool prints on standard output, so the report is one pipe:

```
python tools/backup_coverage.py | python tools/report_render.py
```

## report_data this skill emits

- title: "Backup and Recovery Coverage". subtitle: virtual machine backup protection and health.
- meta: window is the staleness threshold in days, scope is the count of subscriptions scanned, source is "Azure Resource Graph".
- summary_cards: coverage percent, virtual machines, unprotected count, at risk count (unhealthy or stale).
- charts: virtual machine backup state (Protected, Unprotected, At risk), and gaps by subscription.
- findings: columns resource, subscription, resource_group, state, last_backup, recommendation, severity. Each row carries a _band equal to its severity.
- method_notes: the staleness window used, the data services checked by hand, and any scope not assessed.

## Sections the renderer produces

1. Header with title, staleness window, scope, and generation time.
2. Summary cards led by coverage percent.
3. Overview charts: backup state and gaps by subscription.
4. Findings table, sortable and filterable, severity as a coloured pill.
5. Method and limits.

Coverage percent is protected and healthy machines divided by all machines in scope. A machine that is protected but unhealthy or stale counts as at risk, not as covered.
