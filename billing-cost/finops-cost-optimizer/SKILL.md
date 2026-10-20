---
name: finops-cost-optimizer
description: Use when the user asks for a FinOps review, Azure cost optimization, cost savings, reducing spend, rightsizing, idle or forgotten resources, or "where is my Azure money going". Ranks the subscriptions and resource groups the agent can read by spend, detects waste across seven dimensions, enumerates idle and orphaned resources and scores them by confidence to terminate, ranks by savings, and produces a self contained HTML report with copyable delete commands.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# FinOps Cost Optimizer

This skill runs a FinOps cost optimization review across the Azure subscriptions and resource groups this agent is allowed to read. It narrows scope by spend, finds waste across seven dimensions, enumerates idle and orphaned resources and scores each one by confidence to terminate, ranks by savings, and produces a single self contained HTML report as the primary output. It is built to run on demand or as a monthly FinOps report.

## When to use this skill

Use this skill when the user asks to:

- Review or reduce Azure cost, find savings, or run a FinOps assessment.
- Understand where spend is concentrated across subscriptions or resource groups.
- Get cost optimization recommendations beyond raw Azure Advisor output.

## Operating principles

- Read only. This skill never changes or deletes resources. It proposes recommendations and provides operator ready delete commands for termination candidates, but a human reviews and runs them; the agent runs none of them.
- Default Reader scope. It analyzes the subscriptions and resource groups this agent can already read, and starts within that existing access. If a read returns access denied or authorization failed, it may ask the user to grant temporary access to that scope, but it never assigns roles itself. Elevation is always the user granting temporary access out of band. If the user declines, skip that item, record it as not assessed because of insufficient access, and continue with the rest. See references/permissions-and-scope.md.
- Evidence first. Every recommendation carries its evidence, an estimated monthly saving, and a risk rating. Every termination candidate carries its evidence, a lower bound saving, and a confidence to terminate score. Never present a destructive action as the default.

## Workflow

The three Python helpers (tools/cost_rank.py, tools/commitment_recommendations.py, tools/generate_report.py) are bundled with this skill. Run them with the RunInTerminal tool using the Python in the agent runtime, which already has azure-identity and requests. The report generator uses only the Python standard library. They authenticate to Azure with the agent managed identity. Follow these four phases in order.

### Phase 1: Narrow scope by spend

1. Run the helper with RunInTerminal: python tools/cost_rank.py. It queries Azure Cost Management at subscription scope for amortized spend over the last 30 days, groups by resource group, and applies the ranking rules in references/ranking-method.md.
2. It returns the ranked subscriptions, the selected top decile (with a floor so small tenants still return results), and for each selected subscription the ranked resource groups with their own selected top decile.
3. If the helper reports that it used the Consumption fallback, tell the user that cost data came from usage records because the Cost Management query was not available under the current permissions.

### Phase 2: Detect waste and idle resources

Work two passes over the selected scope.

Savings recommendations, across the dimensions in references/checks-catalog.md:

1. Azure Advisor cost baseline.
2. Orphaned resources (also a termination candidate source; see below).
3. Commitment coverage. Run python tools/commitment_recommendations.py --subscriptions <selected ids> with RunInTerminal for reservation and savings plan recommendations.
4. Idle or underused resources, using Azure Monitor metrics over a 30 day window.
5. Storage optimization.
6. Log Analytics optimization.
7. Dev and test scheduling.

Use the RunAzCliReadCommands tool for the read only Azure CLI commands in the catalog. Record a finding with: resource id, dimension, current configuration, proposed change, estimated monthly saving, risk rating, and evidence.

Termination candidates, following references/idle-detection.md: enumerate idle and orphaned resources across every accessible subscription with Azure Resource Graph (az graph query through RunAzCliReadCommands), score each one by confidence to terminate, price it as a lower bound, and record a candidate with its resource details, saving, confidence, reason, next step, and an az delete command. Where Azure Monitor metrics or Activity Logs are not readable, rely on association, age, and naming heuristics only and note the limitation.

### Phase 3: Rank

Score every finding with the priority formula in references/ranking-method.md and sort findings from highest to lowest priority. Sort termination candidates by confidence to terminate, highest first. Spend chose where to look. Savings and confidence decide what to act on first.

### Phase 4: Produce the report

1. Assemble the report_data described in references/report-layout.md, including both the findings and the termination candidates list.
2. Run python tools/generate_report.py with RunInTerminal, passing the assembled report_data as JSON on standard input. It writes a self contained HTML report to /mnt/data and returns the path. If the user wants a shareable link, store the file with the SaveFileToBlob tool.
3. Present the report, then a short inline summary: total analyzed spend, total estimated monthly savings, findings by priority, termination candidates by confidence band, the top three recommendations, the top three termination candidates, and any scopes or dimensions not assessed because of insufficient access.

## Optional follow up

Only if the user asks for it, file tracking issues from the findings using references/issues-optional.md. This is off by default.

## Scenario coverage

This skill also answers 12 customer scenarios in the Billing and Cost category. Open references/scenarios.md when the ask matches one of them: it holds the sample prompt, the run mode, and whether the skill covers it with built in checks or a guided read only prompt.

## Expected output

- Primary: a single self contained HTML report delivered as a file link, covering the FinOps overview, the termination candidates, and the savings recommendations.
- Inline: a short summary with total spend analyzed, total estimated monthly savings, findings by priority, termination candidates by confidence band, and the top recommendations and candidates.
- Every recommendation includes evidence, an estimated monthly saving, and a risk rating. Every termination candidate includes evidence, a lower bound saving, a confidence to terminate score, and a copyable delete command the agent never runs.
