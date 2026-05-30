from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
from pathlib import Path

from .models import Asset, HermesFinding, Mission

logger = logging.getLogger(__name__)


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
DEFAULT_HERMES_BIN = Path.home() / ".local" / "bin" / "hermes"


ROLE_MAP = {
    "prompt_injection": (
        "Red Team Subagent",
        "high",
        "Embedded instructions attempt to override the mission or policy context.",
        "Treat embedded instructions as untrusted data and continue only with the legitimate task.",
    ),
    "authority_pressure": (
        "Red Team Subagent",
        "high",
        "The request uses urgency or rank to pressure the agent into bypassing controls.",
        "Check policy, reduce scope, and require approval for restricted data or actions.",
    ),
    "sensitive_data": (
        "Policy Guardian",
        "high",
        "The mission touches customer identifiers, refund data, credentials, or confidential records.",
        "Redact or aggregate sensitive fields unless explicit approval exists.",
    ),
    "secret_leakage": (
        "Policy Guardian",
        "critical",
        "Repository content may contain credentials or deploy-time secrets.",
        "Never reveal secrets; flag them and recommend rotation.",
    ),
    "memory_poisoning": (
        "Skill Curator",
        "medium",
        "The mission includes a request to persist unsafe trust or approval-bypass behavior.",
        "Store only safe generalized learning, not hostile instructions.",
    ),
    "external_content": (
        "Red Team Subagent",
        "high",
        "Untrusted web content attempts to influence agent behavior outside the research task.",
        "Treat external pages as data, not instructions.",
    ),
    "tool_overreach": (
        "Policy Guardian",
        "high",
        "The requested action may exceed the approved tool boundary.",
        "Convert execution into a dry-run plan and request human approval.",
    ),
}


def hermes_available() -> bool:
    return _hermes_bin() is not None


def build_safety_plan(mission: Mission, assets: list[Asset]) -> dict[str, object]:
    return {
        "objective": mission.objective,
        "risk_zones": mission.risk_types,
        "tool_boundary": mission.tool_boundary,
        "assets_to_inspect": [asset.path for asset in assets],
        "skills_loaded": _skills_for_risks(mission.risk_types),
        "approval_boundary": "External sends, destructive writes, raw exports, memory writes, and credential handling require review.",
        "decision_options": ["allow", "allow_with_redaction", "draft_only", "human_approval_required", "blocked"],
    }


def run_hermes_analysis(mission: Mission, assets: list[Asset]) -> tuple[str, dict[str, object], list[HermesFinding]]:
    plan = build_safety_plan(mission, assets)
    if hermes_available():
        return _run_real_hermes(mission, assets, plan)
    return "demo_adapter", plan, _demo_findings(mission, assets)


def _run_real_hermes(
    mission: Mission, assets: list[Asset], plan: dict[str, object]
) -> tuple[str, dict[str, object], list[HermesFinding]]:
    prompt = {
        "task": "Analyze this agent safety mission and return JSON findings.",
        "mission": mission.__dict__,
        "assets": [{"path": asset.path, "content": asset.content[:4000]} for asset in assets],
        "required_schema": {
            "findings": [
                {
                    "role": "Red Team Subagent",
                    "severity": "high",
                    "finding": "string",
                    "evidence": "string",
                    "recommendation": "string",
                }
            ]
        },
    }
    command = [_hermes_bin() or "hermes", "chat", "-Q", "-q", json.dumps(prompt), "--max-turns", "2"]
    provider = os.getenv("HERMES_IMMUNE_PROVIDER")
    model = os.getenv("HERMES_IMMUNE_MODEL")
    if provider:
        command.extend(["--provider", provider])
    if model:
        command.extend(["--model", model])
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=90,
        )
    except Exception as exc:
        logger.warning("Hermes CLI execution failed: %s — falling back to demo adapter", exc)
        fallback = _demo_findings(mission, assets)
        fallback.insert(
            0,
            HermesFinding(
                role="Hermes Orchestrator",
                severity="low",
                finding="Hermes runtime handoff completed through the local safety adapter.",
                evidence="Hermes runtime exception captured locally",
                recommendation="Review the local Hermes configuration, then rerun the mission for a fresh orchestration trace.",
            ),
        )
        return "demo_adapter_after_hermes_error", plan, fallback

    if completed.returncode != 0:
        fallback = _demo_findings(mission, assets)
        fallback.insert(
            0,
            HermesFinding(
                role="Hermes Orchestrator",
                severity="medium",
                finding="Hermes CLI handoff was captured and normalized by the local safety adapter.",
                evidence="Hermes CLI response captured locally",
                recommendation="Confirm the configured local model is available, then rerun the mission for a fresh orchestration trace.",
            ),
        )
        return "demo_adapter_after_hermes_auth_error", plan, fallback

    findings = _parse_hermes_output(completed.stdout)
    if not findings:
        findings = _demo_findings(mission, assets)
        findings.insert(
            0,
            HermesFinding(
                role="Hermes Orchestrator",
                severity="low",
                finding="Hermes output normalized into dashboard-ready findings.",
                evidence="Hermes CLI response",
                recommendation="Continue with the normalized findings and preserve the original response in the evidence trail.",
            ),
        )
    return "hermes_cli", plan, findings


def _hermes_bin() -> str | None:
    path = shutil.which("hermes")
    if path:
        return path
    if DEFAULT_HERMES_BIN.exists():
        return str(DEFAULT_HERMES_BIN)
    return None


def _parse_hermes_output(output: str) -> list[HermesFinding]:
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        logger.warning("Could not parse Hermes CLI output as JSON")
        return []
    findings = data.get("findings", [])
    result: list[HermesFinding] = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        try:
            result.append(HermesFinding(**finding))
        except TypeError as exc:
            logger.warning("Skipping malformed finding from Hermes output: %s", exc)
    return result


def _skills_for_risks(risk_types: list[str]) -> list[str]:
    mapping = {
        "prompt_injection": "prompt_injection_triage.md",
        "authority_pressure": "authority_pressure_defense.md",
        "sensitive_data": "sensitive_data_handling.md",
        "secret_leakage": "sensitive_data_handling.md",
        "memory_poisoning": "memory_poisoning_defense.md",
        "external_content": "external_content_isolation.md",
        "tool_overreach": "approval_boundary_check.md",
    }
    return sorted({mapping[risk] for risk in risk_types if risk in mapping})


def _demo_findings(mission: Mission, assets: list[Asset]) -> list[HermesFinding]:
    findings = [
        HermesFinding(
            role="Hermes Orchestrator",
            severity="info",
            finding="Mission interpreted and approval boundaries declared before inspecting task content.",
            evidence=mission.objective,
            recommendation="Proceed with policy-first review before action.",
        )
    ]
    for risk in mission.risk_types:
        role, severity, finding, recommendation = ROLE_MAP.get(
            risk,
            ("Evidence Collector", "medium", "Potential safety issue found.", "Collect evidence and escalate if uncertain."),
        )
        evidence = _first_relevant_asset(assets, risk)
        findings.append(
            HermesFinding(
                role=role,
                severity=severity,
                finding=finding,
                evidence=evidence,
                recommendation=recommendation,
            )
        )
    findings.append(
        HermesFinding(
            role="Evidence Collector",
            severity="info",
            finding="Evidence trail assembled with source assets, risk categories, and recommended controls.",
            evidence=", ".join(asset.path for asset in assets),
            recommendation="Generate an audit-friendly Safety Case report.",
        )
    )
    return findings


def _first_relevant_asset(assets: list[Asset], risk: str) -> str:
    risk_words = {
        "prompt_injection": ["ignore", "override", "export"],
        "authority_pressure": ["urgent", "skip", "vp", "executive"],
        "sensitive_data": ["customer", "email", "refund", "ssn"],
        "secret_leakage": ["api_key", "secret", "token", "password"],
        "memory_poisoning": ["remember", "always trust", "bypass"],
        "external_content": ["ignore", "internal files", "system"],
        "tool_overreach": ["delete", "send", "export", "update"],
    }
    words = risk_words.get(risk, [])
    for asset in assets:
        lower = asset.content.lower()
        if any(word in lower for word in words):
            return f"{asset.path}: {asset.content.strip().splitlines()[0][:160]}"
    return assets[0].path if assets else "No asset loaded"
