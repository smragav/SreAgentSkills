---
name: identity-access-hygiene
description: Use when the user asks about identity hygiene, access reviews, least privilege, role assignments, Owner sprawl, overprivileged principals, service principals with high privilege, classic administrators, or standing access. Reads Azure role assignments across the subscriptions the agent can read, flags privileged access risks, and produces a self contained HTML access hygiene report.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# Identity and Access Hygiene

This skill reviews privileged access across the subscriptions this agent can read. It reads the Azure role assignments, flags Owner sprawl, service principals holding high privilege, standing Owner access for users, classic administrators, and assignments to deleted principals, and produces a single self contained HTML report. Least privilege and clean access are foundational security controls, and this makes the drift visible. It runs on demand or as a scheduled sweep.

## When to use this skill

Use this skill when the user asks to:

- Review identity hygiene, access, or least privilege.
- Find Owner sprawl, overprivileged service principals, or standing privileged access.
- Prepare for an access review or find classic administrators to retire.

## Operating principles

- Read only. This skill reads role assignments. It never grants, changes, or removes access; it reports the risk and the recommended change.
- Default Reader scope. It reads assignments across the subscriptions this agent can read. Principal display names and guest status need Microsoft Entra, so the report shows the principal id and type and notes where a directory read would add detail. See references/permissions-and-scope.md.
- Evidence first. Every finding names the principal (id and type), the role, the scope, a severity, and the recommended change.

## Workflow

The scan tool (tools/identity_access.py) and the shared report renderer (tools/report_render.py) are bundled with this skill. Run them with RunInTerminal using the Python in the agent runtime. Both authenticate with the agent managed identity.

### Phase 1: Read the privileged assignments

1. Run python tools/identity_access.py with RunInTerminal. It reads the role assignments and classic administrators across the accessible subscriptions, keeps the privileged roles (Owner, User Access Administrator, Role Based Access Control Administrator, and Contributor for service principals), classifies each against references/checks-catalog.md, and prints a report_data object as JSON.
2. Owner sprawl at subscription scope, service principals holding Owner, and classic administrators are the items worth acting on first.

### Phase 2: Produce the report

1. Pipe the scan into the renderer: python tools/identity_access.py | python tools/report_render.py with RunInTerminal. It writes the self contained HTML report and returns the path. Store it with SaveFileToBlob for a link.
2. Present the report, then a short inline summary: subscriptions with Owner sprawl, service principals with high privilege, classic administrators, and any scope not assessed.

## Scenario coverage

This skill also answers 5 customer scenarios in the Identity and Access category. Open references/scenarios.md when the ask matches one of them: it holds the sample prompt, the run mode, and whether the skill covers it with built in checks or a guided read only prompt.

## Expected output

- Primary: a self contained HTML access hygiene report, covering findings by severity and by role, and the full table naming the principal, role, scope, and recommended change.
- Inline: Owner sprawl, high privilege service principals, and classic administrators.
- Every finding names the principal (id and type), the role, the scope, a severity, and the recommended change. Nothing is changed; recommendations are for a human to apply, ideally with just in time access through Privileged Identity Management.
