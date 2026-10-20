# Scenario coverage for flowlog-firewall-advisor

Category: Network. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| Network topology diagram | Added | Scheduled | Weekly | High |
| Azure Firewall rule generation | Covered | On-demand | During provisioning | Medium |
| Firewall log analysis (KQL) | Covered | Hybrid | Daily + on-demand | High |
| DNS/VPN troubleshooting | Added | On-demand | During connectivity issues | Medium |
| VNet peering health check | Added | Scheduled | Daily | Medium |
| ExpressRoute / VPN Gateway health | Added | Hybrid | Every 5 min + alert | High |
| DNS zone record hygiene | Added | Scheduled | Weekly | High |

## Network topology diagram

Status: Added. Source category: Network Topology And Connectivity.

Auto-generates a visual network topology showing VNets, peerings, subnets, gateways, and connected resources.

Sample prompt:

> Generate a Mermaid diagram showing the network topology for subscription '{subscription_name}'. Include all VNets, their subnets, peering connections, VPN/ExpressRoute gateways, private endpoints, and key resources in each subnet. Show address spaces and peering status.

Mode: Scheduled. Frequency: Weekly. Time saved: High.

## Azure Firewall rule generation

Status: Covered. Source category: Network Topology And Connectivity.

Generates properly structured Azure Firewall rules based on requirements, following naming conventions and best practices.

Sample prompt:

> Generate an Azure Firewall network rule to allow traffic from subnet '{source_subnet}' to '{destination}' on ports {ports}. Follow naming convention '{prefix}-{direction}-{service}'. Include the az CLI command and Bicep snippet to deploy it.

Mode: On-demand. Frequency: During provisioning. Time saved: Medium.

## Firewall log analysis (KQL)

Status: Covered. Source category: Network Topology And Connectivity.

Analyzes Azure Firewall logs to identify blocked traffic patterns, top talkers, and potential misconfigurations.

Sample prompt:

> Query Azure Firewall diagnostic logs for the last 24 hours. Show: (1) top 20 denied flows by count, (2) denied flows where source is an internal subnet (potential misconfiguration), (3) allowed flows to suspicious destinations, (4) traffic volume by rule collection.

Mode: Hybrid. Frequency: Daily + on-demand. Time saved: High.

## DNS/VPN troubleshooting

Status: Added. Source category: Network Topology And Connectivity.

Investigates DNS resolution failures and VPN connectivity issues to restore hybrid and name resolution services.

Sample prompt:

> Diagnose DNS and VPN issues: (1) check DNS resolution failures, which queries are returning NXDOMAIN or SERVFAIL, from which clients, for which domains, (2) check VPN tunnel status, which tunnels are down, disconnect reason, BGP peer state, and last successful connection time. Provide remediation steps.

Mode: On-demand. Frequency: During connectivity issues. Time saved: Medium.

## VNet peering health check

Status: Added. Source category: Network Topology And Connectivity.

Monitors VNet peering connections for status issues, disconnected peerings, or asymmetric configurations.

Sample prompt:

> List all VNet peerings across subscriptions. Check: (1) peering status (Connected/Disconnected/Initiated), (2) both sides exist and are connected, (3) gateway transit settings are symmetric, (4) address space overlaps. Flag any peering not in 'Connected' state or with misconfigured transit.

Mode: Scheduled. Frequency: Daily. Time saved: Medium.

## ExpressRoute / VPN Gateway health

Status: Added. Source category: Network Topology And Connectivity.

Monitors hybrid connectivity gateway health, tunnel status, and throughput to prevent outages.

Sample prompt:

> Check all ExpressRoute circuits and VPN Gateways. Show: (1) circuit/gateway provisioning state, (2) peering state (for ER), (3) tunnel connection status (for VPN), (4) BGP peer state, (5) ingress/egress throughput last 1h vs capacity. Alert on any tunnel down or BGP not established.

Mode: Hybrid. Frequency: Every 5 min + alert. Time saved: High.

## DNS zone record hygiene

Status: Added. Source category: Network Topology And Connectivity.

Identifies dangling DNS records pointing to deleted Azure resources, which could be hijacked by attackers.

Sample prompt:

> Query all Azure DNS zones and Private DNS zones. For each A, AAAA, and CNAME record, verify the target resource still exists in the subscription. Flag records where: (1) target IP is not assigned to any resource, (2) CNAME target domain is not resolving, (3) alias records referencing deleted resources.

Mode: Scheduled. Frequency: Weekly. Time saved: High.
