# Report layout

This skill renders with the shared generator, tools/report_render.py, from a report_data object the scan tool prints, so the report is one pipe and matches the look and feel of every other report in this repository:

```
python tools/network_exposure.py | python tools/report_render.py
```

## report_data this skill emits

- title: "Network Exposure Review". subtitle: internet facing attack surface.
- meta: window is "Point in time", scope is the count of subscriptions scanned, source is "Azure Resource Graph".
- summary_cards: exposed resources, critical exposures, resources with public access, subscriptions scanned.
- charts: findings by severity, and findings by exposure type (open ports, storage public access, PaaS public access).
- findings: columns resource, exposure, subscription, resource_group, detail, recommendation, severity. Each row carries a _band equal to its severity.
- method_notes: the internet source definition, and any scope not assessed.

## Sections the renderer produces

1. Header with title, scope, source, and generation time.
2. Summary cards led by critical exposures.
3. Overview charts: by severity and by exposure type.
4. Findings table, sortable and filterable, severity as a coloured pill.
5. Method and limits.

Severity leads: management or all ports open to the internet are Critical, database ports and anonymous blob access are High, and other open ports or public network access are Medium.
