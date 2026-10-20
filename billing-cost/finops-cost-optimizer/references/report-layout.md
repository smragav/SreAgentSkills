# Report layout

The generate_report tool builds one self contained HTML file with no external assets and no CDN. All styling is inline CSS and every chart is drawn with plain HTML and CSS bars, so the report opens fully styled offline. It writes the file to the file store. Pass it the data below.

## Sections

1. Header: title, generation date, the analysis window (30 days), the scope, and the cost source (CostManagement or the Consumption fallback).
2. Summary cards: analyzed spend, estimated monthly savings, savings as a percent of spend, the termination candidate count, and the recommendation count.
3. FinOps overview: spend by subscription, spend by resource group, and estimated monthly savings by dimension, each as horizontal CSS bars with the value labelled.
4. Termination candidates: candidate summary cards by confidence band, a top candidates chart, a how to read the confidence score panel, and a filterable table. The table filters by subscription, confidence band, and free text, and every row carries a copyable az delete command. Rendered only when candidates are present.
5. Savings recommendations: every finding sorted by priority score, with resource, dimension, current, proposed, monthly saving, risk, and priority band. Sortable and filterable.
6. Method and limits: how spend, savings, and confidence are used, and any heuristic only note when metrics or Activity Logs were not readable.

## Input shape for generate_report

Pass a report_data object with:

- generated_for: a label for the scope, for example the tenant or agent name.
- window_days and data_source.
- totals: analyzed_spend, estimated_monthly_savings, currency.
- subscriptions: a list of objects with name and cost for the selected subscriptions.
- resource_groups: a list of objects with name and cost for the top resource groups.
- savings_by_dimension: a mapping of dimension name to estimated monthly saving.
- findings: a list, each with resource, dimension, current, proposed, monthly_saving, risk, priority_score, and priority_band.
- candidates: the termination candidates, each with resource, resource_type, resource_id, subscription, subscription_id, resource_group, location, monthly_saving, saving_note, confidence, band, reason, next_step, delete_command, and optionally excluded and exclusion_reason. See references/idle-detection.md. The report derives the band from confidence if band is omitted, and builds the delete command from resource_id if delete_command is omitted.

## Accessibility

- Use clear band colours with a text label next to every colour, so meaning never depends on colour alone.
- Give every chart bar a visible numeric value.
- Keep the underlying numbers in the tables next to the charts.
- Keep text and background contrast at WCAG AA or better.

## Styling and interactivity

- The report is fully self contained: inline CSS, CSS bar charts, and a small block of embedded JavaScript with no external library. It renders the same online or offline.
- The termination candidates table filters by subscription, confidence band, and free text, and each delete command has a copy button.
- The savings recommendations table is sortable (click a column header to toggle ascending or descending) and filterable (type in the box above the table).
