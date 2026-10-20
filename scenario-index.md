# Scenario index

Every scenario from https://github.com/alsanch/azure-sre-agent-scenarios mapped to the skill that answers it, grouped by category. Generated from the per skill references/scenarios.md files.

Statuses: Covered (existing checks answer it), Partial (part answered, rest by guided prompt), Added (new guided prompt).

## Billing and Cost

| Scenario | Skill | Status | Mode | Frequency |
| --- | --- | --- | --- | --- |
| 6-month cost summary & trends | [finops-cost-optimizer](billing-cost/finops-cost-optimizer/references/scenarios.md) | Partial | Scheduled | Monthly |
| Budget alerts configuration audit | [finops-cost-optimizer](billing-cost/finops-cost-optimizer/references/scenarios.md) | Added | Scheduled | Monthly |
| Consolidated cost reporting | [finops-cost-optimizer](billing-cost/finops-cost-optimizer/references/scenarios.md) | Added | Scheduled | Monthly |
| Cost analysis by tag/environment | [finops-cost-optimizer](billing-cost/finops-cost-optimizer/references/scenarios.md) | Partial | Scheduled | Weekly |
| Cost anomaly detection | [finops-cost-optimizer](billing-cost/finops-cost-optimizer/references/scenarios.md) | Partial | Hybrid | Daily + event >20% spike |
| Cross-period cost comparison (MG level) | [finops-cost-optimizer](billing-cost/finops-cost-optimizer/references/scenarios.md) | Added | Scheduled | Monthly |
| Disk tier-down opportunities | [finops-cost-optimizer](billing-cost/finops-cost-optimizer/references/scenarios.md) | Added | Scheduled | Bi-weekly |
| Log Analytics workspace ingestion cost analysis | [finops-cost-optimizer](billing-cost/finops-cost-optimizer/references/scenarios.md) | Added | Scheduled | Weekly |
| Orphaned resources & cost impact analysis | [finops-cost-optimizer](billing-cost/finops-cost-optimizer/references/scenarios.md) | Covered | Scheduled | Daily |
| Resources with highest cost increase | [finops-cost-optimizer](billing-cost/finops-cost-optimizer/references/scenarios.md) | Partial | Hybrid | Daily + alert >30% WoW |
| Top consumer services identification | [finops-cost-optimizer](billing-cost/finops-cost-optimizer/references/scenarios.md) | Partial | Scheduled | Weekly |
| Underutilized resources detection | [finops-cost-optimizer](billing-cost/finops-cost-optimizer/references/scenarios.md) | Covered | Scheduled | Weekly |

## Identity and Access

| Scenario | Skill | Status | Mode | Frequency |
| --- | --- | --- | --- | --- |
| High-privilege operation tracking | [identity-access-hygiene](identity-access/identity-access-hygiene/references/scenarios.md) | Added | Scheduled | Daily |
| Permissions required for an action | [identity-access-hygiene](identity-access/identity-access-hygiene/references/scenarios.md) | Added | On-demand | During access request |
| RBAC access audit (who has what) | [identity-access-hygiene](identity-access/identity-access-hygiene/references/scenarios.md) | Added | Scheduled | Weekly |
| RBAC redundancy & over-privilege assessment | [identity-access-hygiene](identity-access/identity-access-hygiene/references/scenarios.md) | Covered | Scheduled | Weekly |
| Stale RBAC assignments | [identity-access-hygiene](identity-access/identity-access-hygiene/references/scenarios.md) | Covered | Scheduled | Weekly |

## Resource Organization

| Scenario | Skill | Status | Mode | Frequency |
| --- | --- | --- | --- | --- |
| AI model inventory & retirement lifecycle | [deprecation-retirement-tracker](resource-organization/deprecation-retirement-tracker/references/scenarios.md) | Partial | Scheduled | Weekly |
| Extension health across VMs | [sql-cmdb-inventory](resource-organization/sql-cmdb-inventory/references/scenarios.md) | Added | Scheduled | Daily |
| Management Group hierarchy audit | [azure-arch](resource-organization/azure-arch/references/scenarios.md) | Added | Scheduled | Monthly |
| Move resources between subscriptions | [azure-arch](resource-organization/azure-arch/references/scenarios.md) | Added | On-demand | During reorg |
| Resource age tracking | [sql-cmdb-inventory](resource-organization/sql-cmdb-inventory/references/scenarios.md) | Added | Scheduled | Weekly |
| Resource group sprawl detection | [azure-arch](resource-organization/azure-arch/references/scenarios.md) | Added | Scheduled | Weekly |
| Resource lock compliance audit | [azure-arch](resource-organization/azure-arch/references/scenarios.md) | Added | Scheduled | Weekly |
| Resources created yesterday | [sql-cmdb-inventory](resource-organization/sql-cmdb-inventory/references/scenarios.md) | Added | Scheduled | Daily |
| Subscription hygiene score | [azure-arch](resource-organization/azure-arch/references/scenarios.md) | Added | Scheduled | Weekly |
| Subscription limits approaching | [quota-limit-watch](resource-organization/quota-limit-watch/references/scenarios.md) | Covered | Scheduled | Weekly |

## Network

| Scenario | Skill | Status | Mode | Frequency |
| --- | --- | --- | --- | --- |
| Azure Firewall rule generation | [flowlog-firewall-advisor](network/flowlog-firewall-advisor/references/scenarios.md) | Covered | On-demand | During provisioning |
| DDoS protection coverage audit | [network-exposure-review](network/network-exposure-review/references/scenarios.md) | Added | Scheduled | Monthly |
| DNS zone record hygiene | [flowlog-firewall-advisor](network/flowlog-firewall-advisor/references/scenarios.md) | Added | Scheduled | Weekly |
| DNS/VPN troubleshooting | [flowlog-firewall-advisor](network/flowlog-firewall-advisor/references/scenarios.md) | Added | On-demand | During connectivity issues |
| ExpressRoute / VPN Gateway health | [flowlog-firewall-advisor](network/flowlog-firewall-advisor/references/scenarios.md) | Added | Hybrid | Every 5 min + alert |
| Firewall log analysis (KQL) | [flowlog-firewall-advisor](network/flowlog-firewall-advisor/references/scenarios.md) | Covered | Hybrid | Daily + on-demand |
| Network topology diagram | [flowlog-firewall-advisor](network/flowlog-firewall-advisor/references/scenarios.md) | Added | Scheduled | Weekly |
| Overly permissive NSG rules audit | [network-exposure-review](network/network-exposure-review/references/scenarios.md) | Covered | Scheduled | Daily |
| Private endpoint & public exposure audit | [network-exposure-review](network/network-exposure-review/references/scenarios.md) | Covered | Scheduled | Weekly |
| Public IP inventory & justification | [network-exposure-review](network/network-exposure-review/references/scenarios.md) | Partial | Scheduled | Weekly |
| VNet peering health check | [flowlog-firewall-advisor](network/flowlog-firewall-advisor/references/scenarios.md) | Added | Scheduled | Daily |

## Security

| Scenario | Skill | Status | Mode | Frequency |
| --- | --- | --- | --- | --- |
| Certificate renewal automation | [certificate-secret-expiry](security/certificate-secret-expiry/references/scenarios.md) | Added | Scheduled | Daily |
| Defender for Cloud assessment | [certificate-secret-expiry](security/certificate-secret-expiry/references/scenarios.md) | Added | Scheduled | Weekly |
| SSL/TLS certificate expiration tracking | [certificate-secret-expiry](security/certificate-secret-expiry/references/scenarios.md) | Covered | Scheduled | Daily |

## Management

| Scenario | Skill | Status | Mode | Frequency |
| --- | --- | --- | --- | --- |
| Agent health monitoring | [observability-coverage-gap](management/observability-coverage-gap/references/scenarios.md) | Added | Scheduled | Daily |
| Alert fatigue analysis | [alert-hygiene-review](management/alert-hygiene-review/references/scenarios.md) | Covered | Scheduled | Weekly |
| Alert rules best-practice audit | [alert-hygiene-review](management/alert-hygiene-review/references/scenarios.md) | Partial | Scheduled | Monthly |
| All write operations across subscription (24h) | [change-audit](management/change-audit/references/scenarios.md) | Added | Scheduled | Daily digest |
| Backup policy compliance & gap detection | [reliability-posture-review](management/reliability-posture-review/references/scenarios.md) | Partial | Scheduled | Daily |
| Changes by non-service-principal users | [change-audit](management/change-audit/references/scenarios.md) | Partial | Scheduled | Daily |
| Changes in last 24h for a resource | [change-audit](management/change-audit/references/scenarios.md) | Covered | On-demand | During incident |
| Data collection rules audit | [observability-coverage-gap](management/observability-coverage-gap/references/scenarios.md) | Added | Scheduled | Weekly |
| Diagnostic settings coverage audit | [observability-coverage-gap](management/observability-coverage-gap/references/scenarios.md) | Covered | Scheduled | Weekly |
| Executive operational report generation (PDF) | [well-architected-review](management/well-architected-review/references/scenarios.md) | Partial | Scheduled | Monthly |
| Fired alerts summary (last 24h) | [alert-hygiene-review](management/alert-hygiene-review/references/scenarios.md) | Added | Scheduled | Daily morning |
| Identify who added a firewall/NSG rule | [change-audit](management/change-audit/references/scenarios.md) | Added | Event-driven | On NSG change alert |
| KQL log queries (common patterns) | [observability-coverage-gap](management/observability-coverage-gap/references/scenarios.md) | Added | On-demand | During troubleshooting |
| Logic Apps code/definition inspection | [incident-triage-rca](management/incident-triage-rca/references/scenarios.md) | Added | On-demand | During debugging |
| Operations dashboard generation | [observability-coverage-gap](management/observability-coverage-gap/references/scenarios.md) | Added | On-demand | On workload onboarding |
| Planned maintenance awareness | [incident-triage-rca](management/incident-triage-rca/references/scenarios.md) | Added | Scheduled | Daily |
| Post-incident review automation | [blameless-postmortem-writer](management/blameless-postmortem-writer/references/scenarios.md) | Covered | Event-driven | On incident closure |
| Resource health status summary | [incident-triage-rca](management/incident-triage-rca/references/scenarios.md) | Partial | Scheduled | Every 1h |
| Resource metrics analysis | [observability-coverage-gap](management/observability-coverage-gap/references/scenarios.md) | Added | On-demand | During incident |
| Rollback command generation for bad changes | [change-audit](management/change-audit/references/scenarios.md) | Added | Event-driven | On failed change |
| RTO/RPO gap analysis | [reliability-posture-review](management/reliability-posture-review/references/scenarios.md) | Added | Scheduled | Monthly |
| Service Health incidents & resource impact | [incident-triage-rca](management/incident-triage-rca/references/scenarios.md) | Partial | Event-driven | On new incident |
| SKU reliability assessment | [reliability-posture-review](management/reliability-posture-review/references/scenarios.md) | Added | On-demand | Architecture review |
| Support ticket creation (pre-populated) | [incident-triage-rca](management/incident-triage-rca/references/scenarios.md) | Added | On-demand | After auto-resolve fails |
| VM performance anomaly detection | [observability-coverage-gap](management/observability-coverage-gap/references/scenarios.md) | Added | Hybrid | Every 15 min + alert |
| Workbook auto-generation | [observability-coverage-gap](management/observability-coverage-gap/references/scenarios.md) | Added | On-demand | On workload onboarding |

## Governance

| Scenario | Skill | Status | Mode | Frequency |
| --- | --- | --- | --- | --- |
| Automated compliance remediation tasks | [tag-governance-compliance](governance/tag-governance-compliance/references/scenarios.md) | Added | Scheduled | Weekly |
| Azure Policy assignment assessment | [tag-governance-compliance](governance/tag-governance-compliance/references/scenarios.md) | Added | Scheduled | Monthly |
| Custom Policy generation | [tag-governance-compliance](governance/tag-governance-compliance/references/scenarios.md) | Added | On-demand | During governance sprint |
| Effective policies per scope | [tag-governance-compliance](governance/tag-governance-compliance/references/scenarios.md) | Added | On-demand | During audit |
| Find built-in policy for a requirement | [tag-governance-compliance](governance/tag-governance-compliance/references/scenarios.md) | Added | On-demand | During compliance planning |
| Naming & tagging convention compliance | [tag-governance-compliance](governance/tag-governance-compliance/references/scenarios.md) | Covered | Scheduled | Weekly |
| Policy compliance state monitoring | [tag-governance-compliance](governance/tag-governance-compliance/references/scenarios.md) | Added | Scheduled | Daily |
| Policy exemptions review | [tag-governance-compliance](governance/tag-governance-compliance/references/scenarios.md) | Added | Scheduled | Weekly |

## Platform Automation

| Scenario | Skill | Status | Mode | Frequency |
| --- | --- | --- | --- | --- |
| Export existing resources to ARM/Bicep | [pre-change-readiness](platform-automation/pre-change-readiness/references/scenarios.md) | Added | On-demand | During IaC adoption |
| Failed deployments in last 24h | [pre-change-readiness](platform-automation/pre-change-readiness/references/scenarios.md) | Added | Scheduled | Daily |
