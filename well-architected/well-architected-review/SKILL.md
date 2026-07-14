---
name: well-architected-review
description: Use when the user asks for a Well-Architected review, a WAF assessment, a Well-Architected Framework scorecard, a pillar review, or "how well architected are we". Runs a curated set of high signal checks across all five Well-Architected pillars (Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency), scores each pillar, and produces a single self contained HTML scorecard.
tools:
  - RunAzCliReadCommands
  - RunInTerminal
  - SaveFileToBlob
---

# Well-Architected Review

This skill produces a single Well-Architected Framework scorecard across the resources this agent can read. It runs a curated set of high signal checks for each of the five pillars (Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency), scores each pillar from 0 to 100, and produces one self contained HTML scorecard as the primary output. It is the front door to the whole suite: it gives the pillar level view a leadership audience wants, and it points at the deep dive skills for the detail. It runs on demand or as a scheduled sweep.

## When to use this skill

Use this skill when the user asks to:

- Run a Well-Architected review or a Well-Architected Framework assessment.
- See a pillar level scorecard across Reliability, Security, Cost, Operational Excellence, and Performance.
- Get a single posture summary that then routes to the detailed skills.

## Operating principles

- Read only. This skill reads configuration. It never changes a resource; it scores posture and recommends where to dig in.
- Default Reader scope. It scores what this agent can read. If a check is denied, it is skipped and noted, not failed. See references/permissions-and-scope.md.
- Roll up, not replacement. It runs a small, curated set of checks per pillar for the score. For the full detail behind a pillar, it points at the dedicated skill (for example reliability-posture-review or network-exposure-review).

## Workflow

The assessment tool (tools/waf_assess.py) and the shared report renderer (tools/report_render.py) are bundled with this skill. Run them with RunInTerminal using the Python in the agent runtime. Both authenticate with the agent managed identity.

### Phase 1: Assess the pillars

1. Run python tools/waf_assess.py with RunInTerminal. It runs the curated checks in references/checks-catalog.md across accessible subscriptions with Azure Resource Graph, computes a pass ratio per check, scores each pillar as a weighted average, and prints a report_data object as JSON.
2. Each check that has failing resources becomes a finding tagged with its pillar, so the table explains the scores.

### Phase 2: Produce the scorecard

1. Pipe the assessment into the renderer: python tools/waf_assess.py | python tools/report_render.py with RunInTerminal. It writes the self contained HTML scorecard and returns the path. Store it with SaveFileToBlob for a link.
2. Present the scorecard, then a short inline summary: the five pillar scores and ratings, the weakest pillar, the highest impact findings, and which deep dive skill to run next for the weakest pillars.

## Expected output

- Primary: a self contained HTML Well-Architected scorecard with a score and rating for each of the five pillars, a pillar score chart, and a findings table tagged by pillar.
- Inline: the five pillar scores, the weakest pillar, and the recommended deep dive skills to run next.
- Every finding is tagged with its pillar and carries the count of affected resources and a severity. The scorecard is a roll up; the dedicated skills hold the full detail.
