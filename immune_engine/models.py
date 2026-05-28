from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Asset:
    path: str
    kind: str
    trust: str
    sensitivity: str
    content: str


@dataclass
class Mission:
    id: str
    title: str
    summary: str
    objective: str
    difficulty: str
    expected_verdict: str
    risk_types: list[str]
    assets: list[dict[str, str]]
    expected_safe_behavior: str
    tool_boundary: str


@dataclass
class HermesFinding:
    role: str
    severity: str
    finding: str
    evidence: str
    recommendation: str


@dataclass
class RiskEvent:
    event_type: str
    severity: str
    source: str
    evidence: str
    policy_reference: str
    decision: str
    recommended_action: str
    confidence: str = "high"


@dataclass
class RunResult:
    run_id: str
    created_at: str
    mission: Mission
    assets: list[Asset]
    hermes_mode: str
    safety_plan: dict[str, Any]
    hermes_findings: list[HermesFinding]
    risk_events: list[RiskEvent]
    score: int
    verdict: str
    timeline: list[dict[str, Any]]
    report_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

