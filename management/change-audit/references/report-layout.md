# Report layout

This skill renders with the shared generator, tools/report_render.py, from a report_data object the scan tool prints, so the report is one pipe and matches the look and feel of every other report in this repository:

```
python tools/change_scan.py | python tools/report_render.py
```

## report_data this skill emits

- title: "Change Audit". subtitle: what changed and whether it preceded a health degradation.
- meta: window is the read window in days, scope is the count of subscriptions scanned, source is "Azure Activity Log".
- summary_cards: total changes, changes linked to a degradation, deletes, failed changes.
- charts: findings by severity, and findings by subscription.
- findings: columns time, resource, change, caller, outcome, note, severity. Each row carries a _band equal to its severity.
- method_notes: the read and correlation windows, and the reminder that correlation is not proof.

## Sections the renderer produces

1. Header with title, window, scope, and generation time.
2. Summary cards led by changes linked to a degradation.
3. Overview charts: by severity and by subscription.
4. Findings table, sortable and filterable, severity as a coloured pill.
5. Method and limits.

The note column is where the value sits: for a linked change it names the degradation it preceded and the time gap, so a reader can judge the link.
