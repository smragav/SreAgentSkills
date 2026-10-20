# Scenario coverage for certificate-secret-expiry

Category: Security. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| SSL/TLS certificate expiration tracking | Covered | Scheduled | Daily | High |
| Certificate renewal automation | Added | Scheduled | Daily | High |
| Defender for Cloud assessment | Added | Scheduled | Weekly | High |

## SSL/TLS certificate expiration tracking

Status: Covered. Source category: Network Topology And Connectivity.

Tracks certificates across Azure services to prevent outages caused by expired certificates.

Sample prompt:

> Scan all certificates in: Key Vaults, App Service certificates, Application Gateway SSL certs, Front Door custom domains, and API Management. Show certificate subject, issuer, expiration date, and days remaining. Alert on any certificate expiring within 30 days.

Mode: Scheduled. Frequency: Daily. Time saved: High.

## Certificate renewal automation

Status: Added. Source category: Security.

Monitors certificate expiration in Key Vault and triggers renewal workflows before expiry causes outages.

Sample prompt:

> Check all certificates in Key Vault accounts across subscriptions. For each: show subject, issuer, expiration date, auto-renewal status, and days remaining. For certificates expiring in < 30 days without auto-renewal: trigger renewal workflow or alert the certificate owner. Show certificates that failed auto-renewal attempts.

Mode: Scheduled. Frequency: Daily. Time saved: High.

## Defender for Cloud assessment

Status: Added. Source category: Security.

Provides a security posture snapshot from Defender for Cloud, highlighting critical findings and score trends.

Sample prompt:

> Pull Defender for Cloud assessment for all subscriptions: (1) secure score current and 30-day trend, (2) unhealthy resources by severity (high/medium/low), (3) top 10 recommendations by impacted resource count, (4) new recommendations in last 7 days. Prioritize by exploitability and blast radius.

Mode: Scheduled. Frequency: Weekly. Time saved: High.
