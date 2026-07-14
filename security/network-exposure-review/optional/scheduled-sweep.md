# Optional scheduled task: weekly network exposure sweep

Create this in Scheduled tasks. Exposure creeps in as rules and resources change, so a weekly sweep keeps the attack surface visible.

- Name: Weekly network exposure sweep
- Schedule: weekly, for example every Monday at 06:00.
- Response agent: the network_exposure_review custom agent, or the main agent.
- Autonomy: Review.

## Task instructions

Run a network exposure review across the subscriptions this agent can read.

1. Use the network-exposure-review skill.
2. Run network_exposure.py to find NSG rules open to the internet, storage with public or anonymous access, and PaaS with public network access.
3. Produce the self contained HTML report and post the file link with a short summary: critical exposures, resources with public access, and the top items to close first.
4. If a previous run exists in memory, call out any newly opened management or database port since the last sweep.

Do not change any rule or access setting. Provide recommendations only, for a human to apply.
