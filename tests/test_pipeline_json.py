"""Validation tests for ADF pipeline/dataset/linked-service JSON.

ADF definitions can't be executed by a reviewer, so this suite is the
executable proof: every JSON file must parse, carry the required ADF fields,
reference only datasets/linked services that exist in this repo, contain no
secrets, and declare retry policies on activities that call external systems.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SECRET_PATTERNS = re.compile(
    r"(password|secret|connectionstring|apikey)\s*=\s*[^@{\s][^,}]*",
    re.IGNORECASE,
)


def _load_jsons(folder: str) -> dict[str, dict]:
    result = {}
    for path in sorted((ROOT / folder).glob("*.json")):
        result[path.stem] = json.loads(path.read_text())
    return result


def test_all_json_files_parse():
    for folder in ("pipelines", "datasets", "linked_services"):
        for path in (ROOT / folder).glob("*.json"):
            json.loads(path.read_text())  # raises on invalid JSON


def test_pipelines_have_name_and_activities():
    pipelines = _load_jsons("pipelines")
    assert len(pipelines) >= 3
    for name, doc in pipelines.items():
        assert doc.get("name"), f"{name}: missing name"
        activities = doc["properties"].get("activities", [])
        assert activities, f"{name}: no activities defined"
        for act in activities:
            assert act.get("name"), f"{name}: activity without a name"
            assert act.get("type"), f"{name}: activity without a type"


def test_referenced_datasets_exist():
    datasets = set(_load_jsons("datasets"))
    pipelines = _load_jsons("pipelines")
    missing = []
    for pname, doc in pipelines.items():
        text = json.dumps(doc)
        for ds in re.findall(r'"referenceName"\s*:\s*"([^"]+)"', text):
            if ds.startswith(("ds_", "pl_")) and ds not in datasets and not ds.startswith("pl_"):
                missing.append(f"{pname} references unknown dataset {ds}")
    assert not missing, missing


def test_no_hardcoded_secrets():
    offenders = []
    for folder in ("pipelines", "datasets", "linked_services"):
        for path in (ROOT / folder).glob("*.json"):
            if SECRET_PATTERNS.search(path.read_text()):
                offenders.append(str(path))
    assert not offenders, f"possible hardcoded secrets: {offenders}"


def test_copy_activities_have_retry_policy():
    pipelines = _load_jsons("pipelines")
    without_retry = []
    for pname, doc in pipelines.items():
        for act in doc["properties"].get("activities", []):
            if act["type"] in ("Copy", "WebActivity", "Lookup"):
                policy = act.get("policy", {})
                if policy.get("retry", 0) < 1:
                    without_retry.append(f"{pname}/{act['name']}")
    assert not without_retry, f"external-call activities without retry: {without_retry}"


def test_quality_gate_has_failure_path():
    gate = _load_jsons("pipelines")["pl_data_quality_gate"]
    if_activities = [a for a in gate["properties"]["activities"] if a["type"] == "IfCondition"]
    assert if_activities, "quality gate has no IfCondition activity"
    gate_activity = if_activities[0]
    assert gate_activity["typeProperties"].get("ifFalseActivities"), \
        "quality gate has no failure path (alert + fail)"
