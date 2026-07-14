# Checks catalog

Privileged access signals read from Azure role assignments, covered by Reader (which includes read on Microsoft.Authorization). The scan tool applies these. Principal display names and guest status need a Microsoft Entra read; without it the report shows the principal id and type.

For each finding the tool records: principal (id and type), role, scope, subscription, the issue, a severity, and the recommended change.

## Read the assignments

```
az role assignment list --subscription <id> --all -o json
```

or the raw endpoint the tool uses:

```
az rest --method GET --url "https://management.azure.com/subscriptions/<id>/providers/Microsoft.Authorization/roleAssignments?api-version=2022-04-01"
```

Classic administrators:

```
az rest --method GET --url "https://management.azure.com/subscriptions/<id>/providers/Microsoft.Authorization/classicAdministrators?api-version=2015-07-01"
```

## Privileged roles the tool keeps

- Owner: 8e3af657-a8ff-443c-a75c-2fe8c4bcb635
- Contributor: b24988ac-6180-42a0-ab88-20f7382dd24c
- User Access Administrator: 18d7d88d-d35e-4fb5-a5c3-7773c20a72d9
- Role Based Access Control Administrator: f58310d9-a9f6-439a-9e8d-f62e7b41a168

Non privileged roles are not reported.

## Signals and severity

- Owner sprawl (High): more than the threshold of Owner assignments at subscription scope (three by default). Fix: reduce standing Owners; grant Owner just in time through Privileged Identity Management.
- Service principal with high privilege (High): a service principal holding Owner, User Access Administrator, or Role Based Access Control Administrator. Fix: scope it down to the least privilege it needs, and prefer a resource scoped role over a subscription wide one.
- Classic administrator (High): a Co Administrator or Service Administrator remains. Fix: migrate to Azure role based access control and remove the classic administrator.
- Privileged role at management group scope (High): Owner or an access administration role assigned at management group scope has a wide blast radius. Fix: confirm it is intended and scope it down where possible.
- Assignment to a deleted or unknown principal (Medium): the principal type is Unknown, so the assignment likely points at a deleted identity. Fix: remove the stale assignment.
- Standing Owner for a user (Medium): a user holds Owner at subscription scope as standing access. Fix: move to just in time Owner through Privileged Identity Management.
- Service principal with Contributor (Low): a service principal holds Contributor at subscription scope. Fix: confirm it needs that breadth; scope it down where possible.

A principal can produce more than one finding when it holds more than one privileged assignment.
