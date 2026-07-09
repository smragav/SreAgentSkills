# Optional scheduled task: weekly backup coverage sweep

Create this in Scheduled tasks. Backup coverage drifts as new machines appear, so a weekly cadence catches gaps early.

- Name: Weekly backup coverage sweep
- Schedule: weekly, for example every Monday at 07:00.
- Response agent: the backup_recovery_coverage custom agent, or the main agent.
- Autonomy: Review.

## Task instructions

Run a backup coverage review across the subscriptions this agent can read.

1. Use the backup-recovery-coverage skill.
2. Run backup_coverage.py to match virtual machines against Azure Backup protected items and classify each machine, then spot check the data services in the checks catalog.
3. Produce the self contained HTML report and post the file link with a short summary: coverage percent, unprotected count, at risk count, and the top subscriptions by gap.
4. If a previous run exists in memory, add a short note on how coverage percent and the unprotected count changed, and call out any newly unprotected machines.

Do not enable or trigger any backup. Provide recommendations only, for a human to apply.
