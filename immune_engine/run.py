from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from .evidence_logger import build_timeline
from .hermes_runner import run_hermes_analysis
from .mission_loader import get_mission, load_assets
from .models import RunResult, utc_now
from .report_generator import generate_report
from .risk_detector import detect_risks
from .score_engine import score_events


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def run_mission(mission_id: str) -> RunResult:
    mission = get_mission(mission_id)
    assets = load_assets(mission)
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
    report_path = generate_report(result)
    result.report_path = str(report_path.relative_to(ROOT))
    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / "latest_run.json").write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    return result

