---
name: blameless-postmortem-writer
description: Use when the user asks for a postmortem, a post incident review, an incident retrospective, a root cause writeup, or a blameless RCA document after an incident. Assembles the timeline, impact, root cause, contributing factors, and action items into a blameless postmortem, and produces a clean self contained HTML document ready to edit and share.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# Blameless Postmortem Writer

This skill turns the facts of a resolved incident into a blameless postmortem. It gathers the timeline and impact, states the root cause in terms of systems rather than people, captures contributing factors and what to change, and produces a clean self contained HTML document ready to edit and share. It removes the paperwork friction so teams actually write postmortems, which is where the durable reliability gains come from. It runs on demand after an incident.

## When to use this skill

Use this skill when the user asks to:

- Write a postmortem, a post incident review, or an incident retrospective.
- Turn an incident timeline into a shareable writeup with action items.
- Produce a blameless root cause document after an incident is resolved.

## Operating principles

- Blameless. Describe what the system did and why it was possible, not who did it. Replace names of people with roles and systems. Assume everyone acted reasonably with the information they had.
- Read only. This skill reads incident evidence and writes a document. It changes nothing in Azure.
- Evidence based and honest. The timeline and impact come from evidence. Where a fact is unknown, say so and make finding it an action item rather than guessing.

## Workflow

The renderer (tools/postmortem_render.py) is bundled with this skill. Run it with RunInTerminal using the Python in the agent runtime; it uses only the standard library.

### Phase 1: Gather the facts

1. Collect the incident facts from the user, from a prior incident report if the incident-triage-rca skill produced one, and from the Activity Log and Resource Health for the affected resources with RunAzCliReadCommands. Fill the structure in references/postmortem-template.md.
2. Build the timeline from first symptom to resolution: detection, escalation, the key diagnostic steps, the mitigation, and the all clear. Note detection time and time to mitigate.

### Phase 2: Write it blameless

Follow references/writing-guide.md. State the root cause as a chain of contributing conditions, not a single human error. Separate the trigger from the underlying weakness. Write action items that are specific, owned, and dated, and that address the underlying weakness, not just the trigger.

### Phase 3: Produce the document

1. Assemble the postmortem object described in references/postmortem-template.md and pipe it into python tools/postmortem_render.py with RunInTerminal. It writes a clean self contained HTML document and returns the path. Store it with SaveFileToBlob for a link.
2. Present the document, then a short inline summary: the incident in one line, the impact, the root cause, and the action items with owners.

## Scenario coverage

This skill also answers 1 customer scenario in the Management category (post incident review automation). Open references/scenarios.md when the ask matches it: it holds the sample prompt, the run mode, and whether the skill covers it with built in checks or a guided read only prompt.

## Expected output

- Primary: a self contained HTML postmortem with summary, impact, timeline, root cause, contributing factors, detection and resolution, lessons, and action items.
- Inline: the one line summary, impact, root cause, and the action items with owners and dates.
- The language stays blameless throughout: systems and conditions, not individuals. Unknown facts are named and turned into action items rather than guessed.
