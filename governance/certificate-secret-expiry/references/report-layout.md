# Report layout

This skill renders with the shared generator, tools/report_render.py, from a report_data object the scan tool prints, so the report is one pipe:

```
python tools/expiry_scan.py | python tools/report_render.py
```

## report_data this skill emits

- title: "Certificate and Secret Expiry". subtitle: certificates, secrets, and credentials by days to expiry.
- meta: window is the horizon in days, scope is the count of subscriptions scanned, source is "Key Vault, App Service, Graph".
- summary_cards: expiring within the horizon, already expired, certificates, secrets and credentials.
- charts: items by severity, and items by time bucket (Expired, within 14 days, 15 to 30 days, 31 days to horizon).
- findings: columns item, kind, source, subscription, expires, days_left, recommendation, severity. Rows are sorted soonest first, and each carries a _band equal to its severity and a numeric sort hint on days_left.
- method_notes: the horizon used, any source not assessed (a vault or Graph that denied the read), and the note that embedded gateway certificates are not enumerated.

## Sections the renderer produces

1. Header with title, horizon, scope, and generation time.
2. Summary cards led by expired and expiring counts.
3. Overview charts: by severity and by time bucket.
4. Findings table, sortable and filterable, sorted soonest first, severity as a coloured pill.
5. Method and limits.

Days remaining drives everything: the sort, the severity, and the time buckets. A negative value means already expired.
