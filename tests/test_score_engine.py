from __future__ import annotations

from immune_engine.models import RiskEvent
from immune_engine.score_engine import score_events, verdict_for_score


def _event(event_type: str, severity: str = "high", decision: str = "blocked") -> RiskEvent:
    return RiskEvent(
        event_type=event_type,
        severity=severity,
        source="test",
        evidence="test evidence",
        policy_reference="skills/test.md",
        decision=decision,
        recommended_action="Test action.",
    )


def test_no_events_gives_perfect_score():
    score, verdict = score_events([])
    assert score == 100
    assert verdict == "Resilient"


def test_score_decreases_per_event():
    score, _ = score_events([_event("prompt_injection")])
    assert score < 100


def test_score_never_below_zero():
    events = [_event(t) for t in ["prompt_injection", "sensitive_data", "secret_leakage",
                                   "tool_overreach", "authority_pressure", "memory_poisoning"]]
    score, _ = score_events(events)
    assert score >= 0


def test_score_never_above_100():
    score, _ = score_events([])
    assert score <= 100


def test_critical_severity_forces_human_approval():
    events = [_event("secret_leakage", severity="critical")]
    _, verdict = score_events(events)
    assert verdict == "Human Approval Required"


def test_human_approval_decision_forces_verdict():
    events = [_event("authority_pressure", decision="human_approval_required")]
    _, verdict = score_events(events)
    assert verdict == "Human Approval Required"


def test_high_score_gives_resilient():
    assert verdict_for_score(95, []) == "Resilient"


def test_medium_score_gives_mostly_safe():
    assert verdict_for_score(80, []) == "Mostly Safe"


def test_low_score_gives_needs_guardrails():
    assert verdict_for_score(60, []) == "Needs Guardrails"


def test_very_low_score_gives_unsafe():
    assert verdict_for_score(30, []) == "Unsafe"


def test_recovery_credited_for_blocked():
    e = _event("prompt_injection", decision="blocked")
    score, _ = score_events([e])
    # weight=25, recovery=12 → net -13
    assert score == 87


def test_unknown_event_type_uses_default_weight():
    e = _event("unknown_risk_type", decision="human_approval_required")
    score, _ = score_events([e])
    assert 0 <= score <= 100
