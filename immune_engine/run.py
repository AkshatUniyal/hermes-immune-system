from __future__ import annotations

import json
import logging
from pathlib import Path
from uuid import uuid4

from .evidence_logger import build_timeline
from .hermes_runner import run_hermes_analysis
from .mission_loader import get_mission, load_assets
from .models import RunResult, utc_now
from .report_generator import generate_report
from .risk_detector import detect_risks
from .score_engine import score_events

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def run_mission(mission_id: str) -> RunResult:
    logger.info("Starting mission run: %s", mission_id)
    mission = get_mission(mission_id)
    assets = load_assets(mission)
    if not assets:
        logger.warning("No assets loaded for mission %s — analysis will run with empty evidence", mission_id)

    hermes_mode, safety_plan, findings = run_hermes_analysis(mission, assets)
    risk_events = detect_risks(mission, assets, findings)
    score, verdict = score_events(risk_events)

    result = RunResult(
        run_id=f"run-{uuid4().hex[:8]}",
        created_at=utc_now(),
        mission=mission,
        assets=assets,
        hermes_mode=hermes_mode,
        safety_plan=safety_plan,
        hermes_findings=findings,
        risk_events=risk_events,
        score=score,
        verdict=verdict,
        timeline=build_timeline(findings, risk_events),
    )

    try:
        report_path = generate_report(result)
        result.report_path = str(report_path.relative_to(ROOT))
    except OSError as exc:
        logger.error("Could not write report for mission %s: %s", mission_id, exc)
        result.report_path = None

    DATA_DIR.mkdir(exist_ok=True)
    try:
        (DATA_DIR / "latest_run.json").write_text(
            json.dumps(result.to_dict(), indent=2), encoding="utf-8"
        )
    except OSError as exc:
        logger.error("Could not persist latest_run.json: %s", exc)

    logger.info("Mission %s complete — score=%d verdict=%s", mission_id, score, verdict)
    return result
