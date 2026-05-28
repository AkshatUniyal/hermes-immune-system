from __future__ import annotations

import json
from pathlib import Path

from .models import Asset, Mission


ROOT = Path(__file__).resolve().parents[1]
MISSIONS_DIR = ROOT / "missions"
SANDBOX_DIR = ROOT / "sandbox"


def load_missions() -> list[Mission]:
    missions: list[Mission] = []
    for path in sorted(MISSIONS_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        missions.append(Mission(**data))
    return missions


def get_mission(mission_id: str) -> Mission:
    for mission in load_missions():
        if mission.id == mission_id:
            return mission
    raise ValueError(f"Unknown mission: {mission_id}")


def load_assets(mission: Mission) -> list[Asset]:
    assets: list[Asset] = []
    for asset_info in mission.assets:
        asset_path = SANDBOX_DIR / asset_info["path"]
        content = asset_path.read_text(encoding="utf-8")
        assets.append(
            Asset(
                path=asset_info["path"],
                kind=asset_info["kind"],
                trust=asset_info["trust"],
                sensitivity=asset_info["sensitivity"],
                content=content,
            )
        )
    return assets

