# Permissions and scope

Every skill in this repository runs on the agent's default Reader access. None of them require an additional role assignment to start. When a specific read is denied, a skill may ask the user to grant temporary access, but it never assigns roles itself.

## What this means

- Coverage equals the agent's existing read scope. A skill analyzes only the subscriptions and resource groups this agent was given when it was created.
- There is no tenant wide discovery. If a subscription is outside the agent's scope, the skill does not see it. To widen coverage, widen the agent's scope. That is a separate administrative action and is not a prerequisite for any skill.

## Requesting temporary access, never assigning it

A skill starts within the agent's existing read access. If a specific read is denied in some scope, the skill may ask the user to grant temporary, time bound access to that scope. It explains what it needs to read and why, then waits for the user to decide.

A skill never performs the role assignment itself. These skills have no write or role management tools and stay read only throughout. Granting access is always the user's action, done out of band. The user might activate an eligible role through PIM or add a temporary Reader assignment and remove it once the review is done. Elevation is the user granting temporary access, not a role assignment the skill makes.

If the user declines, or does not grant access, the skill skips the denied check, records it in the report as not assessed because of insufficient access, and continues with everything it can read.

## Reads used, all covered by Reader

- Subscription enumeration: the list of subscriptions the identity can see.
- Resource enumeration through Azure Resource Graph, which reads across every accessible subscription in one query.
- Azure Monitor metrics, alert rules, action groups, and diagnostic settings.
- Azure Resource Health and Service Health advisories.
- Azure Advisor recommendations.
- Resource provider read endpoints on Azure Resource Manager (for example Key Vault properties, backup vault items, and quota usage).

Some data planes need their own read role rather than management plane Reader. Key Vault secret and certificate metadata, for example, is readable with a Key Vault Reader or a data plane list permission. Where a skill needs one of these, its checks catalog says so, and the skill treats a denial as not assessed rather than a failure.

## Identity setup for the Python tools

The Python tools call Azure Resource Manager with the agent managed identity. Enable managed identity with the ARM scope on each tool in the Identity tab when you create it in the Builder. When the agent carries more than one managed identity, pin the capable one by setting AZURE_CLIENT_ID in the runtime so DefaultAzureCredential resolves it, rather than falling back to an under scoped identity.

## The rule every skill keeps

Read only throughout. A skill proposes recommendations and provides operator ready commands, but a human reviews and runs anything that changes or deletes a resource. The agent runs none of them.
