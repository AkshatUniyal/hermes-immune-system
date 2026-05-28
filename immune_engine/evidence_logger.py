from __future__ import annotations

from .models import HermesFinding, RiskEvent


def build_timeline(findings: list[HermesFinding], events: list[RiskEvent]) -> list[dict[str, object]]:
    timeline: list[dict[str, object]] = []
    second = 4
    for finding in findings:
        timeline.append(
            {
                "time": f"00:{second:02d}",
                "actor": finding.role,
                "severity": finding.severity,
                "title": finding.finding,
                "detail": finding.recommendation,
                "source": finding.evidence,
            }
        )
        second += 7
    for event in events:
        timeline.append(
            {
                "time": f"00:{second:02d}",
                "actor": "Risk Engine",
                "severity": event.severity,
                "title": event.event_type.replace("_", " ").title(),
                "detail": event.recommended_action,
                "source": event.source,
            }
        )
        second += 6
    return timeline

