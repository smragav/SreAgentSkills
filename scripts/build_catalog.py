"""Build the customer facing catalogs and explicit scenario routing."""

import json
import re
import sys
from collections import Counter
from pathlib import Path

from build_scenario_skills import (
    RETAINED_SKILLS, scenario_sources, workflow_definitions,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "tools"))
from report_render import render_html
from validate_library import metadata

LABELS = {
    "billing-cost": "Billing and Cost", "identity-access": "Identity and Access",
    "resource-organization": "Resource Organization", "network": "Network",
    "security": "Security", "management": "Management", "governance": "Governance",
    "platform-automation": "Platform Automation",
}

CSS = """
:root{color-scheme:dark;--bg:#0d1117;--card:#161b22;--border:#30363d;--text:#e6edf3;--muted:#8b949e;--accent:#58a6ff;--good:#3fb950}
:root[data-theme="light"]{color-scheme:light;--bg:#fff;--card:#f6f8fa;--border:#d0d7de;--text:#1f2328;--muted:#59636e;--accent:#0969da;--good:#1a7f37}
*{box-sizing:border-box}body{max-width:1200px;margin:auto;padding:2rem;font:15px/1.6 system-ui,"Segoe UI",sans-serif;background:var(--bg);color:var(--text)}
a{color:var(--accent)}a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
header{display:flex;justify-content:space-between;gap:1rem;align-items:start}h1{font-size:2rem;margin:0}h2{font-size:1.1rem;margin-top:0}
nav{margin:1rem 0;display:flex;flex-wrap:wrap;gap:1rem}.muted{color:var(--muted)}.notice{padding:1rem;border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:8px;margin:1.5rem 0;background:var(--card)}
.filters{display:flex;flex-wrap:wrap;gap:1rem;margin:1.5rem 0}.filters label{display:flex;flex-direction:column;gap:.3rem;flex:1;min-width:180px}
input,select,button{font:inherit;color:var(--text);background:var(--card);border:1px solid var(--border);border-radius:6px;padding:.6rem}
button{cursor:pointer}#cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:1rem}.skill{border:1px solid var(--border);border-radius:10px;padding:1.25rem;background:var(--card)}
.badge{color:var(--good);font-size:.85rem}.links{display:flex;flex-wrap:wrap;gap:1rem}details{margin:1rem 0}summary{cursor:pointer}li{margin:.4rem 0}
footer{margin-top:2rem;border-top:1px solid var(--border);padding-top:1rem;color:var(--muted)}@media(max-width:600px){body{padding:1rem}header{flex-direction:column}}
@media print{header button,.filters,nav{display:none}body{max-width:none;background:white;color:black}#cards{display:block}.skill{break-inside:avoid;margin:1rem 0}a{color:inherit}}
"""

JS = """
const records=JSON.parse(document.getElementById('skill-data').textContent);
const cards=document.getElementById('cards');
const category=document.getElementById('category');
const search=document.getElementById('search');
function node(tag,text){const el=document.createElement(tag);if(text!==undefined)el.textContent=text;return el;}
function link(label,path){const el=node('a',label);el.setAttribute('href',path);return el;}
for(const label of [...new Set(records.map(r=>r.category_label))].sort()){const option=node('option',label);option.value=label;category.appendChild(option);}
function render(){
 const q=search.value.toLowerCase().trim();
 const shown=records.filter(r=>(!category.value||r.category_label===category.value)&&(!q||JSON.stringify(r).toLowerCase().includes(q)));
 cards.textContent='';
 for(const r of shown){
  const card=node('article');card.className='skill';card.dataset.slug=r.slug;
  const badge=node('p',r.category_label);badge.className='badge';card.appendChild(badge);
  card.appendChild(node('h2',r.title));card.appendChild(node('p',r.description));
  if(r.mode)card.appendChild(node('p','Suggested mode: '+r.mode+'. Cadence: '+r.frequency+'.'));
  const links=node('div');links.className='links';links.appendChild(link('Playbook',r.path+'/SKILL.md'));
  if(r.workflow)links.appendChild(link('Evidence workflow',r.path+'/references/workflow.md'));
  if(r.workflow)links.appendChild(link('Output contract',r.path+'/references/output-contract.json'));
  if(r.sample)links.appendChild(link('Synthetic example',r.sample));
  card.appendChild(links);
  if(r.analysis&&r.analysis.length){
   const detail=node('details');detail.appendChild(node('summary','Analysis and limits'));const list=node('ul');
   for(const rule of r.analysis)list.appendChild(node('li',rule));
   for(const limit of r.limitations)list.appendChild(node('li','Limit: '+limit));
   detail.appendChild(list);card.appendChild(detail);
  }
  if(r.sources&&r.sources.length){const detail=node('details');detail.appendChild(node('summary','Microsoft sources'));const list=node('ul');
   for(const source of r.sources){const li=node('li');li.appendChild(link(source.title,source.url));list.appendChild(li);}
   detail.appendChild(list);card.appendChild(detail);
  }
  cards.appendChild(card);
 }
 document.getElementById('count').textContent=shown.length+' of '+records.length+' skills shown';
 if(!shown.length)cards.appendChild(node('p','No skills match these filters.'));
}
for(const control of [category,search])control.addEventListener('input',render);
document.getElementById('themeToggle').addEventListener('click',()=>{
 const light=document.documentElement.getAttribute('data-theme')!=='light';
 document.documentElement.setAttribute('data-theme',light?'light':'dark');
 try{localStorage.setItem('theme',light?'light':'dark');}catch(e){}
 document.getElementById('themeToggle').textContent=light?'Dark theme':'Light theme';
});
document.getElementById('themeToggle').textContent=document.documentElement.getAttribute('data-theme')==='light'?'Dark theme':'Light theme';
render();
"""


def catalog_page(records: list[dict]) -> str:
    title = "Azure SRE Agent skill library"
    data = json.dumps(records, ensure_ascii=True).replace("<", "\\u003c")
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<script>try{{if(localStorage.getItem('theme')==='light')document.documentElement.setAttribute('data-theme','light');}}catch(e){{}}</script>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Customer facing catalog of 105 Azure SRE Agent skills across eight categories.">
<title>{title}</title><style>{CSS}</style></head><body>
<header><div><h1>{title}</h1><p class="muted">105 skills across eight categories.</p><p class="muted">Created for the scenarios in <a href="https://github.com/alsanch/azure-sre-agent-scenarios">alsanch/azure-sre-agent-scenarios</a>, plus additional scenarios. The initial skills came from <a href="https://github.com/onsenturk/SreAgentExtensions">onsenturk/SreAgentExtensions</a>.</p></div>
<button id="themeToggle" type="button" aria-label="Switch between light and dark theme">Light theme</button></header>
<nav aria-label="Library navigation"><a href="index.html">Library</a><a href="scenario-index.md">All skills</a><a href="README.md">Setup and validation</a></nav>
<section class="notice" aria-label="Validation and approval boundary"><strong>Evidence first, approval before action.</strong>
Local tests, output contracts and packaging checks do not establish live Azure validation.
Workflows collect scoped evidence or prepare drafts. Changes, schedules, uploads and messages require separate explicit approval.
Reports need customer sharing review. Examples contain synthetic data, not findings about a customer.
<p><a href="shared/references/customer-sharing.md">Sharing checklist</a> |
<a href="shared/references/assessment-contract.md">Assessment states</a> |
<a href="THIRD-PARTY-NOTICES.md">License notices</a></p></section>
<section class="filters" aria-label="Skill filters">
<label>Search<input id="search" type="search" placeholder="Scenario, service or operation"></label>
<label>Category<select id="category"><option value="">All categories</option></select></label>
</section><p id="count" role="status" aria-live="polite"></p><main id="cards"></main>
<footer>These are operational workflows, not Microsoft certification or guaranteed service outcomes. No tracking or external assets.</footer>
<script id="skill-data" type="application/json">{data}</script><script>{JS}</script></body></html>
"""


def update_retained_routing(path: Path, sources: list[dict]) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace("Default Reader scope.", "Approved read scope.")
    text = text.replace("Both authenticate with the agent managed identity.",
                        "The collector uses the configured identity; the local renderer does not authenticate to Azure.")
    text = text.replace("which already has azure-identity and requests.",
                        "after verifying that the host provides approved azure-identity and requests packages.")
    reference = path.parent / "references" / "scenarios.md"
    matching = []
    if reference.exists():
        old = reference.read_text(encoding="utf-8")
        matching = [source for source in sources if source["title"].casefold() in old.casefold()]
        lines = ["# Related skills", "",
                 "This skill covers only its documented checks. For the following topics, load the related "
                 "skill; a routing entry does not imply that this skill implements that scenario.", ""]
        lines.extend(f"- {source['title']}: load `{source['slug']}` ({source['category_label']})."
                     for source in matching)
        lines.extend(["", "For the complete list, consult the repository skill index. "
                      "Related skills include collection commands, decision rules, permissions and output contracts.", "",
                      "## Sources", "",
                      "- [SRE Agent skill discovery](https://learn.microsoft.com/azure/sre-agent/skills).", ""])
        reference.write_text("\n".join(lines), encoding="utf-8")
    section = (
        "## Scenario coverage\n\n"
        "This skill implements its documented checks, not every related scenario. "
        "Use the related skills for their complete evidence workflows. "
        + ("See [scenario routing](./references/scenarios.md).\n\n" if reference.exists() else "\n\n")
    )
    if "## Scenario coverage" in text:
        text = re.sub(r"## Scenario coverage\n.*?(?=\n## |\Z)", section, text, flags=re.DOTALL)
    shared = """## Assessment and customer sharing

Confirm the explicit customer scope and UTC window before collection. Accessible resources are not automatically approved scope. For a tool that enumerates all visible subscriptions, use an identity restricted to the approved scope or the related skill's scoped commands.

Follow [assessment states and limits](./references/assessment-contract.md), [permissions](./references/permissions-and-scope.md), and [customer sharing review](./references/customer-sharing.md), bundled during deployment. The shared renderer produces a sanitized draft by default; `--include-identifiers` requires an explicitly approved customer audience. Review custom exports with the same checklist.

Configure the host using [governance settings](./references/governance.json). General terminal access is not inherently read only. Never apply changes, schedule work, upload files or send messages without separate explicit approval.
"""
    text = re.sub(r"\n*## Assessment and customer sharing\n.*?(?=\n## |\Z)", "", text, flags=re.DOTALL)
    text = text.rstrip() + "\n\n" + shared
    path.write_text(text, encoding="utf-8")


def synthetic_report(path: Path, info: dict) -> None:
    report = {
        "title": info["title"],
        "subtitle": "Synthetic demonstration of the report layout. This is not a customer assessment.",
        "assessment_status": "Not assessed",
        "meta": {"window": "Illustrative only", "scope": "Synthetic sample; no Azure collection",
                 "source": "Synthetic fixture"},
        "summary_cards": [{"label": "Demonstration", "value": "Synthetic"},
                          {"label": "Live Azure assessment", "value": "Not performed"}],
        "findings": {"columns": ["resource", "state", "evidence", "recommendation", "severity"],
                     "rows": [{"resource": "example-resource", "state": "Not assessed",
                               "evidence": "No customer data or live service calls were used.",
                               "recommendation": "Run the scoped playbook and review actual evidence.",
                               "severity": "Info"}]},
        "method_notes": ["This sample demonstrates presentation only, not the analyzer's control coverage.",
                         "Observed, Needs attention, Not applicable and Not assessed must remain distinct.",
                         "Review the actual evidence and destination before sharing a real report."],
        "sources": [{"title": "Azure SRE Agent skills", "url": "https://learn.microsoft.com/azure/sre-agent/skills"}],
    }
    path.write_text(render_html(report), encoding="utf-8")


def build() -> None:
    sources = scenario_sources(ROOT)
    definitions = workflow_definitions(ROOT)
    source_by_slug = {source["slug"]: source for source in sources}
    if set(definitions) != set(source_by_slug):
        raise ValueError("Every scenario requires exactly one workflow definition.")
    skills = sorted(ROOT.glob("*/*/SKILL.md"))
    if len(skills) != 105 or {path.parent.name for path in skills} != set(source_by_slug) | RETAINED_SKILLS.keys():
        raise ValueError("Expected exactly 105 skills.")
    records = []
    for path in skills:
        info = metadata(path)
        slug = info["name"]
        source = source_by_slug.get(slug)
        definition = definitions.get(slug)
        category = path.parent.parent.name
        title = source["title"] if source else re.search(r"^# (.+)$", info["body"], re.MULTILINE).group(1)
        sample_paths = sorted(path.parent.glob("sample-report/*.html"))
        record = {"slug": slug, "title": title, "description": info["description"],
                  "category": category, "category_label": LABELS[category],
                  "path": path.parent.relative_to(ROOT).as_posix(),
                  "workflow": bool(source), "sample": sample_paths[0].relative_to(ROOT).as_posix() if sample_paths else "",
                  "mode": source["mode"] if source else "", "frequency": source["frequency"] if source else "",
                  "analysis": definition["analysis"] if definition else [],
                  "limitations": definition["limitations"] if definition else [],
                  "sources": definition["sources"] if definition else []}
        records.append(record)
        if not source:
            update_retained_routing(path, sources)
            for sample in sample_paths:
                synthetic_report(sample, record)
    if len(records) != 105:
        raise ValueError(f"Expected 105 skills before publishing catalogs, found {len(records)}.")
    (ROOT / "catalog" / "skills.json").write_text(json.dumps(records, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    (ROOT / "index.html").write_text(catalog_page(records), encoding="utf-8")
    lines = ["# Skill index", "", "All 105 skills by category. They were created for the scenarios in "
             "[alsanch/azure-sre-agent-scenarios](https://github.com/alsanch/azure-sre-agent-scenarios) and also cover "
             "additional scenarios. The initial skills came from Onur Senturk's repository, "
             "[onsenturk/SreAgentExtensions](https://github.com/onsenturk/SreAgentExtensions). Workflow availability is not live Azure validation. "
             "See [license notices](./THIRD-PARTY-NOTICES.md).", ""]
    for category, label in LABELS.items():
        lines.extend([f"## {label}", "", "| Skill | Description | Suggested mode | Suggested cadence |",
                      "| --- | --- | --- | --- |"])
        for record in sorted((item for item in records if item["category"] == category), key=lambda item: item["title"].casefold()):
            summary = " ".join(record["description"].split())
            summary = summary.split(". ", 1)[0].rstrip(".") + "." if ". " in summary else summary
            summary = summary.replace("|", "/")
            lines.append(f"| {record['title']} | [{record['slug']}](./{category}/{record['slug']}/SKILL.md): {summary} | "
                         f"{record['mode'] or 'n/a'} | {record['frequency'] or 'n/a'} |")
        lines.append("")
    lines.extend(["## Validation boundary", "", "Skills with an evidence workflow contain collection commands, analysis rules, "
                  "output fields, permissions, limitations and Microsoft sources. Local validators check all skill "
                  "bundles and synthetic evidence contracts. Customer identity, API execution, real evidence and "
                  "operational outcomes require a separately authorized smoke test.", "", "## Sources", "",
                  "- [SRE Agent skills](https://learn.microsoft.com/azure/sre-agent/skills).", ""])
    (ROOT / "scenario-index.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"skills": len(records), "categories": dict(Counter(record["category"] for record in records))}))


if __name__ == "__main__":
    build()
