# Report layout

This skill renders with the shared generator, tools/report_render.py, from a report_data object the scan tool prints, so the report is one pipe:

```
python tools/tag_compliance.py | python tools/report_render.py
```

## report_data this skill emits

- title: "Tag Governance Compliance". subtitle: resources against the required tag standard.
- meta: window is the required tags list, scope is the count of subscriptions scanned, source is "Azure Resource Graph".
- summary_cards: compliance percent, non compliant resources, resources missing an owner, resources scanned.
- charts: missing by tag (one bar per required tag), and non compliance by subscription.
- findings: columns resource, resource_type, subscription, resource_group, missing_tags, recommendation, severity. Each row carries a _band equal to its severity.
- method_notes: the required tags used, the tolerant matching rule, and the recommendation to enforce with Azure Policy.

## Sections the renderer produces

1. Header with title, the required tags, scope, and generation time.
2. Summary cards led by compliance percent.
3. Overview charts: missing by tag and by subscription.
4. Findings table, sortable and filterable, severity as a coloured pill.
5. Method and limits.

Compliance percent is resources with every required tag present, divided by all resources in scope. A missing owner tag is the most serious gap because it removes accountability.
