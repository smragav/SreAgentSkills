# Optional scheduled task: weekly expiry sweep

Create this in Scheduled tasks. This is the highest value cadence in the set: a weekly sweep with a 60 day horizon gives ample lead time to renew before anything expires.

- Name: Weekly certificate and secret expiry sweep
- Schedule: weekly, for example every Monday at 06:30.
- Response agent: the certificate_secret_expiry custom agent, or the main agent.
- Autonomy: Review.

## Task instructions

Run a certificate and secret expiry review across what this agent can read.

1. Use the certificate-secret-expiry skill.
2. Run expiry_scan.py with a 60 day horizon to enumerate App Service certificates, Key Vault certificates and secrets, and application credentials, and compute days to expiry. Record any source that denies the read as not assessed.
3. Produce the self contained HTML report and post the file link with a short summary: expired items, items expiring within 14 days, the soonest five with their dates, and any source not assessed.
4. If a previous run exists in memory, call out anything that newly entered the 14 day window since the last sweep.

Do not renew or rotate anything. Provide renewal recommendations only, for a human to act on. Raise the horizon argument ahead of a known renewal season for more lead time.
