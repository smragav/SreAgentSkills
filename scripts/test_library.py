import ast
import copy
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from build_scenario_skills import (
    EXTENSION_PROVENANCE, EXTENSION_SLUGS, RETAINED_PROVENANCE, RETAINED_SKILLS,
    UPSTREAM_PROVENANCE, output_contract, render_skill, scenario_sources, workflow_definitions,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "tools"))
from scenario_contract import validate_result
from validate_library import fixture, metadata, validate


@pytest.mark.parametrize("style", ["|", "|-", ">", ">-"])
def test_metadata_preserves_multiline_descriptions(monkeypatch, style):
    path = ROOT / "SKILL.md"
    text = (
        f"---\nname: example\ndescription: {style}\n"
        "  Build an evidence based assessment.\n  Use this skill when reviewing scope.\n"
        "tools:\n  - RunInTerminal\n---\n# Example\n"
    )
    monkeypatch.setattr(Path, "read_text", lambda self, **kwargs: text)
    info = metadata(path)
    assert "Build an evidence based assessment." in info["description"]
    assert "Use this skill when reviewing scope." in info["description"]
    assert "tools:" not in info["description"]
    assert info["tools"] == ["RunInTerminal"]


def definitions():
    workflows = workflow_definitions(ROOT)
    return [(source, workflows.get(source["slug"])) for source in scenario_sources(ROOT)]


def test_source_membership_and_provenance_are_exact_and_disjoint():
    upstream = json.loads((ROOT / "catalog" / "upstream-scenarios.json").read_text(encoding="utf-8"))
    extensions = json.loads((ROOT / "catalog" / "extension-scenarios.json").read_text(encoding="utf-8"))
    sources = scenario_sources(ROOT)
    upstream_sources = [source for source in sources if source["provenance"] == UPSTREAM_PROVENANCE]
    extension_sources = [source for source in sources if source["provenance"] == EXTENSION_PROVENANCE]
    upstream_slugs = {source["slug"] for source in upstream_sources}
    extension_slugs = {source["slug"] for source in extension_sources}
    assert len(upstream_sources) == len(upstream_slugs) == len(upstream["scenarios"]) == 77
    assert upstream_slugs == {source["slug"] for source in upstream["scenarios"]}
    assert len(extension_sources) == len(extension_slugs) == 6
    assert extension_slugs == EXTENSION_SLUGS == {
        "slo-error-budget-analysis", "backup-restore-validation", "release-regression-detection",
        "aks-application-incident-triage", "messaging-delivery-failure-triage",
        "ai-inference-reliability-investigation",
    }
    assert not upstream_slugs & extension_slugs
    assert not (upstream_slugs | extension_slugs) & RETAINED_SKILLS.keys()
    assert len(RETAINED_SKILLS) == 22
    assert extensions["provenance"] == EXTENSION_PROVENANCE
    assert all(source["category"] == "management" for source in extension_sources)
    assert sum(source["category"] == "management" for source in sources) == 32
    for source in extensions["scenarios"]:
        assert {"slug", "title", "category", "mode", "frequency", "description", "prompt", "provenance"} <= source.keys()
        assert source["provenance"] == EXTENSION_PROVENANCE
    for raw, normalized in zip(upstream["scenarios"], upstream_sources):
        assert all(normalized[key] == value for key, value in raw.items())
        assert "provenance" not in raw


@pytest.fixture
def source_documents(monkeypatch):
    paths = {name: ROOT / "catalog" / f"{name}-scenarios.json" for name in ("upstream", "extension")}
    documents = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in paths.items()}
    read_text = Path.read_text

    def read_source(path, *args, **kwargs):
        for name, source_path in paths.items():
            if path == source_path:
                return json.dumps(documents[name])
        return read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_source)
    return documents


@pytest.mark.parametrize("mutation", [
    "missing-upstream", "duplicate-upstream", "extra-upstream", "upstream-extension-overlap",
    "upstream-retained-overlap", "missing-extension", "duplicate-extension", "unknown-extension",
    "manifest-provenance", "record-provenance", "upstream-provenance", "extension-category",
    "extension-description", "extension-prompt",
])
def test_source_loader_rejects_invalid_membership_and_provenance(source_documents, mutation):
    upstream = source_documents["upstream"]["scenarios"]
    extensions = source_documents["extension"]["scenarios"]
    if mutation == "missing-upstream":
        upstream.pop()
    elif mutation == "duplicate-upstream":
        upstream[-1] = copy.deepcopy(upstream[0])
    elif mutation == "extra-upstream":
        upstream.append({**upstream[0], "slug": "unexpected-upstream-scenario"})
    elif mutation == "upstream-extension-overlap":
        upstream[0]["slug"] = extensions[0]["slug"]
    elif mutation == "upstream-retained-overlap":
        upstream[0]["slug"] = next(iter(RETAINED_SKILLS))
    elif mutation == "missing-extension":
        extensions.pop()
    elif mutation == "duplicate-extension":
        extensions[-1] = copy.deepcopy(extensions[0])
    elif mutation == "unknown-extension":
        extensions[0]["slug"] = "unexpected-extension"
    elif mutation == "manifest-provenance":
        source_documents["extension"]["provenance"] = UPSTREAM_PROVENANCE
    elif mutation == "record-provenance":
        extensions[0]["provenance"] = UPSTREAM_PROVENANCE
    elif mutation == "upstream-provenance":
        upstream[0]["provenance"] = EXTENSION_PROVENANCE
    elif mutation == "extension-category":
        extensions[0]["category"] = "network"
    elif mutation == "extension-description":
        extensions[0]["description"] = ""
    elif mutation == "extension-prompt":
        del extensions[0]["prompt"]
    with pytest.raises(ValueError):
        scenario_sources(ROOT)


def test_workflow_loader_rejects_duplicates(monkeypatch):
    path = ROOT / "catalog" / "workflows-test.json"
    monkeypatch.setattr(Path, "glob", lambda self, pattern: [path])
    monkeypatch.setattr(Path, "read_text", lambda self, **kwargs: '[{"slug":"duplicate"},{"slug":"duplicate"}]')
    with pytest.raises(ValueError, match="Duplicate workflow"):
        workflow_definitions(ROOT)


def test_dedicated_source_workflow_membership():
    sources = scenario_sources(ROOT)
    workflows = workflow_definitions(ROOT)
    assert len(workflows) == len(sources) == 83
    assert set(workflows) == {source["slug"] for source in sources}


def test_source_loader_does_not_mutate_pinned_metadata():
    path = ROOT / "catalog" / "upstream-scenarios.json"
    before = path.read_bytes()
    scenario_sources(ROOT)
    assert path.read_bytes() == before


@pytest.mark.parametrize("source", scenario_sources(ROOT), ids=lambda source: source["slug"])
def test_generated_playbook_is_neutral_and_preserves_summary_boundary(source):
    definition = {
        "objective": "Review approved synthetic evidence.",
        "approval": {"required": False},
        "inputs": [], "permissions": [], "sources": [],
        "output_fields": ["observation", "expected", "actual", "limitation"],
    }
    text = render_skill(source, definition)
    assert "never pass unadapted scenario JSON" in text
    assert "Suggested cadence:" in text
    assert "separate explicit approval" in text
    lowered = text.lower()
    assert "upstream" not in lowered and "provenance" not in lowered and "original extension" not in lowered
    assert "Suggested mode:" in text
    assert "[License notices](./references/license-notices.txt)" in text
    if source["provenance"] == EXTENSION_PROVENANCE:
        assert f"`--scenario {source['slug']}`" in text
        assert "`tools/operational_analysis.py`" in text
        assert "`--input <adapted-input.json>`" in text
        assert "`--contract references/output-contract.json`" in text
        assert "`--output <new-private-result.json>`" in text
        assert "Optionally add `--sharing-output <new-sharing-draft.json>`" in text
        assert "private output preserves the full evidence result contract" in text
        assert "not a replacement for the private evidence contract" in text
        assert "refuses overwrites" in text


def test_catalog_pages_hide_origin_labels_and_stay_self_contained():
    from build_catalog import catalog_page

    records = [
        {"slug": source["slug"], "category_label": source["category_label"], "title": source["title"]}
        for source in scenario_sources(ROOT)
    ] + [
        {"slug": slug, "category_label": "Management", "title": slug}
        for slug in RETAINED_SKILLS
    ]
    page = catalog_page(records)
    embedded = re.search(r'<script id="skill-data" type="application/json">(.*?)</script>', page, re.DOTALL)
    assert json.loads(embedded.group(1)) == records
    assert len(records) == 105
    lowered = page.lower().replace("record", "")
    for word in ("provenance", "upstream", "retained", "original extension", "skill type"):
        assert word not in lowered
    assert "for(const control of [category,search])" in page
    assert "<script src=" not in page
    assert 'data-theme="light"' in page
    assert "@media(max-width:600px)" in page
    assert "capabilities.html" not in page
    assert "https://github.com/alsanch/azure-sre-agent-scenarios" in page and "plus additional scenarios" in page
    assert "https://github.com/onsenturk/SreAgentExtensions" in page


def test_catalog_embed_escapes_untrusted_text():
    from build_catalog import catalog_page

    records = [{"title": "</script><script>untrusted</script>"}]
    page = catalog_page(records)
    embedded = re.search(r'<script id="skill-data" type="application/json">(.*?)</script>', page, re.DOTALL)
    assert json.loads(embedded.group(1)) == records
    assert "</script><script>untrusted</script>" not in page


def test_analysis_skill_routing_uses_neutral_wording(monkeypatch):
    from build_catalog import update_retained_routing

    sources = scenario_sources(ROOT)
    upstream = next(source for source in sources if source["provenance"] == UPSTREAM_PROVENANCE)
    extension = next(source for source in sources if source["provenance"] == EXTENSION_PROVENANCE)
    skill = ROOT / "management" / "incident-triage-rca" / "SKILL.md"
    routing = skill.parent / "references" / "scenarios.md"
    contents = {skill: "# Skill\n\n## Scenario coverage\n\nDocumented checks.\n",
                routing: f"# Existing routing\n\n{upstream['title']}\n{extension['title']}\n"}
    monkeypatch.setattr(Path, "exists", lambda self: self in contents)
    monkeypatch.setattr(Path, "read_text", lambda self, **kwargs: contents[self])
    monkeypatch.setattr(Path, "write_text", lambda self, text, **kwargs: contents.update({self: text}))
    update_retained_routing(skill, sources)
    assert upstream["slug"] in contents[routing]
    lowered = (contents[routing] + contents[skill]).lower()
    assert "upstream" not in lowered and "original" not in lowered and "retained" not in lowered


@pytest.mark.parametrize("source", scenario_sources(ROOT), ids=lambda source: source["slug"])
def test_generated_contract_preserves_standard_schema(source):
    fields = ["observation", "expected", "actual", "limitation"]
    contract = output_contract(source["slug"], fields)
    assert contract["properties"]["scenario_id"]["const"] == source["slug"]
    scenario_data = contract["properties"]["findings"]["items"]["properties"]["scenario_data"]
    assert scenario_data["required"] == fields
    definition = {"output_fields": fields}
    for state in ("Observed", "Needs attention", "Not assessed"):
        validate_result(fixture(source, definition, state), contract)


@pytest.mark.parametrize(
    "slug,step",
    [(source["slug"], step) for source, definition in definitions()
     for step in (definition or {}).get("collection", []) if step["language"] == "python"],
    ids=lambda value: value["name"] if isinstance(value, dict) else value,
)
def test_workflow_python_compiles(slug, step):
    ast.parse(step["command"], filename=f"{slug}:{step['name']}")


def test_workflow_shell_commands_parse():
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if shell is None:
        pytest.skip("PowerShell is required for local shell syntax validation.")
    script = r"""
$ErrorActionPreference = 'Stop'
$count = 0
foreach ($file in Get-ChildItem -LiteralPath (Join-Path $env:SRE_VALIDATION_ROOT 'catalog') -Filter 'workflows-*.json') {
    foreach ($scenario in (Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json)) {
        foreach ($step in $scenario.collection) {
            if ($step.language -notin @('powershell', 'azurecli')) { continue }
            $tokens = $null
            $parseErrors = $null
            $null = [System.Management.Automation.Language.Parser]::ParseInput(
                $step.command, [ref]$tokens, [ref]$parseErrors)
            if ($parseErrors.Count) {
                throw ('{0}: {1}: {2}' -f $scenario.slug, $step.name, ($parseErrors.Message -join '; '))
            }
            $count++
        }
    }
}
Write-Output "Parsed $count shell collection steps."
"""
    result = subprocess.run(
        [shell, "-NoProfile", "-NonInteractive", "-Command", script],
        env={**os.environ, "SRE_VALIDATION_ROOT": str(ROOT)},
        capture_output=True, text=True, timeout=60, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    expected = sum(
        step["language"] in ("powershell", "azurecli")
        for _, definition in definitions() for step in definition["collection"]
    )
    assert expected > 0
    assert f"Parsed {expected} shell collection steps." in result.stdout


@pytest.mark.parametrize("source,definition", definitions(), ids=lambda item: item["slug"] if item else "missing")
def test_each_dedicated_scenario_accepts_evidence_and_rejects_false_completion(source, definition):
    assert definition is not None, "A complete workflow is required."
    path = ROOT / source["category"] / source["slug"] / "references" / "output-contract.json"
    contract = json.loads(path.read_text(encoding="utf-8"))
    for state in ("Observed", "Needs attention", "Not assessed"):
        validate_result(fixture(source, definition, state), contract)
    invalid = fixture(source, definition, "Not assessed")
    invalid["assessment_status"] = "Complete"
    with pytest.raises(ValueError, match="Complete"):
        validate_result(invalid, contract)
    for state in ("Observed", "Needs attention", "Not applicable"):
        invalid = copy.deepcopy(fixture(source, definition, "Observed"))
        invalid["findings"][0]["status"] = state
        invalid["findings"][0]["evidence"] = []
        with pytest.raises(ValueError, match="evidence"):
            validate_result(invalid, contract)
    for timestamp in ("2026-10-21T05:30:00+05:30", "2026-10-21T00:00:00"):
        invalid = copy.deepcopy(fixture(source, definition, "Observed"))
        invalid["assessed_at"] = timestamp
        with pytest.raises(ValueError, match="UTC"):
            validate_result(invalid, contract)
    invalid = copy.deepcopy(fixture(source, definition, "Observed"))
    invalid["findings"][0]["evidence"][0]["source"] = True
    with pytest.raises(ValueError, match="source"):
        validate_result(invalid, contract)


def test_library_has_105_valid_packaged_skills():
    result = validate()
    assert result["skills"] == result["bundle_checks"] == 105
    assert result["analysis_tool_skills"] == 22
    assert result["scenario_workflows"] == 83
    assert result["evidence_fixture_checks"] == 249
    assert not result["live_azure_validation"]


def test_all_skill_descriptions_are_discoverable():
    for path in ROOT.glob("*/*/SKILL.md"):
        assert re.search(r"\buse(?: this skill)? (?:when|before)\b", metadata(path)["description"].lower())
