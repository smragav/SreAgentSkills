---
name: aks-reliability-review
description: Use when the user asks for an AKS review, Kubernetes cluster reliability, AKS best practices, cluster resilience, or an AKS health check. Reviews the AKS clusters the agent can read for version currency, node pool resilience, control plane exposure, upgrade and monitoring configuration, and identity and tier settings, scores each finding by severity, and produces a self contained HTML AKS reliability report.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# AKS Reliability Review

This skill reviews the Azure Kubernetes Service clusters this agent can read against reliability and operational best practices. It checks version currency, node pool resilience, control plane exposure, auto upgrade and monitoring, and identity and tier settings, scores each finding by severity, and produces a single self contained HTML report. AKS carries a lot of production weight, and a handful of configuration choices decide whether a cluster rides through a zone loss, an upgrade, or a node failure. It runs on demand or as a scheduled sweep.

## When to use this skill

Use this skill when the user asks to:

- Review AKS or Kubernetes cluster reliability, resilience, or best practices.
- Check clusters before a launch, an upgrade, or an audit.
- Find the riskiest cluster configuration across the estate.

## Operating principles

- Read only. This skill reads cluster configuration. It never upgrades, scales, or reconfigures a cluster; it recommends the change.
- Default Reader scope. It reads the managed cluster configuration across the subscriptions this agent can read. If a read is denied, it records the scope as not assessed and continues. See references/permissions-and-scope.md.
- Evidence first. Every finding names the cluster, the setting that fired, a severity, and the recommended change.

## Workflow

The scan tool (tools/aks_review.py) and the shared report renderer (tools/report_render.py) are bundled with this skill. Run them with RunInTerminal using the Python in the agent runtime. Both authenticate with the agent managed identity.

### Phase 1: Review the clusters

1. Run python tools/aks_review.py with RunInTerminal. It reads the managed cluster configuration with Azure Resource Graph, evaluates each cluster against the checks in references/checks-catalog.md, assigns a severity per finding, and prints a report_data object as JSON.
2. For a cluster that needs a closer look, pull the node pool and upgrade detail by hand with the commands in the checks catalog.

### Phase 2: Produce the report

1. Pipe the scan into the renderer: python tools/aks_review.py | python tools/report_render.py with RunInTerminal. It writes the self contained HTML report and returns the path. Store it with SaveFileToBlob for a link.
2. Present the report, then a short inline summary: clusters reviewed, clusters with High findings, the most common gap, and the top clusters to address.

## Expected output

- Primary: a self contained HTML AKS reliability report, covering findings by severity and by subscription, and the full table naming the setting and the recommended change per cluster.
- Inline: clusters reviewed, clusters with High findings, and the top issues.
- Every finding names the cluster, the setting, a severity, and the recommended change. Nothing is reconfigured; recommendations are for a human to apply.
