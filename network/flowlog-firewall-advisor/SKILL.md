---
name: flowlog-firewall-advisor
description: Use when the user asks what firewall rules a virtual network needs, wants to move a VNet behind Azure Firewall, asks what traffic to allow, mentions deriving rules from flow logs, asks about egress from a VNet, lateral movement between subnets, or wants to know what is actually talking to what. Reads VNet flow logs through Traffic Analytics, reconstructs the connections that really occurred, and produces a severity ranked review report with proposed Azure Firewall network rules and the evidence behind each one.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# Flow Log Firewall Advisor

This skill answers the question that blocks every firewall rollout: what traffic
does this virtual network actually carry. It reads the VNet flow logs the platform
already collects, reconstructs the connections that occurred, ranks them by the risk
they represent, and proposes Azure Firewall network rules with the evidence attached
to each one. It runs on demand before a migration or a policy change, or as a
scheduled review of egress and lateral movement.

## When to use this skill

Use this skill when the user asks to:

- Work out what firewall rules a virtual network or subnet needs.
- Review what a workload is talking to, inside the virtual network or out to the internet.
- Prepare to put a virtual network behind Azure Firewall, or tighten an existing policy.
- Understand egress to public addresses, or lateral movement between subnets.
- See which connections are being blocked today and by which rule.

Do not use this skill to review network security group configuration in the
abstract. That is `network-exposure-review`, which reads the rules as configured.
This skill reads the traffic that actually flowed.

## Operating principles

- **Read only.** This skill reads flow log data. It never creates, changes or deletes
  a rule, a policy, or a firewall. Proposed rules are text for a human to review.
- **Default Reader scope.** It reads across the subscriptions this agent can read,
  plus the Log Analytics workspaces receiving flow logs. A denied read is recorded
  as not assessed rather than treated as a failure. See
  `references/permissions-and-scope.md`.
- **Evidence first.** Every proposed rule carries the flow count, the byte volume,
  and when the traffic was first and last seen. A rule with no evidence is not a rule.
- **Never widen silently.** Traffic that is blocked today stays blocked. Any place the
  analysis broadens observed hosts into a subnet is listed explicitly rather than
  folded quietly into a rule.

## Workflow

The analyzer (`tools/flowlog_firewall_advisor.py`) and the shared renderer
(`tools/report_render.py`) are bundled with this skill. Run them with RunInTerminal
using the Python in the agent runtime. Both authenticate with the agent managed
identity.

An agent can carry both a system assigned and a user assigned identity, and usually
only one of them holds the roles. The tool resolves this itself: it reads the agent
resource named in its own token and authenticates as the user assigned identity
attached to it. `--client-id <clientId>` overrides that, and
`python tools/flowlog_firewall_advisor.py --whoami` prints the principal each
audience resolves to when a read is refused or discovery comes back empty.

### Phase 1: Find the flow logs

1. Run `python tools/flowlog_firewall_advisor.py --discover` with RunInTerminal. It
   queries Azure Resource Graph for Network Watcher flow log resources, keeps the
   ones targeting a virtual network with Traffic Analytics enabled, and groups them
   by the workspace they publish to.
2. If nothing is found, do not conclude there are no flow logs yet. An identity that
   can read nothing gets an empty Resource Graph result rather than an error, so run
   `--whoami` first and confirm the identity is the one holding the roles. Only once
   the identity is right, report the empty result. Flow logs written only to a storage
   account do not populate `NTANetAnalytics`. Say so plainly rather than reporting an
   empty result as a clean bill of health, and offer the two ways forward: enable
   Traffic Analytics, or point the skill at the storage account.
3. If more than one workspace is found, use the one with the most enabled flow logs
   unless the user named a scope.

### Phase 2: Check the window is real

1. Run `python tools/flowlog_firewall_advisor.py --coverage --workspace <guid>`. It
   reports how far back the workspace genuinely holds data and how fresh the newest
   record is.
2. **Do not skip this.** Asking for 30 days from a workspace holding 6 is the most
   common way to build a rule set from a fraction of the traffic, and the result
   looks complete. If the window is narrowed, say so in the summary.
3. If the newest record is more than a few hours old, ingestion has probably stopped.
   Report that as a finding, not a footnote: rules derived from stale data will be
   missing whatever changed since.

### Phase 3: Analyse and report

1. Run the analysis and pipe it into the renderer:
   `python tools/flowlog_firewall_advisor.py --workspace <guid> --days <n> | python tools/report_render.py`
   with RunInTerminal. It writes the self contained HTML report and returns the path.
   Store it with SaveFileToBlob for a link.
2. Present the report, then a short inline summary: the highest severity findings,
   how much of the policy budget the proposed rules consume, anything blocked today
   that a naive reading would have allowed, and any scope not assessed.

## How findings are ranked

Severity reflects blast radius, not effort. The full catalog is in
`references/checks-catalog.md`. In short:

| Severity | What it means |
|---|---|
| Critical | Management ports reachable across a trust boundary, or a source set so broad the rule is effectively any to any |
| High | Egress to public addresses with no service tag, so the rule pins IP literals that churn |
| Medium | Broad east-west reach, or an address group widened from observed hosts to a whole subnet |
| Low | Ordinary service traffic on a well known port between two known endpoints |
| Info | Platform traffic excluded from the rules, and connections already blocked today |

## Scenario coverage

This skill also answers 7 customer scenarios in the Network category (topology, firewall rules and logs, DNS and VPN troubleshooting, peering, ExpressRoute and VPN gateway health, DNS zone hygiene). Open references/scenarios.md when the ask matches one of them: it holds the sample prompt, the run mode, and whether the skill covers it with built in checks or a guided read only prompt.

## Expected output

- **Primary:** a self contained HTML report covering coverage and completeness, traffic
  by category, egress to public addresses, connections blocked today, the proposed rule
  set, and every place an address group was widened.
- **Inline:** the highest severity findings, the policy budget consumed, and the count
  of connections excluded because they are already blocked.
- Every proposed rule names its sources, destinations, ports, and the evidence behind
  it. Nothing is changed. The rules are a proposal for a human to review.

## What this skill will not tell you

State these limits whenever presenting results. They are the difference between a
useful proposal and a false sense of safety.

- **Traffic that did not happen during the window is missing.** A month end job will
  not appear in a one week capture and will break when the policy is enforced. Always
  report the window alongside the rules.
- **Network rules only.** Application rules need fully qualified domain names, which
  cannot be derived from IP flow logs. Egress to software as a service appears as IP
  literals unless Traffic Analytics resolved a service tag.
- **Flow logs record what happened, not what should be allowed.** Recommend deploying
  any derived rule set in a non enforcing mode alongside the existing policy first.
