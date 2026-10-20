---
name: appservice-containerapps-health
description: Use when the user asks about App Service or Web App health, Container Apps health, web tier reliability, scaling and health probes, Always On, HTTPS and TLS enforcement, or a web workload best practices check. Reviews the App Service sites and plans and the Container Apps the agent can read for scaling, health probes, transport security, and plan tier, scores each finding by severity, and produces a self contained HTML web tier health report.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# App Service and Container Apps Health

This skill reviews the web tier this agent can read: App Service sites and plans, and Azure Container Apps. It checks scaling and health probes, transport security (HTTPS and minimum TLS), Always On, and plan tier, scores each finding by severity, and produces a single self contained HTML report. The web tier is usually the front door, so a few settings decide whether it scales under load, fails a probe cleanly, and refuses insecure traffic. It runs on demand or as a scheduled sweep.

## When to use this skill

Use this skill when the user asks to:

- Review App Service, Web App, or Container Apps health and best practices.
- Check scaling, health probes, or transport security on the web tier.
- Prepare a web workload for a launch or a load event.

## Operating principles

- Read only. This skill reads configuration. It never scales, restarts, or reconfigures a site or an app; it recommends the change.
- Default Reader scope. It reads configuration across the subscriptions this agent can read. If a read is denied, it records the scope as not assessed and continues. See references/permissions-and-scope.md.
- Evidence first, and light on false positives. It flags a setting only when the configuration clearly shows the gap, and skips a check when the needed field is not present rather than guessing.

## Workflow

The scan tool (tools/appservice_review.py) and the shared report renderer (tools/report_render.py) are bundled with this skill. Run them with RunInTerminal using the Python in the agent runtime. Both authenticate with the agent managed identity.

### Phase 1: Review the web tier

1. Run python tools/appservice_review.py with RunInTerminal. It reads App Service sites and plans and Container Apps with Azure Resource Graph, evaluates each against the checks in references/checks-catalog.md, assigns a severity per finding, and prints a report_data object as JSON.
2. For a site that needs a closer look at its configuration, pull the detail by hand with the commands in the checks catalog.

### Phase 2: Produce the report

1. Pipe the scan into the renderer: python tools/appservice_review.py | python tools/report_render.py with RunInTerminal. It writes the self contained HTML report and returns the path. Store it with SaveFileToBlob for a link.
2. Present the report, then a short inline summary: sites and apps reviewed, those with High findings, the most common gap, and the top items to address.

## Expected output

- Primary: a self contained HTML web tier health report, covering findings by severity and by category, and the full table naming the setting and the recommended change per site or app.
- Inline: sites and apps reviewed, those with High findings, and the top issues.
- Every finding names the resource, the category, the setting, a severity, and the recommended change. Nothing is reconfigured; recommendations are for a human to apply.
