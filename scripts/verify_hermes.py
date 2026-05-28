from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_HERMES = Path.home() / ".local" / "bin" / "hermes"


def hermes_bin() -> str | None:
    return shutil.which("hermes") or (str(DEFAULT_HERMES) if DEFAULT_HERMES.exists() else None)


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=120, check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Hermes CLI integration for Hermes Immune System.")
    parser.add_argument("--provider", help="Hermes provider override, for example openrouter, nous, anthropic, copilot.")
    parser.add_argument("--model", help="Hermes model override.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    hermes = hermes_bin()
    if not hermes:
        print("FAIL: hermes command not found.")
        return 1

    print(f"Hermes binary: {hermes}")
    version = run([hermes, "--version"], root)
    print((version.stdout or version.stderr).strip())
    if version.returncode != 0:
        print("FAIL: Hermes is installed but version check failed.")
        return 1

    prompt = 'Reply with exactly this JSON and no prose: {"ok": true}'
    command = [hermes, "chat", "-Q", "-q", prompt, "--max-turns", "1"]
    if args.provider:
        command.extend(["--provider", args.provider])
    if args.model:
        command.extend(["--model", args.model])

    probe = run(command, root)
    output = (probe.stdout + "\n" + probe.stderr).strip()
    print("Hermes probe output:")
    print(output)
    if probe.returncode != 0:
        print("FAIL: Hermes model call failed. Authenticate a provider or choose a working provider/model.")
        return 2

    if '{"ok": true}' not in output:
        print("WARN: Hermes responded, but not with the exact expected JSON.")

    sys.path.insert(0, str(root))
    from immune_engine.run import run_mission

    result = run_mission("mission_02_executive_pressure")
    print("Project run:")
    print(json.dumps({"mode": result.hermes_mode, "score": result.score, "verdict": result.verdict}, indent=2))
    if result.hermes_mode != "hermes_cli":
        print("FAIL: Project did not complete in hermes_cli mode.")
        return 3

    print("PASS: Hermes CLI is installed, authenticated, and powering the project run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
