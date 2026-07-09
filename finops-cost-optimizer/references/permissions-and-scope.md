# Permissions and scope

This skill runs on the agent's default Reader access. It does not require any additional role assignment to start. When a specific read is denied, it may ask the user to grant temporary access, but it never assigns roles itself.

## What this means

- Coverage equals the agent's existing read scope. The skill analyzes only the subscriptions and resource groups this agent was given when it was created.
- There is no tenant wide discovery. If a subscription is outside the agent's scope, the skill does not see it. To widen coverage, widen the agent's scope. That is a separate administrative action and is not a prerequisite for this skill.

## Requesting temporary access, never assigning it

The skill starts within the agent's existing read access. If a specific read is denied in some scope, the skill may ask the user to grant temporary, time bound access to that scope. It explains what it needs to read and why, then waits for the user to decide.

The skill never performs the role assignment itself. It has no write or role management tools and stays read only throughout. Granting access is always the user's action, done out of band. The user might activate an eligible role through PIM or add a temporary Reader assignment and remove it once the review is done. Elevation is the user granting temporary access, not a role assignment the skill makes.

If the user declines, or does not grant access, the skill skips the denied check, records it in the report as not assessed because of insufficient access, and continues with everything it can read.

## Reads used, all covered by Reader

- Subscription enumeration: the list of subscriptions the identity can see.
- Cost: the Cost Management query at subscription scope. Reader can read cost data at subscription and resource group scope.
- Cost fallback: if a tenant blocks the Cost Management query action, the cost_rank tool falls back to the Consumption usage details read, which is a plain read covered by Reader.
- Advisor cost recommendations.
- Azure Monitor metrics.
- Reservation recommendations. Savings plan recommendations are best effort and may return nothing under Reader in some tenants.
- Resource enumeration for the orphaned and storage checks.

## Billing scope note

Cost figures here come from resource and subscription scope queries. Enrollment or billing account scope data (for example EA or MCA invoice level views) is not used, because that requires billing roles outside the Azure RBAC Reader model.

## Identity setup for the Python tools

The cost_rank and commitment_recommendations tools call Azure Resource Manager. Enable managed identity with the ARM scope on each tool in the Identity tab when you create it in the Builder.
