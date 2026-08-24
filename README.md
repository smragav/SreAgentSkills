# Azure SRE Agent Extensions

A collection of skills for the Azure SRE Agent, grouped by pillar, with a flagship Well-Architected review that scores all five pillars in one scorecard. Each skill reviews the resources the agent can read, stays read only, ranks findings by severity or confidence, and produces a single self contained HTML report (inline CSS, CSS bar charts, no external assets). Most also ship an optional custom agent, an optional scheduled sweep, and a rendered sample report.

This repository holds the source. The running artifacts live inside the SRE Agent, authored in the Builder or deployed as code with the shared data plane script.

## Pillars and skills

| Pillar | Skill | What it does |
| --- | --- | --- |
| [well-architected](well-architected) | [well-architected-review](well-architected/well-architected-review) | One scorecard scoring all five Well-Architected pillars; the front door to the suite. |
| [reliability-resilience](reliability-resilience) | [reliability-posture-review](reliability-resilience/reliability-posture-review) | Single points of failure and redundancy gaps, scored by severity. |
| | [quota-limit-watch](reliability-resilience/quota-limit-watch) | Compute, network, and storage counters close to their quota. |
| [observability](observability) | [observability-coverage-gap](observability/observability-coverage-gap) | Resources missing diagnostic settings, alerts, action groups, or a workspace. |
| | [alert-hygiene-review](observability/alert-hygiene-review) | Noisy, cry wolf, unacknowledged, and disabled alert rules. |
| [incident-response](incident-response) | [incident-triage-rca](incident-response/incident-triage-rca) | Gathers health, changes, and neighbours into a timeline for root cause. |
| | [blameless-postmortem-writer](incident-response/blameless-postmortem-writer) | Turns incident facts into a blameless postmortem document. |
| | [recurring-incident-patterns](incident-response/recurring-incident-patterns) | Repeat offenders over time from alerts and resource health degradations. |
| [governance](governance) | [certificate-secret-expiry](governance/certificate-secret-expiry) | Certificates, secrets, and credentials ranked by days to expiry. |
| | [deprecation-retirement-tracker](governance/deprecation-retirement-tracker) | End of life runtimes, retired tiers, classic resources, old versions. |
| | [tag-governance-compliance](governance/tag-governance-compliance) | Resources against a required tag standard, feeding chargeback. |
| | [sql-cmdb-inventory](governance/sql-cmdb-inventory) | SQL estate CMDB inventory across VM, Arc, Managed Instance, and Azure SQL, enriched with Defender counts. |
| [security](security) | [network-exposure-review](security/network-exposure-review) | Internet facing attack surface: open ports, storage and PaaS public access. |
| | [identity-access-hygiene](security/identity-access-hygiene) | Owner sprawl, overprivileged principals, classic admins, stale assignments. |
| | [flowlog-firewall-advisor](security/flowlog-firewall-advisor) | What a virtual network actually talks to, as proposed Azure Firewall rules with evidence. |
| [workload-health](workload-health) | [aks-reliability-review](workload-health/aks-reliability-review) | AKS clusters against reliability and operational best practices. |
| | [data-platform-review](workload-health/data-platform-review) | SQL, PostgreSQL, MySQL, and Cosmos DB redundancy and backup posture. |
| | [appservice-containerapps-health](workload-health/appservice-containerapps-health) | App Service and Container Apps scaling, probes, and transport security. |
| [operational-excellence](operational-excellence) | [change-audit](operational-excellence/change-audit) | What changed and whether it preceded a health degradation. |
| | [pre-change-readiness](operational-excellence/pre-change-readiness) | Go / no-go readiness (reliability, exposure, capacity) for a target scope. |
| [architecture](architecture) | [azure-arch](architecture/azure-arch) | First pass Azure landing zone design and rough order cost estimate from a VM inventory. |
| cost-optimization | [finops-cost-optimizer](finops-cost-optimizer) | Ranks spend, detects waste, scores idle resources to terminate. |

The cost optimizer predates the pillar layout and keeps its own top level folder and deployment script; treat it as the cost optimization pillar.

The architecture pillar's azure-arch skill is a design and migration generator rather than a read only posture review. It models a target Azure landing zone from a VM inventory and emits a draw.io diagram, an Excel cost workbook, a CSV, and JSON metadata, using the draw.io MCP connector instead of the shared HTML renderer. Both azure-arch and the governance sql-cmdb-inventory skill mirror their upstream source as flat folders (a SKILL.md, plus generator-template.py for azure-arch), so they skip the references, tools, optional, and sample-report subfolders the posture reviews use.

## How a skill is structured

Every skill folder carries the same anatomy, following the cost optimizer that came first:

- SKILL.md: the orchestration playbook, with YAML frontmatter (name, description, and the built in tools it attaches).
- references/: the checks catalog, the scoring or report layout notes, and other supporting files the skill follows.
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
  -SkillPath ../../governance/certificate-secret-expiry -DryRun
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
