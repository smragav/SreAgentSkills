# Azure SRE Agent skills

A customer sharable library of **105 Azure SRE Agent skills** across eight categories: billing, identity, resource organization, network, security, management, governance and platform automation.

These skills were created for the scenarios listed in [alsanch/azure-sre-agent-scenarios](https://github.com/alsanch/azure-sre-agent-scenarios) and also cover additional scenarios beyond that list. The initial skills came from Onur Senturk's repository, [onsenturk/SreAgentExtensions](https://github.com/onsenturk/SreAgentExtensions). See the [license notices](./THIRD-PARTY-NOTICES.md).

Each skill has concrete evidence collection steps, analysis rules, scoped permission requirements, output fields, limitations and Microsoft documentation sources. Skills never change customer resources on their own.

**Validation boundary:** local regression tests and bundle checks are not live Azure validation. A scenario can require service access, retained telemetry, host tools, operator inputs or an approved change process that this repository cannot supply automatically.

## Start here

**You can add individual skills to your own existing Azure SRE Agent. You do not need this author's workspace, a new agent or all 105 skills.** You do need permission to customize the target agent and separately approved access to the resources you want it to investigate.

1. [Get the repository and choose a skill](#1-get-the-repository-and-choose-one-skill).
2. [Preview and install the complete skill bundle](#2-preview-the-bundle-without-contacting-azure).
3. [Configure the agent's tools, identity and resource access](#5-configure-runtime-tools-identity-and-access).
4. [Run a small first investigation](#using-an-installed-skill).

Use the deployment script when possible: it includes the shared files that these skills need. Copying only `SKILL.md`, connecting this GitHub repository as knowledge, or downloading one skill folder is not equivalent to installing the complete executable skill.

The examples below use Windows PowerShell and run from this repository's root. Replace every value in angle brackets before running a command. Installation changes the selected agent's skill definition; the investigation examples do not authorize changes to customer resources.

## Browse the library

- [Interactive library](./index.html): search and filter all skills, with analysis rules, limits and sources.
- [Skill index](./scenario-index.md).
- [Machine readable skill catalog](./catalog/skills.json).

The HTML library embeds its data and offers category and search filters. Playbook and example links require the rest of the library, so share the repository or its complete archive when those links are needed.

| Category | Skills |
| --- | ---: |
| Billing and Cost | 13 |
| Identity and Access | 6 |
| Resource Organization | 14 |
| Network | 14 |
| Security | 3 |
| Management | 43 |
| Governance | 9 |
| Platform Automation | 3 |
| **Total** | **105** |

## Skills with a bundled analysis tool

Most skills are evidence workflows: the agent runs the documented read commands, applies the analysis rules and produces a result that follows the skill's output contract. Some skills also bundle a Python tool. These need Python and any listed packages in the agent execution environment, and the identity setup described in [configure runtime tools](#5-configure-runtime-tools-identity-and-access).

| Category | Skills with a bundled tool |
| --- | --- |
| Billing and Cost | `finops-cost-optimizer` |
| Identity and Access | `identity-access-hygiene` |
| Resource Organization | `azure-arch`, `sql-cmdb-inventory`, `deprecation-retirement-tracker`, `quota-limit-watch` |
| Network | `network-exposure-review`, `flowlog-firewall-advisor` |
| Security | `certificate-secret-expiry` |
| Management | `well-architected-review`, `reliability-posture-review`, `observability-coverage-gap`, `alert-hygiene-review`, `incident-triage-rca`, `blameless-postmortem-writer`, `recurring-incident-patterns`, `change-audit`, `aks-reliability-review`, `data-platform-review`, `appservice-containerapps-health` |
| Governance | `tag-governance-compliance` |
| Platform Automation | `pre-change-readiness` |

These tools implement their documented checks only. Related skills provide broader workflows, and a routing entry is not proof that a tool implements every related scenario.

## Skills with a local evidence analyzer

| Scenario | Skill |
| --- | --- |
| SLO and error budget analysis | [`slo-error-budget-analysis`](./management/slo-error-budget-analysis/references/workflow.md) |
| Backup and restore validation | [`backup-restore-validation`](./management/backup-restore-validation/references/workflow.md) |
| Release regression detection | [`release-regression-detection`](./management/release-regression-detection/references/workflow.md) |
| AKS application incident triage | [`aks-application-incident-triage`](./management/aks-application-incident-triage/references/workflow.md) |
| Messaging delivery failure triage | [`messaging-delivery-failure-triage`](./management/messaging-delivery-failure-triage/references/workflow.md) |
| AI inference reliability investigation | [`ai-inference-reliability-investigation`](./management/ai-inference-reliability-investigation/references/workflow.md) |

These six skills use the bundled `tools/operational_analysis.py` with their scenario ID, adapted input and output contract as described in each workflow. Supply the required `--output <new-private-result.json>` to preserve the full evidence result contract. Optional `--sharing-output <new-sharing-draft.json>` produces a redacted draft for customer sharing review, not a replacement for the private evidence contract. Both output paths must be new because the analyzer refuses overwrites. A customer summary JSON is acceptable. The HTML renderer expects a different presentation shape, so adapt results explicitly rather than sending unadapted scenario JSON to it.

Follow the [operational evidence input guide](./shared/references/operational-evidence.md) and the six workflows linked above. Normalize collected evidence locally into the documented scenario JSON shape; raw Azure CLI output is not analyzer input. Supply explicit customer approved thresholds, objectives and observation windows rather than assuming example values are suitable. Each of these skills includes `references/evidence-example.json`, a synthetic fixture for local testing, not customer evidence or approved operational thresholds.

## Safety and scope

1. Confirm the customer tenant, explicit subscription allowlist, resource groups or IDs, and UTC window.
2. Configure the intended managed identity. Production identity errors must not silently fall back to a different principal. Local developer authentication is an explicit choice.
3. Match roles to the evidence source. Azure Reader alone does not supply all log, billing, Key Vault data plane or directory permissions.
4. Keep denied, missing, unsupported and truncated evidence visible. Missing evidence is not zero findings, compliant, healthy or GO.
5. Default to reading evidence and generating local drafts. Moves, renewal, remediation, rollback, scheduling, deployment, support requests and external delivery need separate approval.
6. Enforce permissions and tool authorization in the host. A playbook or general terminal tool does not itself enforce read only behavior.

Some bundled tools enumerate all subscriptions the identity can see. Use them only with an identity restricted to the approved customer scope. Otherwise, use the related skill's explicit scoped commands.

See [permissions](./shared/references/permissions-and-scope.md), [assessment states](./shared/references/assessment-contract.md), and [governance configuration](./shared/references/governance.json).

See [environment settings](./.env.example) for identity mode, lifecycle evidence and report output configuration. Set them in the approved host; the example file is not loaded automatically.

## Customer sharing

- All published examples are synthetic layout demonstrations, not customer assessments.
- The shared renderer creates a sanitized draft by default and preserves the private input object.
- `--include-identifiers` is an explicit option for an approved customer audience; recognized credentials remain redacted.
- Automated redaction is not a release approval. Review free text, diagrams, CSV/JSON, PDFs and attachments.
- No report is automatically sent or uploaded.

Apply the [customer sharing checklist](./shared/references/customer-sharing.md) before delivery.

## Skill anatomy and packaging

```text
category/
  skill-name/
    SKILL.md
    references/
      workflow.md
      output-contract.json
      scenario.json
    tools/                 (when the skill needs its own implementation)
    sample-report/         (optional synthetic demonstration)
shared/
  references/              (permissions, assessment, sharing, governance, license)
  tools/                   (identity, rendering, sharing, evidence validation)
```

The shared deployment script bundles immediate shared and skill `references` and `tools` files, plus skill root files. Skill files override shared files with the same deployed path. Tests, samples, `optional` directories and nested directories are not runtime attachments.

Shared reference links in playbooks resolve in the deployed bundle. In the source tree, the originals are under [shared references](./shared/references/).

## Install a skill in your Azure SRE Agent

### Prerequisites

| Requirement | What to prepare |
| --- | --- |
| An existing Azure SRE Agent | Its tenant ID, subscription ID, resource group and agent resource name. This guide does not create an agent. |
| Permission to customize that agent | Use an account authorized for Builder and skill updates. The deployment client expects SRE Agent Administrator access on the target agent. Azure Owner or Contributor alone does not replace SRE Agent data access roles. See [user roles](https://learn.microsoft.com/azure/sre-agent/user-roles). |
| Local installation tools | PowerShell 5.1 or later, Azure CLI and the complete repository. Git is needed only if cloning instead of downloading an archive. Python is not needed just to install a skill. |
| Runtime capability | The selected skill's tools and dependencies must be available in the agent execution environment. Python skills require Python 3 and any packages named by that skill. Installing the definition does not install packages or configure a connector. |
| Approved investigation scope | Target tenant, subscription allowlist, resource IDs or resource groups, observation window and evidence permissions. The agent's subscription can differ from the subscriptions it investigates. |

### 1. Get the repository and choose one skill

Clone the repository, or download and extract its complete archive:

```powershell
git clone https://github.com/smragav/SreAgentSkills.git sre-agent-skills
Set-Location .\sre-agent-skills
```

If you already have a local copy, open that folder instead. Use the published branch or release containing the skills you want. Check with the repository owner if a listed skill is not in the version you downloaded; local unpublished changes are not included in a GitHub clone.

Open [the interactive library](./index.html) in a browser and choose one scenario. Read that skill's `SKILL.md`, permissions and workflow before installing it.

For this walkthrough, use the SLO and error budget skill:

```powershell
$SkillPath = '.\management\slo-error-budget-analysis'
Test-Path -LiteralPath (Join-Path $SkillPath 'SKILL.md')
```

**Expected:** `True`. If it returns `False`, stop and correct the folder or repository version.

Other examples of valid skill paths:

| Need | `SkillPath` |
| --- | --- |
| Investigate AKS application symptoms | `.\management\aks-application-incident-triage` |
| Compare release cohorts | `.\management\release-regression-detection` |
| Review existing restore drill evidence | `.\management\backup-restore-validation` |
| Investigate Service Bus queue delivery | `.\management\messaging-delivery-failure-triage` |
| Review AI inference reliability | `.\management\ai-inference-reliability-investigation` |
| Assess alert fatigue | `.\management\alert-fatigue-analysis` |

### 2. Preview the bundle without contacting Azure

Set the details of the **agent receiving the skill**, not an application you plan to investigate:

```powershell
$TenantId = '<agent-tenant-id>'
$AgentSubscriptionId = '<subscription-containing-the-agent>'
$AgentResourceGroup = '<resource-group-containing-the-agent>'
$AgentName = '<existing-agent-resource-name>'

$InstallArgs = @{
    SubscriptionId = $AgentSubscriptionId
    ResourceGroup = $AgentResourceGroup
    AgentName = $AgentName
    SkillPath = $SkillPath
}

.\shared\iac\deploy-skill.ps1 @InstallArgs -DryRun
```

**Expected:** output beginning with `[dry-run] skill 'slo-error-budget-analysis'`, followed by its description, tool names and the `additionalFiles` list.

This script's `-DryRun` is local: it does not log in, resolve an agent endpoint or send an Azure request. Inspect the tools and files. The bundle should contain the skill's workflow and output contract, shared assessment and sharing references, and `tools/operational_analysis.py`. It must not contain customer evidence or credentials.

Do not deploy every skill automatically. Begin with one that has a clear owner and test case.

### 3. Sign in and verify the destination

Sign in as the authorized installer:

```powershell
az login --tenant $TenantId
az account set --subscription $AgentSubscriptionId
az account show --query '{tenant:tenantId,subscription:id,name:name}' --output json
```

Verify that the tenant and subscription are the intended destination. Stop if a command fails or the destination is wrong. This is your local installer sign in, not the identity the agent will use later to investigate resources.

Before installation, check **Builder > Skills** for a skill with the same name. The script sends a `PUT` using the `name` from `SKILL.md`: a matching name can update an existing definition. Save the current guidance, tools and supporting files before an intentional update.

### 4. Install the reviewed bundle

Run the following only after approving the destination, skill content and attached tools:

```powershell
.\shared\iac\deploy-skill.ps1 @InstallArgs
```

**Expected:** the script sends the skill definition, reads it back and prints a message beginning with:

```text
Deployed. Skill 'slo-error-budget-analysis' present with ...
```

Then open your Azure SRE Agent and go to **Builder > Skills**:

1. Find `slo-error-budget-analysis`.
2. Check the description and procedural guidance.
3. Confirm that the expected tools and supporting files are present.
4. Resolve any missing or unavailable tool before running the workflow.

The success message confirms that the definition was saved and read back. It does **not** confirm runtime dependencies, data access, successful evidence collection or the investigation result.

The script is this library's deployment client, not a separately documented Microsoft CLI command. It discovers the agent endpoint through ARM and uses the agent data plane. API availability and tenant configuration can vary. If this route is unavailable, use the portal method below or ask your platform administrator; do not bypass permission checks.

### 5. Configure runtime tools, identity and access

Installing a skill and granting resource access are separate tasks:

| Check | What the agent administrator must do |
| --- | --- |
| Attached tools | Compare the skill's `tools` frontmatter with the installed tool attachments. Confirm the selected CLI, terminal, query or connector tools are available. Do not substitute a tool with broader permissions just to make the workflow run. |
| Execution environment | Confirm Python and the skill's required packages exist where the agent executes tools. Tools such as `kubectl` also need their own approved context and permissions. A script attachment is not an installed runtime. |
| Python identity | For this library's managed identity collectors, configure `AZURE_CLIENT_ID` with the approved user assigned identity's **client ID**, not its object ID or Azure resource ID. See [environment settings](./.env.example). Setting it on your laptop does not configure the remote agent runtime. |
| Other identity modes | `SRE_IDENTITY_MODE=developer` is an explicit local development choice, not a production fallback. Use `system-assigned` only on a host that actually provides that identity. Do not replace the SRE Agent's intended identity to avoid an access error. |
| Resource access | Have an authorized administrator grant only the permissions documented by the selected skill at the approved scope. Log, billing, Key Vault, Kubernetes and directory access have separate requirements. The installer script grants none of them. |
| Approval controls | Configure the host's tool authorization and approval behavior. Text saying read only is not an enforcement boundary, especially with a terminal tool. Keep changes and external delivery separately approved. |

Set environment values through the execution host's supported configuration mechanism. This repository does not configure that mechanism or automatically load `.env.example`. If the host cannot expose the approved identity to a Python collector, stop and resolve that prerequisite rather than adding credentials to a skill file.

The local evidence analyzer does not authenticate to Azure. Its evidence collection commands still need the appropriate agent or tool identity and access.

### Portal alternative: add the skill manually

Microsoft documents skill creation in **Builder > Skills**. If you cannot use the deployment script:

1. Open the target agent, navigate to **Builder > Skills**, and create a skill.
2. Use the selected `SKILL.md` file for its name, description and complete procedural guidance. Keep the name consistent with the folder and references.
3. Select the tools listed in that file using the tool picker.
4. Add the supporting files with the same relative paths the deployment dry run lists. Include both the selected skill's files and shared files:

   | Local source | Relative path in the skill |
   | --- | --- |
   | Files directly under `shared\references` | `references/<filename>` |
   | Files directly under `shared\tools`, excluding Python unit tests | `tools/<filename>` |
   | Files directly under the selected skill's `references` | `references/<filename>` |
   | Files directly under the selected skill's `tools`, excluding Python unit tests | `tools/<filename>` |
   | Other files directly under the skill root, excluding `SKILL.md` and Python unit tests | `<filename>` |

5. If a shared file and a skill file have the same relative path, use the skill's version, matching the deployment script.
6. Save the skill and complete the same runtime and first use checks described here.

The supporting file controls can differ by portal version. If your editor cannot preserve the required file paths, use the script with an authorized administrator instead of saving an incomplete skill. This guide does not assume that SRE Agent supports uploading this repository as a ZIP package.

Uploading `SKILL.md` as a knowledge document alone does not attach executable tools or their dependencies.

## Using an installed skill

### First run: use synthetic evidence

For skills with a local evidence analyzer, such as the one below, begin with its bundled `references/evidence-example.json`. In the agent chat, use a prompt such as:

```text
Use the slo-error-budget-analysis skill.
Run its local analyzer against the bundled references/evidence-example.json
and references/output-contract.json.
Choose new output filenames for the private result and sanitized sharing draft.
Do not query Azure, change resources, create a schedule or upload anything.
State clearly that this is synthetic evidence, not a customer assessment.
Show the SLI, remaining error budget, assessment status and limitations.
```

**Expected for this fixture:** SLI `0.995` (99.5%), approximately `50` remaining bad events, an `Observed` finding and `Complete` local assessment coverage. Complete describes the supplied local assessment, not a production health guarantee. The sharing copy must still be labelled as a draft requiring human review.

If you want to verify the analyzer on your own computer before involving the agent, run this from the repository root with Python 3 installed:

```powershell
$TestDir = Join-Path ([System.IO.Path]::GetTempPath()) ('sre-skill-test-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $TestDir | Out-Null

python .\shared\tools\operational_analysis.py `
  --scenario slo-error-budget-analysis `
  --input .\management\slo-error-budget-analysis\references\evidence-example.json `
  --contract .\management\slo-error-budget-analysis\references\output-contract.json `
  --output (Join-Path $TestDir 'private-result.json') `
  --sharing-output (Join-Path $TestDir 'sharing-draft.json')

if ($LASTEXITCODE -ne 0) { throw 'The local synthetic test failed. Read the error before continuing.' }
Write-Output "Synthetic test outputs: $TestDir"
Get-Content -LiteralPath (Join-Path $TestDir 'private-result.json') -Raw
```

This local test needs no Azure login and makes no cloud calls. Output files are written to the displayed temporary directory, not into the repository. It tests the analyzer, not the remote agent installation. The tool refuses to overwrite an existing output file.

### Next run: use a small approved customer scope

Azure SRE Agent selects skills from their descriptions and the question. An explicit `/skill` command is not required; naming the skill and goal makes your intention clear.

Use this prompt as a starting point, replacing every placeholder:

```text
Use the slo-error-budget-analysis skill to assess request success.
Tenant: <approved tenant ID>.
Subscription allowlist: <approved subscription ID>.
Application Insights resource ID: <exact approved resource ID>.
Log Analytics workspace: <approved workspace GUID>.
Observation window: <start UTC> to <end UTC>.
SLO: <customer approved target and event eligibility/success definition>.

First confirm the identity, resource scope, required inputs and permissions.
Use approved read tools only. Do not enumerate unrelated subscriptions.
Collect the evidence and normalize it to the operational evidence contract.
Do not use synthetic data or example thresholds for this assessment.
If evidence is missing, denied or incomplete, report that explicitly.
Produce the private JSON result and a sanitized customer summary draft.
Do not change resources, create schedules, send or upload anything.
```

For the other scenarios, name the relevant skill and supply the inputs in its `SKILL.md`. In particular:

| Scenario | Supply before analysis |
| --- | --- |
| Backup restore | Existing approved drill results, application readiness and integrity evidence, recovery timestamps and customer RTO/RPO targets. Installing this skill does not run a restore. |
| Release comparison | Approved release mapping, comparable cohorts and windows, minimum sample and error/latency thresholds. |
| AKS application triage | Verified cluster context, approved namespace, pod snapshots and events, restart criteria and any separately approved log access. |
| Messaging triage | Exact Service Bus queue, timed depth snapshots, completion evidence and queue thresholds. |
| AI inference | Exact deployment and compatible request/latency evidence, existing evaluation results, quality rubric and customer thresholds. |

For these six skills, the analyzer takes the documented **normalized evidence JSON**, not raw CLI output. Use [the input guide](./shared/references/operational-evidence.md). Missing evidence is not permission to fill fields from examples.

Before wider use, run an authorized test covering one known healthy case, one finding and one denied or missing evidence case. Confirm that missing evidence is never reported as healthy. Review the private evidence and sharing copy separately.

### Use the skill from a custom agent

Skills can be used by the main SRE Agent or by a custom agent. For a custom agent, open **Builder > Agent Canvas** and select the installed skill in **Choose Skills**. If managing custom agent YAML, merge the following into its existing configuration rather than replacing its other settings:

```yaml
allowed_skills:
  - slo-error-budget-analysis
```

The name must match the installed skill. Microsoft documents a maximum of five concurrently active skills; this is not a limit of five installed definitions. Select the skills each agent needs rather than installing or enabling the entire library indiscriminately.

### Update an installed skill safely

1. Save the current installed guidance, tool list and supporting files.
2. Review the newer repository version and its changes.
3. Repeat the dry run for the same skill name and destination.
4. Approve the update, install it, and repeat the synthetic and scoped checks.
5. If necessary, restore the saved version through Builder or redeploy the saved source version. Do not assume reinstalling changes resource permissions, schedules or customer infrastructure.

## Troubleshooting installation and first use

| Symptom | Check and next action |
| --- | --- |
| `No SKILL.md found` or `Test-Path` returns `False` | Run from the repository root. Confirm `SkillPath` and the downloaded branch or release. Keep the complete shared directory. |
| Script is blocked by local policy | Follow your organization's approved PowerShell execution or signing process. Do not disable organization policy to run the script. |
| Login or endpoint discovery fails | Confirm the tenant, agent subscription, resource group and exact agent resource name. Check Azure CLI sign in, ARM read access and network reachability. |
| Install returns `403` | Check your SRE Agent data access role on the target agent. Your installer permissions and the agent's resource access are separate. Do not grant broad resource Contributor to fix a skill authoring failure. |
| Skill is installed but not selected | Check its saved description and name. Ask for the scenario explicitly. If using a custom agent, check its selected skills or `allowed_skills`. |
| A tool, connector, Python package or `kubectl` is unavailable | Configure the approved runtime/tool prerequisite. Installing supporting files does not install software, authorize a connector or grant a Kubernetes context. |
| `references/...` or `tools/...` cannot be found | Recheck the complete bundle and relative paths. Copying only `SKILL.md` or a knowledge document is insufficient. |
| Identity selection or resource reads fail | Verify the remote runtime identity configuration and the selected skill's evidence permissions. Do not paste a token or secret into a skill. Retain the result as Not assessed. |
| JSON input is rejected | Use the scenario's normalized input contract, valid UTC timestamps, approved resource IDs and explicit customer thresholds. Raw CLI output and unresolved placeholders are not valid input. |
| Output already exists | Choose a new private output filename and, if requested, a new sharing draft filename. Do not overwrite original evidence. |
| A report is Partial or Not assessed | Read its limitations and fix only the missing evidence or access prerequisite. These states are valid safety outcomes, not reasons to replace missing values with zero. |

See [the deployment client notes](./shared/iac/README.md) for implementation details. No step in this guide grants permission to run a restore, replay messages, restart a workload, change a model, create a schedule or send a report.

## Validation and regeneration

The existing Python tools require the host's approved `azure-identity` and `requests` packages for live reads. Local classification and contract tests avoid cloud calls. Pytest is required for the test command; the generators and structure validator use the Python standard library.

Tests parse every embedded Python command. Shell syntax validation covers the PowerShell and Azure CLI examples when PowerShell is available. Parsing is not a service execution test.

```powershell
python -m pytest -q
python .\scripts\validate_library.py
```

Maintainers regenerate the scenario skills and catalogs from the reviewed definitions in [catalog](./catalog/):

```powershell
python .\scripts\build_scenario_skills.py
python .\scripts\build_catalog.py
python .\scripts\validate_library.py
```

The catalog generator also updates routing and common references in the skills that bundle tools, and replaces sample reports with synthetic demonstrations. It does not modify their analyzer tools. Review diffs to preserve deliberate manual changes.

Library checks cover 105 skill names, descriptions and tool allowlists, deployed references, 83 scenario workflows and **249 synthetic evidence fixtures** (three states per scenario workflow). Catalog checks confirm routing in both HTML pages and the skill index. Tests additionally reject false completeness and missing evidence. They do not execute every CLI query against Azure.

Before operational use, perform an authorized smoke test of the selected skills with the configured identity, complete pagination, a known healthy case, a finding and an access denial. Record the live API and telemetry prerequisites and any unassessed checks.

## Attribution and sources

- [License notices](./THIRD-PARTY-NOTICES.md).
- [Azure SRE Agent skills](https://learn.microsoft.com/azure/sre-agent/skills).
- [Azure SRE Agent permissions](https://learn.microsoft.com/azure/sre-agent/permissions).
- [Azure SRE Agent user roles](https://learn.microsoft.com/azure/sre-agent/user-roles).
- [Azure Well-Architected Framework](https://learn.microsoft.com/azure/well-architected/what-is-well-architected-framework).
- Service specific Microsoft sources are linked in each workflow and checks catalog.

**Verification:** portal skill creation, automatic selection, custom agent skill assignment, the concurrent skill limit and the distinction between user roles and agent permissions were verified against Microsoft Learn on 2026-10-21. Script parameters, bundling, dry run behavior and installation messages were checked against [the deployment client](./shared/iac/deploy-skill.ps1). End to end installation in a customer tenant is not established by these documentation checks.
