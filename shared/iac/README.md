# Shared deployment

One parameterized data plane deploy script for every pillar skill, so the deploy client is not copied into each skill folder. See the repository README for the pillar layout, and the SRE Agent deployment notes for why the data plane is used rather than the control plane.

## What deploy-skill.ps1 does

Point it at a skill folder. It reads the name, description, and tools from that skill's SKILL.md frontmatter, bundles the skill's own references and tools together with the shared references and shared tools (report_render.py), and PUTs the skill to the agent data plane endpoint, the same surface the portal Builder uses.

Files are bundled as additionalFiles with these relative paths, so the skill runs the same way it reads locally:

- references/ from shared/references and the skill's references (the skill's file wins on a name clash).
- tools/ from shared/tools and the skill's tools. Unit test files (test_*.py) are skipped.

## Prerequisites

- Azure CLI with an active `az login`.
- Builder access on the target agent (the SRE Agent Administrator role). The agent must already exist.

## Usage

Dry run first to see exactly what would be sent:

```powershell
cd shared/iac
./deploy-skill.ps1 -SubscriptionId <sub> -ResourceGroup rg-sre-agent -AgentName sreagent2 `
  -SkillPath ../../governance/certificate-secret-expiry -DryRun
```

Then deploy:

```powershell
./deploy-skill.ps1 -SubscriptionId <sub> -ResourceGroup rg-sre-agent -AgentName sreagent2 `
  -SkillPath ../../governance/certificate-secret-expiry
```

`-SkillPath` is any pillar skill folder that contains a SKILL.md, for example:

- ../../reliability-resilience/reliability-posture-review
- ../../observability/observability-coverage-gap
- ../../incident-response/incident-triage-rca
- ../../workload-health/aks-reliability-review

## Notes

- The control plane sub-resource API (Microsoft.App/agents/skills) is restricted to internal tenants in preview, so this script uses the data plane with a bearer token for the https://azuresre.dev audience.
- Windows PowerShell 5.1 ConvertTo-Json is pathologically slow on large string payloads, so the script builds the JSON body with an explicit string escaper. PowerShell 7 also works.
- The tools authenticate with the agent managed identity at run time. Enable managed identity with the ARM scope on each Python tool in the Builder Identity tab, and pin AZURE_CLIENT_ID when the agent carries more than one identity.
