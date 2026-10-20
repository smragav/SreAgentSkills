# Scenario coverage for deprecation-retirement-tracker

Category: Resource Organization. Scenarios sourced from the customer scenario battery at https://github.com/alsanch/azure-sre-agent-scenarios.

Each scenario below is a customer asked use case routed to this skill as the closest fit. Status values:

- Covered: the skill's existing checks and tools answer the scenario.
- Partial: the skill answers part of it; follow the prompt for the remainder with read only queries.
- Added: new guided prompt, answered with read only Azure Resource Graph, Azure Monitor, Activity Log or Cost Management queries following this skill's Workflow. No Python tool backs it yet.

Treat the prompts as starting points and adapt them to the environment. The source marks the scenarios as not all validated against Azure SRE Agent. Keep every run read only, name the resource and scope behind each finding, and report a denied read as not assessed rather than as a pass.

| Scenario | Status | Mode | Frequency | Time saved |
| --- | --- | --- | --- | --- |
| AI model inventory & retirement lifecycle | Partial | Scheduled | Weekly | High |

## AI model inventory & retirement lifecycle

Status: Partial. Source category: Resource Organization.

Inventories all deployed Azure OpenAI and AI Foundry model deployments across subscriptions, cross-references each model and version against the official Microsoft model retirement schedule, and flags deployments that are already deprecated, approaching retirement, or running on a version with a known successor. Helps teams plan model migrations proactively and avoid service disruptions when deprecated models stop accepting requests.

Sample prompt:

> List all Azure OpenAI and AI Foundry model deployments across all subscriptions. For each, show: resource name, resource group, model name, model version, deployment name, and deployment date. Cross-reference each model and version against the official retirement schedule at https://learn.microsoft.com/en-us/azure/foundry-classic/openai/concepts/model-retirement-schedule. Classify each deployment as: (1) 'Retired', model version past its retirement date, (2) 'Retiring soon', retirement date within the next 90 days, (3) 'Current', no retirement date announced or retirement date > 90 days away. For retired and retiring-soon models, show the retirement date, recommended replacement model/version, and the number of days until retirement. Summarize total deployments by status.

Mode: Scheduled. Frequency: Weekly. Time saved: High.
