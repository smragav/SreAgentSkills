# Skill index

All 105 skills by category. They were created for the scenarios in [alsanch/azure-sre-agent-scenarios](https://github.com/alsanch/azure-sre-agent-scenarios) and also cover additional scenarios. The initial skills came from Onur Senturk's repository, [onsenturk/SreAgentExtensions](https://github.com/onsenturk/SreAgentExtensions). Workflow availability is not live Azure validation. See [license notices](./THIRD-PARTY-NOTICES.md).

## Billing and Cost

| Skill | Description | Suggested mode | Suggested cadence |
| --- | --- | --- | --- |
| 6-month cost summary & trends | [6-month-cost-summary-trends](./billing-cost/6-month-cost-summary-trends/SKILL.md): Use when investigating 6-month cost summary & trends. | Scheduled | Monthly |
| Budget alerts configuration audit | [budget-alerts-configuration-audit](./billing-cost/budget-alerts-configuration-audit/SKILL.md): Use when investigating budget alerts configuration audit. | Scheduled | Monthly |
| Consolidated cost reporting | [consolidated-cost-reporting](./billing-cost/consolidated-cost-reporting/SKILL.md): Use when investigating consolidated cost reporting. | Scheduled | Monthly |
| Cost analysis by tag/environment | [cost-analysis-by-tag-environment](./billing-cost/cost-analysis-by-tag-environment/SKILL.md): Use when investigating cost analysis by tag/environment. | Scheduled | Weekly |
| Cost anomaly detection | [cost-anomaly-detection](./billing-cost/cost-anomaly-detection/SKILL.md): Use when investigating cost anomaly detection. | Hybrid | Daily + event >20% spike |
| Cross-period cost comparison (MG level) | [cross-period-cost-comparison-mg-level](./billing-cost/cross-period-cost-comparison-mg-level/SKILL.md): Use when investigating cross-period cost comparison (mg level). | Scheduled | Monthly |
| Disk tier-down opportunities | [disk-tier-down-opportunities](./billing-cost/disk-tier-down-opportunities/SKILL.md): Use when investigating disk tier-down opportunities. | Scheduled | Bi-weekly |
| FinOps Cost Optimizer | [finops-cost-optimizer](./billing-cost/finops-cost-optimizer/SKILL.md): Use when the user asks for a FinOps review, Azure cost optimization, cost savings, reducing spend, rightsizing, idle or forgotten resources, or "where is my Azure money going". | n/a | n/a |
| Log Analytics workspace ingestion cost analysis | [log-analytics-workspace-ingestion-cost-analysis](./billing-cost/log-analytics-workspace-ingestion-cost-analysis/SKILL.md): Use when investigating log analytics workspace ingestion cost analysis. | Scheduled | Weekly |
| Orphaned resources & cost impact analysis | [orphaned-resources-cost-impact-analysis](./billing-cost/orphaned-resources-cost-impact-analysis/SKILL.md): Use when investigating orphaned resources & cost impact analysis. | Scheduled | Daily |
| Resources with highest cost increase | [resources-with-highest-cost-increase](./billing-cost/resources-with-highest-cost-increase/SKILL.md): Use when investigating resources with highest cost increase. | Hybrid | Daily + alert >30% WoW |
| Top consumer services identification | [top-consumer-services-identification](./billing-cost/top-consumer-services-identification/SKILL.md): Use when investigating top consumer services identification. | Scheduled | Weekly |
| Underutilized resources detection | [underutilized-resources-detection](./billing-cost/underutilized-resources-detection/SKILL.md): Use when investigating underutilized resources detection. | Scheduled | Weekly |

## Identity and Access

| Skill | Description | Suggested mode | Suggested cadence |
| --- | --- | --- | --- |
| High-privilege operation tracking | [high-privilege-operation-tracking](./identity-access/high-privilege-operation-tracking/SKILL.md): Use when investigating high-privilege operation tracking. | Scheduled | Daily |
| Identity and Access Hygiene | [identity-access-hygiene](./identity-access/identity-access-hygiene/SKILL.md): Use when the user asks about identity hygiene, access reviews, least privilege, role assignments, Owner sprawl, overprivileged principals, service principals with high privilege, classic administrators, or standing access. | n/a | n/a |
| Permissions required for an action | [permissions-required-for-an-action](./identity-access/permissions-required-for-an-action/SKILL.md): Use when investigating permissions required for an action. | On-demand | During access request |
| RBAC access audit (who has what) | [rbac-access-audit-who-has-what](./identity-access/rbac-access-audit-who-has-what/SKILL.md): Use when investigating rbac access audit (who has what). | Scheduled | Weekly |
| RBAC redundancy & over-privilege assessment | [rbac-redundancy-over-privilege-assessment](./identity-access/rbac-redundancy-over-privilege-assessment/SKILL.md): Use when investigating rbac redundancy & over-privilege assessment. | Scheduled | Weekly |
| Stale RBAC assignments | [stale-rbac-assignments](./identity-access/stale-rbac-assignments/SKILL.md): Use when investigating stale rbac assignments. | Scheduled | Weekly |

## Resource Organization

| Skill | Description | Suggested mode | Suggested cadence |
| --- | --- | --- | --- |
| AI model inventory & retirement lifecycle | [ai-model-inventory-retirement-lifecycle](./resource-organization/ai-model-inventory-retirement-lifecycle/SKILL.md): Use when investigating ai model inventory & retirement lifecycle. | Scheduled | Weekly |
| Azure Architecture Skill | [azure-arch](./resource-organization/azure-arch/SKILL.md): Build a first-pass Azure landing-zone architecture and cost estimate from a VM inventory workbook. | n/a | n/a |
| Deprecation and Retirement Tracker | [deprecation-retirement-tracker](./resource-organization/deprecation-retirement-tracker/SKILL.md): Use when the user asks about deprecations, retirements, end of life runtimes or platforms, unsupported versions, retiring SKUs, old Kubernetes or AKS versions, legacy or classic resources, or upcoming forced migrations. | n/a | n/a |
| Extension health across VMs | [extension-health-across-vms](./resource-organization/extension-health-across-vms/SKILL.md): Use when investigating extension health across vms. | Scheduled | Daily |
| Management Group hierarchy audit | [management-group-hierarchy-audit](./resource-organization/management-group-hierarchy-audit/SKILL.md): Use when investigating management group hierarchy audit. | Scheduled | Monthly |
| Move resources between subscriptions | [move-resources-between-subscriptions](./resource-organization/move-resources-between-subscriptions/SKILL.md): Use when investigating move resources between subscriptions. | On-demand | During reorg |
| Quota and Limit Watch | [quota-limit-watch](./resource-organization/quota-limit-watch/SKILL.md): Use when the user asks about quotas, service limits, capacity headroom, vCPU or core limits, public IP or network limits, "will a deployment or scale out fail", or approaching Azure limits. | n/a | n/a |
| Resource age tracking | [resource-age-tracking](./resource-organization/resource-age-tracking/SKILL.md): Use when investigating resource age tracking. | Scheduled | Weekly |
| Resource group sprawl detection | [resource-group-sprawl-detection](./resource-organization/resource-group-sprawl-detection/SKILL.md): Use when investigating resource group sprawl detection. | Scheduled | Weekly |
| Resource lock compliance audit | [resource-lock-compliance-audit](./resource-organization/resource-lock-compliance-audit/SKILL.md): Use when investigating resource lock compliance audit. | Scheduled | Weekly |
| Resources created yesterday | [resources-created-yesterday](./resource-organization/resources-created-yesterday/SKILL.md): Use when investigating resources created yesterday. | Scheduled | Daily |
| SQL CMDB Inventory Skill | [sql-cmdb-inventory](./resource-organization/sql-cmdb-inventory/SKILL.md): Build a scoped SQL inventory across Azure SQL VM, Arc enabled SQL Server, SQL Managed Instance and Azure SQL. | n/a | n/a |
| Subscription hygiene score | [subscription-hygiene-score](./resource-organization/subscription-hygiene-score/SKILL.md): Use when investigating subscription hygiene score. | Scheduled | Weekly |
| Subscription limits approaching | [subscription-limits-approaching](./resource-organization/subscription-limits-approaching/SKILL.md): Use when investigating subscription limits approaching. | Scheduled | Weekly |

## Network

| Skill | Description | Suggested mode | Suggested cadence |
| --- | --- | --- | --- |
| Azure Firewall rule generation | [azure-firewall-rule-generation](./network/azure-firewall-rule-generation/SKILL.md): Use when investigating azure firewall rule generation. | On-demand | During provisioning |
| DDoS protection coverage audit | [ddos-protection-coverage-audit](./network/ddos-protection-coverage-audit/SKILL.md): Use when investigating ddos protection coverage audit. | Scheduled | Monthly |
| DNS zone record hygiene | [dns-zone-record-hygiene](./network/dns-zone-record-hygiene/SKILL.md): Use when investigating dns zone record hygiene. | Scheduled | Weekly |
| DNS/VPN troubleshooting | [dns-vpn-troubleshooting](./network/dns-vpn-troubleshooting/SKILL.md): Use when investigating dns/vpn troubleshooting. | On-demand | During connectivity issues |
| ExpressRoute / VPN Gateway health | [expressroute-vpn-gateway-health](./network/expressroute-vpn-gateway-health/SKILL.md): Use when investigating expressroute / vpn gateway health. | Hybrid | Every 5 min + alert |
| Firewall log analysis (KQL) | [firewall-log-analysis-kql](./network/firewall-log-analysis-kql/SKILL.md): Use when investigating firewall log analysis (kql). | Hybrid | Daily + on-demand |
| Flow Log Firewall Advisor | [flowlog-firewall-advisor](./network/flowlog-firewall-advisor/SKILL.md): Use when the user asks what firewall rules a virtual network needs, wants to move a VNet behind Azure Firewall, asks what traffic to allow, mentions deriving rules from flow logs, asks about egress from a VNet, lateral movement between subnets, or wants to know what is actually talking to what. | n/a | n/a |
| Network Exposure Review | [network-exposure-review](./network/network-exposure-review/SKILL.md): Use when the user asks about internet exposure, public exposure, attack surface, open ports, NSG rules open to the internet, public IPs, storage public access, or PaaS resources reachable from the internet. | n/a | n/a |
| Network topology diagram | [network-topology-diagram](./network/network-topology-diagram/SKILL.md): Use when investigating network topology diagram. | Scheduled | Weekly |
| Overly permissive NSG rules audit | [overly-permissive-nsg-rules-audit](./network/overly-permissive-nsg-rules-audit/SKILL.md): Use when investigating overly permissive nsg rules audit. | Scheduled | Daily |
| Private endpoint & public exposure audit | [private-endpoint-public-exposure-audit](./network/private-endpoint-public-exposure-audit/SKILL.md): Use when investigating private endpoint & public exposure audit. | Scheduled | Weekly |
| Public IP inventory & justification | [public-ip-inventory-justification](./network/public-ip-inventory-justification/SKILL.md): Use when investigating public ip inventory & justification. | Scheduled | Weekly |
| SSL/TLS certificate expiration tracking | [ssl-tls-certificate-expiration-tracking](./network/ssl-tls-certificate-expiration-tracking/SKILL.md): Use when investigating ssl/tls certificate expiration tracking. | Scheduled | Daily |
| VNet peering health check | [vnet-peering-health-check](./network/vnet-peering-health-check/SKILL.md): Use when investigating vnet peering health check. | Scheduled | Daily |

## Security

| Skill | Description | Suggested mode | Suggested cadence |
| --- | --- | --- | --- |
| Certificate and Secret Expiry | [certificate-secret-expiry](./security/certificate-secret-expiry/SKILL.md): Use when the user asks about expiring certificates, expiring secrets, certificate or secret rotation, "what is about to expire", Key Vault expiry, TLS certificate expiry, or service principal or app registration credential expiry. | n/a | n/a |
| Certificate renewal automation | [certificate-renewal-automation](./security/certificate-renewal-automation/SKILL.md): Use when investigating certificate renewal automation. | Scheduled | Daily |
| Defender for Cloud assessment | [defender-for-cloud-assessment](./security/defender-for-cloud-assessment/SKILL.md): Use when investigating defender for cloud assessment. | Scheduled | Weekly |

## Management

| Skill | Description | Suggested mode | Suggested cadence |
| --- | --- | --- | --- |
| Agent health monitoring | [agent-health-monitoring](./management/agent-health-monitoring/SKILL.md): Use when investigating agent health monitoring. | Scheduled | Daily |
| AI inference reliability investigation | [ai-inference-reliability-investigation](./management/ai-inference-reliability-investigation/SKILL.md): Use when investigating ai inference reliability investigation. | On demand | During an inference reliability investigation |
| AKS application incident triage | [aks-application-incident-triage](./management/aks-application-incident-triage/SKILL.md): Use when investigating aks application incident triage. | On demand | During an application incident |
| AKS Reliability Review | [aks-reliability-review](./management/aks-reliability-review/SKILL.md): Use when the user asks for an AKS review, Kubernetes cluster reliability, AKS best practices, cluster resilience, or an AKS health check. | n/a | n/a |
| Alert fatigue analysis | [alert-fatigue-analysis](./management/alert-fatigue-analysis/SKILL.md): Use when investigating alert fatigue analysis. | Scheduled | Weekly |
| Alert Hygiene Review | [alert-hygiene-review](./management/alert-hygiene-review/SKILL.md): Use when the user asks about alert noise, alert fatigue, flapping alerts, too many alerts, noisy alert rules, alert tuning, or severity misconfiguration. | n/a | n/a |
| Alert rules best-practice audit | [alert-rules-best-practice-audit](./management/alert-rules-best-practice-audit/SKILL.md): Use when investigating alert rules best-practice audit. | Scheduled | Monthly |
| All write operations across subscription (24h) | [all-write-operations-across-subscription-24h](./management/all-write-operations-across-subscription-24h/SKILL.md): Use when investigating all write operations across subscription (24h). | Scheduled | Daily digest |
| App Service and Container Apps Health | [appservice-containerapps-health](./management/appservice-containerapps-health/SKILL.md): Use when the user asks about App Service or Web App health, Container Apps health, web tier reliability, scaling and health probes, Always On, HTTPS and TLS enforcement, or a web workload best practices check. | n/a | n/a |
| Backup and restore validation | [backup-restore-validation](./management/backup-restore-validation/SKILL.md): Use when investigating backup and restore validation. | On demand | After an approved restore exercise or backup review |
| Backup policy compliance & gap detection | [backup-policy-compliance-gap-detection](./management/backup-policy-compliance-gap-detection/SKILL.md): Use when investigating backup policy compliance & gap detection. | Scheduled | Daily |
| Blameless Postmortem Writer | [blameless-postmortem-writer](./management/blameless-postmortem-writer/SKILL.md): Use when the user asks for a postmortem, a post incident review, an incident retrospective, a root cause writeup, or a blameless RCA document after an incident. | n/a | n/a |
| Change Audit | [change-audit](./management/change-audit/SKILL.md): Use when the user asks what changed, a change audit, change review, "what changed and did it break something", recent deployments and their effect, or wants to correlate changes with incidents. | n/a | n/a |
| Changes by non-service-principal users | [changes-by-non-service-principal-users](./management/changes-by-non-service-principal-users/SKILL.md): Use when investigating changes by non-service-principal users. | Scheduled | Daily |
| Changes in last 24h for a resource | [changes-in-last-24h-for-a-resource](./management/changes-in-last-24h-for-a-resource/SKILL.md): Use when investigating changes in last 24h for a resource. | On-demand | During incident |
| Data collection rules audit | [data-collection-rules-audit](./management/data-collection-rules-audit/SKILL.md): Use when investigating data collection rules audit. | Scheduled | Weekly |
| Data Platform Review | [data-platform-review](./management/data-platform-review/SKILL.md): Use when the user asks for a database review, data platform reliability, SQL or PostgreSQL or MySQL or Cosmos DB resilience, database backup and geo replication, or a data tier health check. | n/a | n/a |
| Diagnostic settings coverage audit | [diagnostic-settings-coverage-audit](./management/diagnostic-settings-coverage-audit/SKILL.md): Use when investigating diagnostic settings coverage audit. | Scheduled | Weekly |
| Executive operational report generation (PDF) | [executive-operational-report-generation-pdf](./management/executive-operational-report-generation-pdf/SKILL.md): Use when investigating executive operational report generation (pdf). | Scheduled | Monthly |
| Fired alerts summary (last 24h) | [fired-alerts-summary-last-24h](./management/fired-alerts-summary-last-24h/SKILL.md): Use when investigating fired alerts summary (last 24h). | Scheduled | Daily morning |
| Identify who added a firewall/NSG rule | [identify-who-added-a-firewall-nsg-rule](./management/identify-who-added-a-firewall-nsg-rule/SKILL.md): Use when investigating identify who added a firewall/nsg rule. | Event-driven | On NSG change alert |
| Incident Triage and Root Cause Assist | [incident-triage-rca](./management/incident-triage-rca/SKILL.md): Use when the user reports an incident, an outage, an alert that fired, a resource that is down or degraded, or asks for triage, root cause analysis, or "what changed". | n/a | n/a |
| KQL log queries (common patterns) | [kql-log-queries-common-patterns](./management/kql-log-queries-common-patterns/SKILL.md): Use when investigating kql log queries (common patterns). | On-demand | During troubleshooting |
| Logic Apps code/definition inspection | [logic-apps-code-definition-inspection](./management/logic-apps-code-definition-inspection/SKILL.md): Use when investigating logic apps code/definition inspection. | On-demand | During debugging |
| Messaging delivery failure triage | [messaging-delivery-failure-triage](./management/messaging-delivery-failure-triage/SKILL.md): Use when investigating messaging delivery failure triage. | On demand | During a delivery failure or backlog investigation |
| Observability Coverage Gap | [observability-coverage-gap](./management/observability-coverage-gap/SKILL.md): Use when the user asks about monitoring coverage, observability gaps, "where are we blind", missing diagnostic settings, resources with no alerts, no action groups, or no Log Analytics. | n/a | n/a |
| Operations dashboard generation | [operations-dashboard-generation](./management/operations-dashboard-generation/SKILL.md): Use when investigating operations dashboard generation. | On-demand | On workload onboarding |
| Planned maintenance awareness | [planned-maintenance-awareness](./management/planned-maintenance-awareness/SKILL.md): Use when investigating planned maintenance awareness. | Scheduled | Daily |
| Post-incident review automation | [post-incident-review-automation](./management/post-incident-review-automation/SKILL.md): Use when investigating post-incident review automation. | Event-driven | On incident closure |
| Recurring Incident Patterns | [recurring-incident-patterns](./management/recurring-incident-patterns/SKILL.md): Use when the user asks about recurring incidents, repeat offenders, chronic problems, "what keeps breaking", flaky resources, or wants to find the workloads that generate the most incidents over time. | n/a | n/a |
| Release regression detection | [release-regression-detection](./management/release-regression-detection/SKILL.md): Use when investigating release regression detection. | On demand | After a release or reported regression |
| Reliability Posture Review | [reliability-posture-review](./management/reliability-posture-review/SKILL.md): Use when the user asks for a reliability review, resilience assessment, high availability check, single points of failure, a Well-Architected reliability review, or "will we survive a zone or region outage". | n/a | n/a |
| Resource health status summary | [resource-health-status-summary](./management/resource-health-status-summary/SKILL.md): Use when investigating resource health status summary. | Scheduled | Every 1h |
| Resource metrics analysis | [resource-metrics-analysis](./management/resource-metrics-analysis/SKILL.md): Use when investigating resource metrics analysis. | On-demand | During incident |
| Rollback command generation for bad changes | [rollback-command-generation-for-bad-changes](./management/rollback-command-generation-for-bad-changes/SKILL.md): Use when investigating rollback command generation for bad changes. | Event-driven | On failed change |
| RTO/RPO gap analysis | [rto-rpo-gap-analysis](./management/rto-rpo-gap-analysis/SKILL.md): Use when investigating rto/rpo gap analysis. | Scheduled | Monthly |
| Service Health incidents & resource impact | [service-health-incidents-resource-impact](./management/service-health-incidents-resource-impact/SKILL.md): Use when investigating service health incidents & resource impact. | Event-driven | On new incident |
| SKU reliability assessment | [sku-reliability-assessment](./management/sku-reliability-assessment/SKILL.md): Use when investigating sku reliability assessment. | On-demand | Architecture review |
| SLO and error budget analysis | [slo-error-budget-analysis](./management/slo-error-budget-analysis/SKILL.md): Use when investigating slo and error budget analysis. | Scheduled | Daily or during an incident |
| Support ticket creation (pre-populated) | [support-ticket-creation-pre-populated](./management/support-ticket-creation-pre-populated/SKILL.md): Use when investigating support ticket creation (pre-populated). | On-demand | After auto-resolve fails |
| VM performance anomaly detection | [vm-performance-anomaly-detection](./management/vm-performance-anomaly-detection/SKILL.md): Use when investigating vm performance anomaly detection. | Hybrid | Every 15 min + alert |
| Well-Architected Review | [well-architected-review](./management/well-architected-review/SKILL.md): Use when the user asks for a Well-Architected review, a WAF assessment, a Well-Architected Framework scorecard, a pillar review, or "how well architected are we". | n/a | n/a |
| Workbook auto-generation | [workbook-auto-generation](./management/workbook-auto-generation/SKILL.md): Use when investigating workbook auto-generation. | On-demand | On workload onboarding |

## Governance

| Skill | Description | Suggested mode | Suggested cadence |
| --- | --- | --- | --- |
| Automated compliance remediation tasks | [automated-compliance-remediation-tasks](./governance/automated-compliance-remediation-tasks/SKILL.md): Use when investigating automated compliance remediation tasks. | Scheduled | Weekly |
| Azure Policy assignment assessment | [azure-policy-assignment-assessment](./governance/azure-policy-assignment-assessment/SKILL.md): Use when investigating azure policy assignment assessment. | Scheduled | Monthly |
| Custom Policy generation | [custom-policy-generation](./governance/custom-policy-generation/SKILL.md): Use when investigating custom policy generation. | On-demand | During governance sprint |
| Effective policies per scope | [effective-policies-per-scope](./governance/effective-policies-per-scope/SKILL.md): Use when investigating effective policies per scope. | On-demand | During audit |
| Find built-in policy for a requirement | [find-built-in-policy-for-a-requirement](./governance/find-built-in-policy-for-a-requirement/SKILL.md): Use when investigating find built-in policy for a requirement. | On-demand | During compliance planning |
| Naming & tagging convention compliance | [naming-tagging-convention-compliance](./governance/naming-tagging-convention-compliance/SKILL.md): Use when investigating naming & tagging convention compliance. | Scheduled | Weekly |
| Policy compliance state monitoring | [policy-compliance-state-monitoring](./governance/policy-compliance-state-monitoring/SKILL.md): Use when investigating policy compliance state monitoring. | Scheduled | Daily |
| Policy exemptions review | [policy-exemptions-review](./governance/policy-exemptions-review/SKILL.md): Use when investigating policy exemptions review. | Scheduled | Weekly |
| Tag Governance Compliance | [tag-governance-compliance](./governance/tag-governance-compliance/SKILL.md): Use when the user asks about tagging compliance, tag governance, resources missing tags, untagged resources, ownership tags, missing owner or environment or cost center tags, or chargeback readiness. | n/a | n/a |

## Platform Automation

| Skill | Description | Suggested mode | Suggested cadence |
| --- | --- | --- | --- |
| Export existing resources to ARM/Bicep | [export-existing-resources-to-arm-bicep](./platform-automation/export-existing-resources-to-arm-bicep/SKILL.md): Use when investigating export existing resources to arm/bicep. | On-demand | During IaC adoption |
| Failed deployments in last 24h | [failed-deployments-in-last-24h](./platform-automation/failed-deployments-in-last-24h/SKILL.md): Use when investigating failed deployments in last 24h. | Scheduled | Daily |
| Pre-Change Readiness | [pre-change-readiness](./platform-automation/pre-change-readiness/SKILL.md): Use before a launch, a migration, a deployment, or a big change, or when the user asks for a readiness check, a go or no-go, or "are we ready to ship". | n/a | n/a |

## Validation boundary

Skills with an evidence workflow contain collection commands, analysis rules, output fields, permissions, limitations and Microsoft sources. Local validators check all skill bundles and synthetic evidence contracts. Customer identity, API execution, real evidence and operational outcomes require a separately authorized smoke test.

## Sources

- [SRE Agent skills](https://learn.microsoft.com/azure/sre-agent/skills).
