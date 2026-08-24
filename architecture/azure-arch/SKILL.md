---
name: azure-arch
description: |
  Build a first-pass Azure landing-zone architecture and cost estimate from a VM inventory workbook.
  Use this skill when the user wants a draw.io architecture, Azure stencil diagram, landing-zone recommendation,
  migration target design, or rough-order monthly Azure cost estimate for a server estate.
  Outputs typically include a draw.io document, an Excel cost workbook, a CSV summary, and JSON metadata.
tools:
  - DrawioMCP_create_diagram
  - DrawioMCP_search_shapes
  - RunInTerminal
---

# Azure Architecture Skill

Use this skill to convert a VM/server inventory into a reusable Azure landing-zone design package.

## When to use

Use this skill when the user asks for any of the following:
- An Azure architecture diagram from a server or VM list
- A draw.io or diagrams.net document with Azure stencils
- A first-pass landing-zone design for a migration to Azure
- A rough-order monthly Azure cost estimate from an inventory workbook
- A comparison scenario such as Azure Hybrid Benefit on eligible Windows Server VMs

## Inputs expected

This skill works best when you have:
- A spreadsheet or CSV containing server inventory
- Core sizing fields such as server name, role, CPU, RAM, OS, and application/system grouping
- Region target, such as West Europe
- Scope assumptions, such as new subscription, new VNets, single region, or DR exclusion

If some details are missing, infer a practical first-pass design and state the assumptions in the output artifacts.

## Required workflow

1. Read the input inventory file from the thread workspace.
2. Normalize columns and derive workload classes such as web/app/data/SAP/non-prod.
3. Map servers to an Azure VM size family and then select the latest stable SKU version available in the target region that still meets the workload requirement.
   - Prefer newer region-available D-series SKUs for general web/app workloads.
   - Prefer newer region-available E-series SKUs for data and memory-heavy workloads.
   - Do not hardcode one version if a newer valid version is available in that region.
4. Assign storage profiles for OS and data disks.
   - Prefer Premium SSD v2 for modeled disks.
   - Fall back to Premium SSD managed disks only when the target region, workload, or price trace does not support a clean Premium SSD v2 estimate.
5. Build a hub-and-spoke landing-zone design unless the user explicitly requests a different pattern.
6. Ensure the architecture narrative and recommendations align to the Azure Well-Architected Framework, especially security, reliability, operational excellence, performance efficiency, and cost optimization.
7. Create the architecture diagram through the draw.io MCP server, not through Python string generation.
   - Use `DrawioMCP_search_shapes` when Azure-specific stencil styles are needed.
   - Use `DrawioMCP_create_diagram` to generate the `.drawio` artifact from the modeled architecture.
   - Reflect only the modeled target Azure resources and assumptions, not anything currently deployed.
   - Show each modeled Azure resource explicitly in the diagram rather than collapsing multiple resources into one consolidated node, summary tile, or pooled block.
   - When the inventory implies repeated resources, enumerate them clearly in the architecture output so the user can see the full modeled footprint.
8. Estimate Azure monthly costs using current Azure Retail Prices API data.
9. Produce both baseline PAYG and Azure Hybrid Benefit scenarios when Windows Server eligibility is relevant.
10. Produce reliability recommendations tailored to the modeled estate.
11. Explicitly remind the user to enable Microsoft Defender for Cloud and subscription-level service alerts for the target subscription.
12. Emit these deliverables:
   - `<prefix>-landing-zone.drawio` generated via draw.io MCP
   - `<prefix>-cost-estimate.xlsx`
   - `<prefix>-cost-summary.csv`
   - `<prefix>-estimate-metadata.json`
13. Persist the generated files for download before sharing them with the user.

## Default architecture pattern

Unless the user specifies otherwise, use:
- Four subscriptions by environment: prod, dev, test, and acceptance
- Matching environment VNets for prod, dev, test, and acceptance rather than combining all workloads into one network boundary
- A hub-and-spoke layout within each environment, or a shared connectivity hub with clearly separated spokes per environment when the user wants centralized connectivity
- Prod VNets segmented for web/app and data tiers where needed; dev, test, and acceptance VNets can be simpler unless the inventory or compliance requirements justify more tiers
- Shared services such as Log Analytics, Recovery Services Vault, Key Vault, policy/governance, and subscription monitoring
- Hub services such as VPN/ExpressRoute, VPN Gateway, Azure Firewall, Bastion, and Private DNS Resolver
- Zone-aware shared services and failure-domain separation for critical workloads where the region and service support it
- Well-Architected guardrails called out directly in the architecture assumptions and recommendations

## Costing rules

- Use Azure Retail Prices API list/consumption pricing.
- Restrict VM price selection to true `Consumption` rows.
- Exclude Spot and Low Priority rows.
- Prefer the latest region-available VM SKU version that satisfies the sizing requirement.
- Model Windows baseline using Windows-inclusive pricing.
- Model Azure Hybrid Benefit by using the base compute rate for eligible Windows Server VMs.
- Prefer Premium SSD v2 disk pricing for modeled storage and document any fallback to classic Premium SSD managed disks.
- Exclude items unless the user explicitly asks for them:
  - Data egress
  - Public IP charges
  - DNS query charges
  - DDoS Protection
  - Backup vault storage
  - Paired-region DR
  - SQL Server or third-party licensing not embedded in the selected SKU

## Output expectations

The Excel workbook should contain, at minimum:
- `Summary`
- `SharedServices`
- `VMEstimate`
- `Assumptions`
- `PriceTrace`
- `Recommendations`

The `Summary` sheet should include:
- Baseline monthly total
- Monthly total with Azure Hybrid Benefit
- AHB savings

Subscription readiness reminders should be captured in `Assumptions`, `Recommendations`, and the metadata JSON rather than as a zero-cost summary line.

The metadata JSON should include:
- generation timestamp
- input workbook path
- server count
- baseline monthly total
- monthly total with AHB
- AHB savings
- assumption notes
- reliability recommendations
- subscription reminders
- Well-Architected alignment notes

## Implementation template

Use the included Python template as the starting point for cost-model implementation:
- [generator-template.py](generator-template.py)

Copy it into the current thread workspace, then adapt:
- thread paths
- source workbook path
- region
- environment-specific subscription names and VNet CIDRs for prod, dev, test, and acceptance
- shared service assumptions
- workload grouping rules for sizing and costing only
- any user-requested architecture variants that affect pricing or recommendations

The Python template is for workbook, CSV, and metadata generation only. Create the diagram as a separate step through the draw.io MCP server, and do not use workbook grouping rules to consolidate distinct modeled Azure resources in the architecture view.

## Execution guidance

- Keep the script in the thread workspace, not in the attached repo.
- Validate that the MCP-generated `.drawio` artifact and the Python-generated output files exist and are non-empty.
- If Azure Retail Prices API returns transient errors, use bounded retry/backoff.
- When the user asks for Hybrid Benefit, present both baseline and AHB values so the savings are explicit.
- Include a recommendation section that highlights reliability improvements such as zone redundancy, backup validation, restore testing, and alert/action-group readiness.
- Always call out that Microsoft Defender for Cloud onboarding and subscription-level Service Health or Activity Log alerting still need to be enabled as part of landing-zone readiness.

## Example user asks

- "Here is my VM list. Give me an Azure architecture diagram."
- "Produce the draw.io version with Azure stencils."
- "Do a cost estimation in West Europe."
- "Show me the Hybrid Benefit included costs as well."
