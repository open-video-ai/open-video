"""The generate --json self-verification channel (agent-facing contract)."""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_dry_run_json_contract():
    out = subprocess.run(
        [sys.executable, str(REPO / "cli" / "open_video.py"),
         "a blue test pattern", "--duration", "8", "--dry-run", "--json"],
        capture_output=True, text=True, cwd=REPO, timeout=120)
    assert out.returncode == 0, out.stderr
    payload = json.loads(out.stdout.strip().splitlines()[-1])
    assert payload["dry_run"] is True and payload["validated"] is True
    assert payload["film"] is None
    assert payload["shots"] and set(payload["shots"][0]) == {"scene_id", "mode", "duration_s", "seed"}
