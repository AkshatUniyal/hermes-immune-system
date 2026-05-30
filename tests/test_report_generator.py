from __future__ import annotations

import pytest

from immune_engine.models import Asset, HermesFinding, Mission, RiskEvent, RunResult
from immune_engine.report_generator import generate_report


def _make_result(tmp_path) -> RunResult:
    mission = Mission(
        id="test_mission",
        title="Test Mission",
        summary="A test mission.",
        objective="Verify report generation.",
        difficulty="low",
        expected_verdict="Resilient",
        risk_types=["prompt_injection"],
        assets=[],
        expected_safe_behavior="Safe behavior described here.",
        tool_boundary="Read-only",
    )
    finding = HermesFinding(
        role="Red Team",
        severity="high",
        finding="Injection attempt detected.",
        evidence="ignore previous instructions",
        recommendation="Block and log.",
    )
    event = RiskEvent(
        event_type="prompt_injection",
        severity="high",
        source="test/file.md",
        evidence="ignore previous instructions",
        policy_reference="skills/prompt_injection_triage.md",
        decision="blocked",
        recommended_action="Ignore hostile instructions.",
    )
    return RunResult(
        run_id="run-test1234",
        created_at="2026-05-30T00:00:00+00:00",
        mission=mission,
        assets=[],
        hermes_mode="demo_adapter",
        safety_plan={"objective": "Test", "risk_zones": ["prompt_injection"]},
        hermes_findings=[finding],
        risk_events=[event],
        score=87,
        verdict="Mostly Safe",
        timeline=[],
    )


def test_generate_report_creates_file(tmp_path, monkeypatch):
    import immune_engine.report_generator as rg
    monkeypatch.setattr(rg, "REPORTS_DIR", tmp_path)
    result = _make_result(tmp_path)
    path = generate_report(result)
    assert path.exists()
    assert path.suffix == ".md"


def test_report_contains_run_id(tmp_path, monkeypatch):
    import immune_engine.report_generator as rg
    monkeypatch.setattr(rg, "REPORTS_DIR", tmp_path)
    result = _make_result(tmp_path)
    path = generate_report(result)
    content = path.read_text(encoding="utf-8")
    assert "run-test1234" in content


def test_report_contains_score(tmp_path, monkeypatch):
    import immune_engine.report_generator as rg
    monkeypatch.setattr(rg, "REPORTS_DIR", tmp_path)
    result = _make_result(tmp_path)
    path = generate_report(result)
    content = path.read_text(encoding="utf-8")
    assert "87/100" in content


def test_report_contains_verdict(tmp_path, monkeypatch):
    import immune_engine.report_generator as rg
    monkeypatch.setattr(rg, "REPORTS_DIR", tmp_path)
    result = _make_result(tmp_path)
    path = generate_report(result)
    content = path.read_text(encoding="utf-8")
    assert "Mostly Safe" in content


def test_report_contains_mission_title(tmp_path, monkeypatch):
    import immune_engine.report_generator as rg
    monkeypatch.setattr(rg, "REPORTS_DIR", tmp_path)
    result = _make_result(tmp_path)
    path = generate_report(result)
    content = path.read_text(encoding="utf-8")
    assert "Test Mission" in content


def test_report_filename_matches_run_id_and_mission(tmp_path, monkeypatch):
    import immune_engine.report_generator as rg
    monkeypatch.setattr(rg, "REPORTS_DIR", tmp_path)
    result = _make_result(tmp_path)
    path = generate_report(result)
    assert "run-test1234" in path.name
    assert "test_mission" in path.name
