from __future__ import annotations

from pathlib import Path

from .models import RunResult


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"


def generate_report(result: RunResult) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    path = REPORTS_DIR / f"{result.run_id}_{result.mission.id}.md"
    lines = [
        f"# Agent Safety Case Report: {result.mission.title}",
        "",
        f"Run ID: `{result.run_id}`",
        f"Created: `{result.created_at}`",
        f"Hermes mode: `{result.hermes_mode}`",
        f"Safety score: **{result.score}/100**",
        f"Verdict: **{result.verdict}**",
        "",
        "## Mission",
        result.mission.objective,
        "",
        "## Hermes Safety Plan",
    ]
    for key, value in result.safety_plan.items():
        lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
    lines.extend(["", "## Findings"])
    for finding in result.hermes_findings:
        lines.extend(
            [
                f"### {finding.role}: {finding.severity.title()}",
                finding.finding,
                "",
                f"Evidence: `{finding.evidence}`",
                "",
                f"Recommendation: {finding.recommendation}",
                "",
            ]
        )
    lines.extend(["## Risk Events"])
    for event in result.risk_events:
        lines.extend(
            [
                f"### {event.event_type.replace('_', ' ').title()}",
                f"- Severity: `{event.severity}`",
                f"- Source: `{event.source}`",
                f"- Evidence: {event.evidence}",
                f"- Policy reference: `{event.policy_reference}`",
                f"- Decision: `{event.decision}`",
                f"- Recommended action: {event.recommended_action}",
                "",
            ]
        )
    lines.extend(
        [
            "## Safe Outcome",
            result.mission.expected_safe_behavior,
            "",
            "## Transparency Note",
            "This is a local safety-lab prototype for the DEV Hermes Agent Challenge. It uses synthetic assets only. "
            "When the Hermes CLI is installed, the adapter can call Hermes directly; otherwise the demo adapter creates "
            "deterministic Hermes-style planning and findings for reproducible offline judging.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path

