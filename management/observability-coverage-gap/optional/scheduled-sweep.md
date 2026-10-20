# Optional scheduled task: monthly observability coverage sweep

Create this in Scheduled tasks. New resources arrive without monitoring wiring, so a monthly sweep keeps coverage from drifting.

- Name: Monthly observability coverage sweep
- Schedule: monthly, for example the first business day at 08:30.
- Response agent: the observability_coverage_gap custom agent, or the main agent.
- Autonomy: Review.

## Task instructions

Run an observability coverage review across the subscriptions this agent can read.

1. Use the observability-coverage-gap skill.
2. Run observability_gap.py to map diagnostic settings, metric alert coverage, action groups, and workspaces, then verify anything not answerable in bulk.
3. Produce the self contained HTML report and post the file link with a short summary: resources with gaps, blind resources with no diagnostic settings, subscriptions with no action group, and the top gaps by subscription.
4. If a previous run exists in memory, add a short note on newly blind resources since the last sweep.

Do not create any monitoring wiring. Provide recommendations only, for a human to apply.
