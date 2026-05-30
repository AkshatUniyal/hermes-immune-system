from __future__ import annotations

import json
import logging
from pathlib import Path

from .models import Asset, Mission

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
MISSIONS_DIR = ROOT / "missions"
SANDBOX_DIR = ROOT / "sandbox"


def load_missions() -> list[Mission]:
    missions: list[Mission] = []
    for path in sorted(MISSIONS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            missions.append(Mission(**data))
        except (json.JSONDecodeError, TypeError, KeyError) as exc:
            logger.warning("Skipping malformed mission file %s: %s", path.name, exc)
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
        try:
            content = asset_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.warning("Asset file not found: %s — skipping", asset_path)
            continue
        except OSError as exc:
            logger.warning("Could not read asset %s: %s — skipping", asset_path, exc)
            continue
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
