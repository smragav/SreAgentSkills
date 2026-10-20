# Scoring method

Reliability findings are ranked by severity, which reflects blast radius and likelihood, not the effort to fix. The scan tool assigns a starting severity per signal; confirm or adjust it with evidence.

## Severity bands

- Critical: an outage is likely and the blast radius is wide, for example a shared ingress point or a production database with no failover path. Reserve Critical for signals corroborated by scope (production naming, public exposure, or a large dependency fan in).
- High: a real single point of failure or a retiring platform tier that will force an outage if unaddressed. Most Basic tier and no redundancy signals start here.
- Medium: a redundancy gap that degrades resilience but has a workaround or a smaller blast radius.
- Low: a gap on a resource whose naming or tags mark it as lab, sandbox, or otherwise not production.

## Starting severity by signal

| Signal | Starting severity |
| --- | --- |
| Basic public IP, Basic load balancer | High |
| Compute with no zone or set redundancy | High |
| Premium SQL database without zone redundancy | High |
| Single instance scale set | Medium |
| Locally redundant storage | Medium |
| Application Gateway not zone redundant | Medium |
| AKS node pool without zones or a single node | Medium |
| Single region Cosmos DB account | Medium |

## Adjustments

- Lower by one band when the resource name or tags mark it non production (lab, dev, sandbox, poc, temp).
- Raise by one band when the resource is clearly production and shared: a public facing name, a hub or shared naming pattern, or a resource many others depend on.
- Never raise to Critical without at least one corroborating signal beyond the base rule.

## Roll up

The report groups findings by severity and by subscription. Sort the finding table by severity, Critical first. The inline summary leads with the count of Critical and High findings, since those are the ones worth acting on first.
