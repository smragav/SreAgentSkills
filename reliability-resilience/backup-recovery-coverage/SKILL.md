---
name: backup-recovery-coverage
description: Use when the user asks about backup coverage, backup gaps, "is everything backed up", recovery readiness, Recovery Services vault protection, or unprotected virtual machines. Cross references the virtual machines the agent can read against Azure Backup protected items, flags machines with no protection and machines whose backups are stale or unhealthy, and produces a self contained HTML backup coverage report.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# Backup and Recovery Coverage

This skill measures how well the workloads this agent can read are protected by Azure Backup. It cross references virtual machines against the Recovery Services and Backup vault protected items, flags machines with no protection and machines whose last backup is stale or unhealthy, and produces a single self contained HTML coverage report. It finds the "we thought it was backed up" gap before a restore is needed. It runs on demand or as a scheduled sweep.

## When to use this skill

Use this skill when the user asks to:

- Check backup coverage or find unprotected resources.
- Confirm recovery readiness before a change window or an audit.
- Find backups that are failing or have not run recently.

## Operating principles

- Read only. This skill never enables, changes, or triggers a backup. It reports coverage and recommends what to protect; a human configures it.
- Default Reader scope. It reads virtual machine inventory and Azure Backup protected items across the subscriptions this agent can read. If a read is denied, it records the scope as not assessed and continues. See references/permissions-and-scope.md.
- Evidence first. Every finding carries the resource id, the backup state (unprotected, unhealthy, or stale), the last backup time where known, and the recommended action.

## Workflow

The scan tool (tools/backup_coverage.py) and the shared report renderer (tools/report_render.py) are bundled with this skill. Run them with the RunInTerminal tool using the Python in the agent runtime. Both authenticate with the agent managed identity.

### Phase 1: Measure coverage

1. Run python tools/backup_coverage.py with RunInTerminal. It enumerates virtual machines and Azure Backup protected items with Azure Resource Graph, matches them by resource id, and prints a ready to render report_data object as JSON.
2. It classifies each machine as protected and healthy, unprotected, unhealthy, or stale (last backup older than the staleness window, three days by default), following references/checks-catalog.md.

### Phase 2: Cover the data services Resource Graph cannot answer alone

Azure SQL, Azure Files, and Cosmos DB protect differently (long term retention policies, share snapshots, continuous backup). Use the read only commands in references/checks-catalog.md to spot check these, and record any gaps as findings. Treat a denied read as not assessed.

### Phase 3: Produce the report

1. Pipe the scan into the renderer: python tools/backup_coverage.py | python tools/report_render.py with RunInTerminal. It writes the self contained HTML report and returns the path. Store it with SaveFileToBlob if the user wants a link.
2. Present the report, then a short inline summary: coverage percent, unprotected count, at risk count (unhealthy or stale), the top subscriptions by gap, and any scope not assessed.

## Expected output

- Primary: a self contained HTML backup coverage report, covering coverage percent, backup state by resource, and the finding table with the recommended action per machine.
- Inline: coverage percent, unprotected and at risk counts, and the top gaps.
- Every finding carries the resource id, the backup state, the last backup time where known, and the recommended action. Nothing is enabled or triggered; recommendations are for a human to apply.
