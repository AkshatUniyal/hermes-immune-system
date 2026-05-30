from __future__ import annotations

import json
import pytest

from immune_engine.mission_loader import load_missions, get_mission, load_assets
from immune_engine.models import Mission


def test_load_missions_returns_list():
    missions = load_missions()
    assert isinstance(missions, list)
    assert len(missions) > 0


def test_all_missions_have_required_fields():
    for mission in load_missions():
        assert mission.id
        assert mission.title
        assert mission.objective
        assert isinstance(mission.risk_types, list)
        assert isinstance(mission.assets, list)


def test_get_mission_returns_correct_mission():
    missions = load_missions()
    first = missions[0]
    found = get_mission(first.id)
    assert found.id == first.id
    assert found.title == first.title


def test_get_mission_raises_on_unknown_id():
    with pytest.raises(ValueError, match="Unknown mission"):
        get_mission("definitely_not_a_real_mission_id")


def test_load_assets_returns_assets():
    missions = load_missions()
    # Use first mission that has assets defined
    for mission in missions:
        if mission.assets:
            assets = load_assets(mission)
            assert len(assets) > 0
            break


def test_load_assets_content_not_empty():
    for mission in load_missions():
        if mission.assets:
            assets = load_assets(mission)
            for asset in assets:
                assert asset.content.strip()
                assert asset.path
            break


def test_load_assets_missing_file_skipped(tmp_path, monkeypatch):
    import immune_engine.mission_loader as ml
    monkeypatch.setattr(ml, "SANDBOX_DIR", tmp_path)
    mission = Mission(
        id="test",
        title="Test",
        summary="Test",
        objective="Test",
        difficulty="low",
        expected_verdict="Resilient",
        risk_types=[],
        assets=[{"path": "nonexistent/file.md", "kind": "doc", "trust": "low", "sensitivity": "low"}],
        expected_safe_behavior="Safe.",
        tool_boundary="Read-only",
    )
    assets = load_assets(mission)
    assert assets == []


def test_malformed_mission_json_skipped(tmp_path, monkeypatch):
    import immune_engine.mission_loader as ml
    monkeypatch.setattr(ml, "MISSIONS_DIR", tmp_path)
    (tmp_path / "bad_mission.json").write_text("not valid json", encoding="utf-8")
    missions = load_missions()
    assert missions == []
