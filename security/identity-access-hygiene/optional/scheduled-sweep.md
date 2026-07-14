# Optional scheduled task: monthly access hygiene sweep

Create this in Scheduled tasks. Access drifts as people and workloads change, so a monthly review keeps least privilege honest and feeds your access reviews.

- Name: Monthly identity and access hygiene sweep
- Schedule: monthly, for example the first business day at 08:00.
- Response agent: the identity_access_hygiene custom agent, or the main agent.
- Autonomy: Review.

## Task instructions

Run an identity and access hygiene review across the subscriptions this agent can read.

1. Use the identity-access-hygiene skill.
2. Run identity_access.py to read role assignments and classic administrators, keep the privileged roles, and classify each finding.
3. Produce the self contained HTML report and post the file link with a short summary: Owner sprawl, high privilege service principals, classic administrators, and stale assignments.
4. If a previous run exists in memory, call out newly added privileged access since the last sweep.

Do not grant, change, or remove any access. Provide recommendations only, for a human to apply, ideally with just in time access through Privileged Identity Management.
