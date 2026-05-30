from __future__ import annotations

import json

from immune_engine.hermes_runner import (
    _parse_hermes_output,
    _skills_for_risks,
    _first_relevant_asset,
    build_safety_plan,
)
from immune_engine.models import Asset, Mission


def _mission(risk_types: list[str] = None) -> Mission:
    return Mission(
        id="test_mission",
        title="Test",
        summary="Test",
        objective="Test objective",
        difficulty="low",
        expected_verdict="Resilient",
        risk_types=risk_types or ["prompt_injection"],
        assets=[],
        expected_safe_behavior="Safe.",
        tool_boundary="Read-only",
    )


def _asset(content: str, path: str = "test/file.md") -> Asset:
    return Asset(path=path, kind="document", trust="low", sensitivity="high", content=content)


def test_parse_valid_hermes_output():
    output = json.dumps({
        "findings": [
            {
                "role": "Red Team",
                "severity": "high",
                "finding": "Injection detected.",
                "evidence": "ignore previous",
                "recommendation": "Block.",
            }
        ]
    })
    findings = _parse_hermes_output(output)
    assert len(findings) == 1
    assert findings[0].role == "Red Team"


def test_parse_invalid_json_returns_empty():
    findings = _parse_hermes_output("not json at all")
    assert findings == []


def test_parse_empty_findings_list():
    output = json.dumps({"findings": []})
    assert _parse_hermes_output(output) == []


def test_parse_malformed_finding_skipped():
    output = json.dumps({
        "findings": [
            {"role": "Red Team", "severity": "high"},  # missing required fields
            {
                "role": "Policy",
                "severity": "medium",
                "finding": "Data exposed.",
                "evidence": "email found",
                "recommendation": "Redact.",
            },
        ]
    })
    findings = _parse_hermes_output(output)
    assert len(findings) == 1
    assert findings[0].role == "Policy"


def test_parse_non_dict_findings_skipped():
    output = json.dumps({"findings": ["string item", None, 42]})
    assert _parse_hermes_output(output) == []


def test_skills_for_known_risks():
    skills = _skills_for_risks(["prompt_injection", "sensitive_data"])
    assert "prompt_injection_triage.md" in skills
    assert "sensitive_data_handling.md" in skills


def test_skills_for_unknown_risk_is_empty():
    skills = _skills_for_risks(["nonexistent_risk"])
    assert skills == []


def test_skills_deduped():
    # secret_leakage and sensitive_data both map to sensitive_data_handling.md
    skills = _skills_for_risks(["secret_leakage", "sensitive_data"])
    assert skills.count("sensitive_data_handling.md") == 1


def test_build_safety_plan_keys():
    plan = build_safety_plan(_mission(), [])
    assert "objective" in plan
    assert "risk_zones" in plan
    assert "tool_boundary" in plan
    assert "skills_loaded" in plan
    assert "decision_options" in plan


def test_first_relevant_asset_matches_keyword():
    assets = [_asset("The customer wants a refund for order 123.")]
    result = _first_relevant_asset(assets, "sensitive_data")
    assert "customer" in result.lower() or "refund" in result.lower()


def test_first_relevant_asset_no_match_returns_first_path():
    assets = [_asset("harmless content", "safe/file.md")]
    result = _first_relevant_asset(assets, "prompt_injection")
    assert result == "safe/file.md"


def test_first_relevant_asset_empty_returns_placeholder():
    result = _first_relevant_asset([], "prompt_injection")
    assert result == "No asset loaded"
