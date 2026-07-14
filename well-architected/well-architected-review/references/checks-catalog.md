# Checks catalog

The curated checks behind the scorecard, one small set per Well-Architected pillar, all read with Azure Resource Graph and covered by Reader. Each check counts the applicable resources and the failing resources, so the score is a defensible pass ratio, not a guess. These are a roll up; the dedicated skill for each pillar holds the full detail.

## Scoring

- Each check has a severity, which sets its weight: Critical 4, High 3, Medium 2, Low 1.
- For each check, pass ratio equals (applicable minus failing) divided by applicable. A check with no applicable resources is skipped.
- Pillar score equals 100 times the weighted average of its checks' pass ratios, rounded. Ratings: Excellent 90 and above, Good 75 to 89, Fair 50 to 74, Poor below 50.

## Reliability

- Virtual machines with no availability zone and no availability set (High). Deep dive: reliability-posture-review.
- Locally redundant storage accounts (Medium).
- Premium or Business Critical SQL databases without zone redundancy (High).
- Single region Cosmos DB accounts (Medium).

## Security

- Storage accounts allowing anonymous blob access (High). Deep dive: network-exposure-review.
- Platform services with public network access enabled (Medium).
- Key Vaults without purge protection (Medium). Deep dive: identity-access-hygiene for the wider posture.

## Cost Optimization

- Unattached managed disks (Medium). Deep dive: finops-cost-optimizer.
- Unassociated public IP addresses (Low).

## Operational Excellence

- Resources with no owner tag (Medium). Deep dive: tag-governance-compliance.
- AKS clusters below the supported Kubernetes floor (Medium). Deep dive: deprecation-retirement-tracker.

## Performance Efficiency

- App Service plans on Free, Shared, or Basic tiers (Medium). Deep dive: appservice-containerapps-health.
- Container Apps that cannot scale out (a single maximum replica) (Low).

## Extending

Add a check by appending to the list in tools/waf_assess.py with its pillar, severity, recommendation, and a Resource Graph query that returns applicable and failing counts. Keep the set small and high signal; the detailed skills are where breadth belongs.
