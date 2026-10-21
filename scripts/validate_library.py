"""Validate source and deployed skill structure without contacting Azure."""

import argparse
import json
import posixpath
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

from build_scenario_skills import (
    EXTENSION_PROVENANCE, RETAINED_SKILLS, scenario_sources, scenario_summary, workflow_definitions,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "tools"))
from scenario_contract import validate_result

ALLOWED_TOOLS = {"RunAzCliReadCommands", "RunInTerminal", "SaveFileToBlob",
                 "CreateScheduledMonitoringTask", "UpdateScheduledTask", "ListScheduledTasks",
                 "PauseScheduledTask", "ResumeScheduledTask", "CancelScheduledTask", "GetTaskExecutionHistory"}


def metadata(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
    if not match:
        raise ValueError(f"{path.relative_to(ROOT)}: missing frontmatter")
    header = match.group(1)
    result = {}
    for key in ("name", "description"):
        field = re.search(rf"^{key}:\s*(.+)$", header, re.MULTILINE)
        if not field:
            raise ValueError(f"{path.relative_to(ROOT)}: missing {key}")
        value = field.group(1).strip()
        if value in ("|", "|-", ">", ">-"):
            remainder = header[field.end():]
            lines = []
            for line in remainder.splitlines():
                if line and not line[0].isspace():
                    break
                if line.strip():
                    lines.append(line.strip())
            value = ("\n" if value.startswith("|") else " ").join(lines)
            result[key] = value
        else:
            result[key] = json.loads(value) if value.startswith('"') else value.strip("'")
    tool_match = re.search(r"^tools:\s*(?:\[(.*?)\]|((?:\r?\n[ \t]+-[^\n]+)+))", header, re.MULTILINE)
    if not tool_match:
        raise ValueError(f"{path.relative_to(ROOT)}: explicit tools required")
    if tool_match.group(1) is not None:
        tools = [part.strip().strip("'\"") for part in tool_match.group(1).split(",") if part.strip()]
    else:
        tools = re.findall(r"^\s+-\s+([A-Za-z0-9_]+)\s*$", tool_match.group(2), re.MULTILINE)
    result["tools"] = tools
    result["body"] = text[match.end():]
    return result


def bundle_files(skill: Path) -> dict[str, Path]:
    bundle = {"SKILL.md": skill / "SKILL.md"}
    for directory in (ROOT / "shared" / "references", ROOT / "shared" / "tools",
                      skill / "references", skill / "tools"):
        if directory.exists():
            for path in directory.iterdir():
                if path.is_file() and not path.name.startswith("test_") and path.suffix != ".pyc":
                    bundle[f"{directory.name}/{path.name}"] = path
    for path in skill.iterdir():
        if path.is_file() and path.name != "SKILL.md" and not path.name.startswith("test_"):
            bundle[path.name] = path
    return bundle


def fixture(source: dict, definition: dict, state: str) -> dict:
    assessed = state != "Not assessed"
    return {
        "scenario_id": source["slug"],
        "scope": {"subscription_ids": ["00000000-0000-0000-0000-000000000000"]},
        "assessed_at": "2026-10-21T00:00:00Z",
        "assessment_status": "Complete" if assessed else "Not assessed",
        "coverage": {"expected_checks": 1, "assessed_checks": 1 if assessed else 0, "truncated": False},
        "findings": [{
            "id": "synthetic-001", "status": state,
            "severity": "Medium" if state == "Needs attention" else "Info",
            "evidence": [{"source": "Synthetic test fixture, not Azure data",
                          "collected_at": "2026-10-21T00:00:00Z"}] if assessed else [],
            "scenario_data": {field: "Synthetic evidence" if assessed else None
                              for field in definition["output_fields"]},
        }],
        "limitations": [] if assessed else ["Synthetic access denial: required evidence unavailable."],
    }


def validate() -> dict:
    sources = scenario_sources(ROOT)
    definitions = workflow_definitions(ROOT)
    source_by_slug = {source["slug"]: source for source in sources}
    source_slugs = set(source_by_slug)
    extension_slugs = {source["slug"] for source in sources if source["provenance"] == EXTENSION_PROVENANCE}
    if set(definitions) != source_slugs:
        raise ValueError("Every scenario requires exactly one workflow definition.")
    skills = sorted(path for path in ROOT.glob("*/*/SKILL.md") if path.parent.parent.name != "shared")
    if len(skills) != 105:
        raise ValueError(f"Expected 105 skills, found {len(skills)}")
    names, packaged = set(), 0
    for path in skills:
        info = metadata(path)
        name = info["name"]
        if name != path.parent.name or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", name):
            raise ValueError(f"Invalid skill name or folder mismatch: {name}")
        if name in names or not info["tools"] or not set(info["tools"]) <= ALLOWED_TOOLS:
            raise ValueError(f"Duplicate name or unsupported tools: {name}")
        if not 1 <= len(info["description"]) <= 1024:
            raise ValueError(f"Invalid description length: {name}")
        expected_category = source_by_slug[name]["category"] if name in source_by_slug else RETAINED_SKILLS.get(name)
        if expected_category != path.parent.parent.name:
            raise ValueError(f"Unexpected skill or category: {name}")
        names.add(name)
        bundle = bundle_files(path.parent)
        for required in ("references/customer-sharing.md", "references/assessment-contract.md",
                         "references/permissions-and-scope.md", "references/governance.json",
                         "references/license-notices.txt", "tools/sharing.py", "tools/scenario_contract.py",
                         "tools/azure_http.py"):
            if required not in bundle:
                raise ValueError(f"{name}: missing bundled {required}")
        if name in extension_slugs and "tools/operational_analysis.py" not in bundle:
            raise ValueError(f"{name}: missing bundled tools/operational_analysis.py")
        for relative, document in bundle.items():
            if document.suffix != ".md":
                continue
            content = re.sub(r"```.*?```", "", document.read_text(encoding="utf-8"), flags=re.DOTALL)
            for link in re.findall(r"\[[^\]]+\]\(([^)\n]+)\)", content):
                target = link.split(" ", 1)[0].strip("<>").split("#", 1)[0]
                if not target or re.match(r"^[a-zA-Z]+:", target):
                    continue
                deployed = posixpath.normpath(str(Path(relative).parent / target).replace("\\", "/"))
                if deployed not in bundle:
                    raise ValueError(f"{name}: unresolved link {relative}: {target}")
        packaged += 1
    if names != source_slugs | RETAINED_SKILLS.keys() or names - source_slugs != RETAINED_SKILLS.keys():
        raise ValueError("Exactly the 22 analysis tool skills and 83 scenario workflows must be packaged.")
    fixture_checks = 0
    for source in sources:
        definition = definitions[source["slug"]]
        if len(definition["analysis"]) < 3 or len(definition["validation_cases"]) < 3:
            raise ValueError(f"Incomplete analysis or validation cases: {source['slug']}")
        if len(definition["output_fields"]) < 4 or len(definition["limitations"]) < 2:
            raise ValueError(f"Incomplete output or limits: {source['slug']}")
        if not definition["collection"] or not definition["permissions"] or not definition["sources"]:
            raise ValueError(f"Missing implementation evidence: {source['slug']}")
        for field in definition["output_fields"]:
            if not re.fullmatch(r"[a-z][a-z0-9_]*", field):
                raise ValueError(f"Invalid scenario output field: {source['slug']}:{field}")
        for item in definition["collection"]:
            if not item["command"].strip() or not item["explanation"].strip():
                raise ValueError(f"Empty evidence collector: {source['slug']}")
        for item in definition["sources"]:
            if not item["url"].startswith("https://learn.microsoft.com/") or not item["verified_on"]:
                raise ValueError(f"Missing Microsoft grounding: {source['slug']}")
        contract_path = ROOT / source["category"] / source["slug"] / "references" / "output-contract.json"
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        source_path = contract_path.with_name("scenario.json")
        if json.loads(source_path.read_text(encoding="utf-8")) != scenario_summary(source):
            raise ValueError(f"Generated scenario metadata mismatch: {source['slug']}")
        skill_text = (contract_path.parent.parent / "SKILL.md").read_text(encoding="utf-8")
        lowered = skill_text.lower()
        if ("upstream" in lowered or "scenario provenance" in lowered or "original extension" in lowered
                or "[License notices](./references/license-notices.txt)" not in skill_text):
            raise ValueError(f"Skill text must link license notices without origin labels: {source['slug']}")
        if source["provenance"] == EXTENSION_PROVENANCE and "tools/operational_analysis.py" not in skill_text:
            raise ValueError(f"Analyzer guidance missing: {source['slug']}")
        for state in ("Observed", "Needs attention", "Not assessed"):
            validate_result(fixture(source, definition, state), contract)
            fixture_checks += 1
    catalog = json.loads((ROOT / "catalog" / "skills.json").read_text(encoding="utf-8"))
    if {item["slug"] for item in catalog} != names or len(catalog) != len(names):
        raise ValueError("The published catalog must contain every skill exactly once.")
    for record in catalog:
        source = source_by_slug.get(record["slug"])
        category = source["category"] if source else RETAINED_SKILLS[record["slug"]]
        if (record["category"] != category or record["workflow"] is not bool(source)
                or record["path"] != f"{category}/{record['slug']}"
                or {"kind", "provenance"} & record.keys()):
            raise ValueError(f"Catalog routing mismatch: {record['slug']}")
        if not (ROOT / record["path"] / "SKILL.md").is_file():
            raise ValueError(f"Catalog playbook target is missing: {record['slug']}")
        if record["sample"] and not (ROOT / record["sample"]).is_file():
            raise ValueError(f"Catalog sample target is missing: {record['slug']}")

    class PageLinks(HTMLParser):
        def handle_starttag(self, tag, attrs):
            values = dict(attrs)
            if tag == "script" and values.get("src"):
                raise ValueError("Catalogs must not load external scripts.")
            for key in ("href", "src"):
                link = values.get(key, "")
                if link and not re.match(r"^[a-zA-Z]+:", link) and not (ROOT / link.split("#")[0]).exists():
                    raise ValueError(f"Unresolved catalog link: {link}")

    for filename in ("index.html",):
        page = (ROOT / filename).read_text(encoding="utf-8")
        PageLinks().feed(page)
        embedded = re.search(r'<script id="skill-data" type="application/json">(.*?)</script>', page, re.DOTALL)
        if not embedded or json.loads(embedded.group(1)) != catalog:
            raise ValueError(f"Embedded catalog does not match published skill metadata: {filename}")
        lowered = page.lower()
        if any(word in lowered for word in ("upstream", "retained assessment", "original extension",
                                            'id="provenance"', ">provenance<")):
            raise ValueError(f"Catalog exposes origin labels: {filename}")
    index = (ROOT / "scenario-index.md").read_text(encoding="utf-8")
    routes = re.findall(r"\[([a-z0-9-]+)\]\(\./([^)\n]+/SKILL\.md)\)", index)
    if len(routes) != 105 or {slug for slug, _ in routes} != names:
        raise ValueError("The skill index must route every skill exactly once.")
    for slug, route in routes:
        category = source_by_slug[slug]["category"] if slug in source_by_slug else RETAINED_SKILLS[slug]
        if route != f"{category}/{slug}/SKILL.md":
            raise ValueError(f"Skill index routing mismatch: {slug}")
    if any(word in index.lower() for word in ("upstream", "original extension", "retained assessment")):
        raise ValueError("The skill index exposes origin labels.")
    return {"validated_at": datetime.now(timezone.utc).isoformat(), "validation_level": "Local",
            "skills": len(skills), "analysis_tool_skills": len(skills) - len(source_slugs),
            "scenario_workflows": len(source_slugs), "bundle_checks": packaged,
            "evidence_fixture_checks": fixture_checks, "live_azure_validation": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional validation JSON path inside this repository.")
    arguments = parser.parse_args()
    result = validate()
    if arguments.output:
        target = arguments.output.resolve()
        if not target.is_relative_to(ROOT):
            parser.error("--output must be inside this repository")
        target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
