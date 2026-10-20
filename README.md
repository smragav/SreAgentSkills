# Azure SRE Agent Extensions

A collection of skills for the Azure SRE Agent, grouped by the Azure Landing Zone scenario categories that customers ask about (billing and cost, identity and access, resource organization, network, security, management, governance, platform automation), with a flagship Well-Architected review that scores all five pillars in one scorecard. Each skill reviews the resources the agent can read, stays read only, ranks findings by severity or confidence, and produces a single self contained HTML report (inline CSS, CSS bar charts, no external assets). Most also ship an optional custom agent, an optional scheduled sweep, and a rendered sample report.

This repository holds the source. The running artifacts live inside the SRE Agent, authored in the Builder or deployed as code with the shared data plane script.

## Demo dashboard

Two self contained pages at the repository root, both offline capable like the reports themselves:

- [index.html](index.html) walks the whole suite as one story in seven acts, links every rendered sample report, lists all skills in a filterable table, and carries a fifteen minute demo script.
- [capabilities.html](capabilities.html) covers what each skill assesses check by check, which Azure APIs and agent tools it uses, and how it sits next to Azure Advisor, Defender for Cloud, Azure Policy, Service Health, and Cost Management, including where the native tool is the better answer.

## Categories and skills

| Category | Skill | What it does |
| --- | --- | --- |
| [billing-cost](billing-cost) | [finops-cost-optimizer](billing-cost/finops-cost-optimizer) | Ranks spend, detects waste, scores idle resources to terminate. |
| [identity-access](identity-access) | [identity-access-hygiene](identity-access/identity-access-hygiene) | Owner sprawl, overprivileged principals, classic admins, stale assignments. |
| [resource-organization](resource-organization) | [azure-arch](resource-organization/azure-arch) | First pass Azure landing zone design and rough order cost estimate from a VM inventory. |
| | [sql-cmdb-inventory](resource-organization/sql-cmdb-inventory) | SQL estate CMDB inventory across VM, Arc, Managed Instance, and Azure SQL, enriched with Defender counts. |
| | [deprecation-retirement-tracker](resource-organization/deprecation-retirement-tracker) | End of life runtimes, retired tiers, classic resources, old versions. |
| | [quota-limit-watch](resource-organization/quota-limit-watch) | Compute, network, and storage counters close to their quota. |
| [network](network) | [network-exposure-review](network/network-exposure-review) | Internet facing attack surface: open ports, storage and PaaS public access. |
| | [flowlog-firewall-advisor](network/flowlog-firewall-advisor) | What a virtual network actually talks to, as proposed Azure Firewall rules with evidence. |
| [security](security) | [certificate-secret-expiry](security/certificate-secret-expiry) | Certificates, secrets, and credentials ranked by days to expiry. |
| [management](management) | [well-architected-review](management/well-architected-review) | One scorecard scoring all five Well-Architected pillars; the front door to the suite. |
| | [reliability-posture-review](management/reliability-posture-review) | Single points of failure and redundancy gaps, scored by severity. |
| | [observability-coverage-gap](management/observability-coverage-gap) | Resources missing diagnostic settings, alerts, action groups, or a workspace. |
| | [alert-hygiene-review](management/alert-hygiene-review) | Noisy, cry wolf, unacknowledged, and disabled alert rules. |
| | [incident-triage-rca](management/incident-triage-rca) | Gathers health, changes, and neighbours into a timeline for root cause. |
| | [blameless-postmortem-writer](management/blameless-postmortem-writer) | Turns incident facts into a blameless postmortem document. |
| | [recurring-incident-patterns](management/recurring-incident-patterns) | Repeat offenders over time from alerts and resource health degradations. |
| | [change-audit](management/change-audit) | What changed and whether it preceded a health degradation. |
| | [aks-reliability-review](management/aks-reliability-review) | AKS clusters against reliability and operational best practices. |
| | [data-platform-review](management/data-platform-review) | SQL, PostgreSQL, MySQL, and Cosmos DB redundancy and backup posture. |
| | [appservice-containerapps-health](management/appservice-containerapps-health) | App Service and Container Apps scaling, probes, and transport security. |
| [governance](governance) | [tag-governance-compliance](governance/tag-governance-compliance) | Resources against a required tag standard, feeding chargeback, plus the policy scenarios. |
| [platform-automation](platform-automation) | [pre-change-readiness](platform-automation/pre-change-readiness) | Go / no-go readiness (reliability, exposure, capacity) for a target scope. |

The categories follow the Azure Landing Zone design areas used by the customer scenario battery at [alsanch/azure-sre-agent-scenarios](https://github.com/alsanch/azure-sre-agent-scenarios). Every skill carries its scenarios in references/scenarios.md, and [scenario-index.md](scenario-index.md) lists all 77 scenarios with the skill that answers each. Of those, 15 are covered by existing checks, 13 are partly covered, and 49 are new guided prompts that run read only through Azure Resource Graph, Azure Monitor, the Activity Log, or Cost Management without a Python tool behind them yet.

Four skills have no scenario mapped yet and keep their original scope: recurring-incident-patterns, aks-reliability-review, data-platform-review, and appservice-containerapps-health. The Well-Architected pillar scores (reliability, security, cost, operational excellence, performance) still appear inside the well-architected-review scorecard; the folders are organized by scenario category, not by pillar.

Several categories hold the closest existing skill rather than a perfect fit: the Resource Organization scenarios for management groups, subscription hygiene, resource group sprawl, locks, and moving resources sit on azure-arch, the resource age and extension health scenarios sit on sql-cmdb-inventory, and the Defender for Cloud assessment sits on certificate-secret-expiry. A dedicated skill for each is a candidate follow up.

The azure-arch skill is a design and migration generator rather than a read only posture review. It models a target Azure landing zone from a VM inventory and emits a draw.io diagram, an Excel cost workbook, a CSV, and JSON metadata, using the draw.io MCP connector instead of the shared HTML renderer. Both azure-arch and sql-cmdb-inventory mirror their upstream source as flat folders (a SKILL.md, plus generator-template.py for azure-arch), so they skip the tools, optional, and sample-report subfolders the posture reviews use; they only gain a references folder for scenarios.md.

## How a skill is structured

Every skill folder carries the same anatomy, following the cost optimizer that came first:

- SKILL.md: the orchestration playbook, with YAML frontmatter (name, description, and the built in tools it attaches).
- references/: the checks catalog, the scoring or report layout notes, scenarios.md (the customer scenarios routed to the skill, with sample prompts), and other supporting files the skill follows.
- tools/: the Python tools. Each analyzer prints a report_data object as JSON, which pipes straight into the shared renderer. The heavy Azure imports are lazy so the pure logic is unit tested; each tool ships a test_*.py.
- optional/: an optional custom agent (agent.yaml) and an optional scheduled sweep, or a task note for the incident skills.
- sample-report/: a rendered HTML sample of the report the skill produces, so the output can be reviewed without running the skill.

## Shared foundation

The [shared](shared) folder holds what every skill reuses, so the deploy client and the renderer are not copied thirteen times:

- shared/tools/report_render.py: one generic self contained HTML report generator (summary cards, CSS bar charts, a sortable and filterable findings table, and an optional action candidates table with copy buttons).
- shared/references/permissions-and-scope.md: the common Reader scope reference bundled into every skill.
- shared/iac/deploy-skill.ps1: one parameterized data plane deploy script for any skill.

## Deploy

Point the shared script at a skill folder. It reads the name, description, and tools from that skill's SKILL.md frontmatter, bundles the skill's references and tools together with the shared references and shared tools, and PUTs the skill to the agent data plane, the same surface the Builder uses.

```powershell
cd shared/iac
./deploy-skill.ps1 -SubscriptionId <sub> -ResourceGroup <rg> -AgentName <agent> `
  -SkillPath ../../security/certificate-secret-expiry -DryRun
```

Drop -DryRun to deploy. See [shared/iac/README.md](shared/iac/README.md) for details and the reason the data plane is used rather than the control plane. You can also author any skill by hand in the Builder by pasting SKILL.md, uploading the reference files, and creating the Python tools.

## Prerequisites

- An Azure SRE Agent with Builder access.
- The agent's managed identity has its default Reader on the subscriptions and resource groups you want analyzed. A few skills read data planes that need their own read role (Key Vault item metadata, Microsoft Graph for application credentials); each skill treats a denied read as not assessed rather than a failure.
- Azure CLI with an active az login, and the SRE Agent Administrator role on the agent, to deploy as code.

## Design principles

- Read only throughout. Skills propose recommendations and provide operator ready commands, but a human reviews and runs anything that changes or deletes a resource.
- Default Reader scope. Coverage equals the agent's read scope. A skill may ask the user to grant temporary access when a read is denied, but it never assigns roles itself.
- Evidence first. Every finding carries its evidence and a severity or a confidence. Severity reflects blast radius and likelihood, not effort.
- Self contained output. One HTML report per run, styled inline, that opens the same online or offline.
