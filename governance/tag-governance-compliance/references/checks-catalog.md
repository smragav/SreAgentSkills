# Checks catalog

Tag compliance against a required standard, read with Azure Resource Graph and covered by Reader.

For each finding the tool records: resource id, resource type, subscription, resource group, the missing tags, a severity, and the recommended values.

## The required standard

The default required tags are owner, environment, and cost center. Override them by passing a comma separated list to the tool, for example:

```
python tools/tag_compliance.py owner,environment,cost-center,application
```

Choose the set your organisation actually enforces. A small, enforced standard beats a long, ignored one.

## Enumerate resources and tags

```
az graph query -q "resources | project name, id, type, resourceGroup, subscriptionId, tags" --first 1000
```

The tool reads the tags bag on each resource. Resource groups carry their own tags and are checked separately from resources where you extend the scan; the default run covers resources.

## Tolerant key matching

Tag keys are matched case insensitively and with separators removed, so a single requirement is met by any common spelling:

- cost-center is satisfied by CostCenter, cost_center, or costcenter.
- owner is satisfied by Owner or OWNER.

This avoids flagging a resource that is tagged correctly but with a different key style. Values are not validated by default; the requirement is presence. Add value checks by hand where a tag must match an allowed list (for example environment in prod, nonprod, or dev).

## Severity

- High: the owner tag is missing. Without an owner there is no accountable team for the resource, which blocks both incident response and chargeback.
- Medium: any other required tag is missing (for example environment or cost center).

A resource missing more than one required tag appears once, listing them, at the highest severity among them.

## Fixing and enforcing

- Fix: apply the missing tags with the correct values. Set owner to the accountable team, environment to the deployment stage, and cost center to the billing code.
- Enforce durably: use Azure Policy to require the tags and, where appropriate, inherit them from the resource group or subscription. Policy is the lasting fix; a one time tagging pass drifts again without it.
