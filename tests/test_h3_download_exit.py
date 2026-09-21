"""Regression: h3_download.sh must exit nonzero when integrity verification fails.

W5 — the script wrote VERIFY_FAILED to the status file but then `break`ed out
of the loop and exited 0, so callers could not detect a same-size corrupt
weight. No network, no modelscope: OPEN_VIDEO_PYTHON is stubbed so the
snapshot_download heredoc returns 0 once (consuming stdin), while every other
invocation execs the real interpreter — so the real scripts/h3_download.sh
drives the real scripts/verify_h3_manifest.py over tiny files.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
DOWNLOAD_SH = REPO / "scripts" / "h3_download.sh"
VERIFIER = REPO / "scripts" / "verify_h3_manifest.py"

PAYLOAD = b"w"  # one byte


def _fixture(root: Path, stub: Path, *, corrupt: bool) -> None:
    (root / "scripts").mkdir(parents=True)
    (root / "models").mkdir()
    shutil.copy2(DOWNLOAD_SH, root / "scripts" / "h3_download.sh")
    shutil.copy2(VERIFIER, root / "scripts" / "verify_h3_manifest.py")

    sha = hashlib.sha256(b"X").hexdigest() if corrupt else hashlib.sha256(PAYLOAD).hexdigest()
    manifest = {
        "model": "test/model",
        "files": {
            "w": {
                "url": "https://example.invalid/w",
                "size": len(PAYLOAD),
                "commit": "a" * 40,
                "sha256": sha,
            }
        },
    }
    (root / "models" / "h3_manifest.json").write_text(json.dumps(manifest))
    weights = root / "h3_models"
    weights.mkdir()
    (weights / "w").write_bytes(PAYLOAD)

    counter = stub.parent / "stub.calls"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        'if [ "${1:-}" = "-" ]; then\n'
        "  cat > /dev/null\n"
        f'  n=$(cat "{counter}" 2>/dev/null || echo 0)\n'
        f'  echo $((n + 1)) > "{counter}"\n'
        '  [ "$n" -eq 0 ] && exit 0\n'
        "  exit 1\n"
        "fi\n"
        f'exec "{sys.executable}" "$@"\n'
    )
    stub.chmod(0o755)


def _run(root: Path, stub: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, OPEN_VIDEO_PYTHON=str(stub),
               OPEN_VIDEO_MODELS=str(root / "h3_models"),
               OPEN_VIDEO_DOWNLOAD_HEARTBEAT=str(root / "logs/heartbeat.log"),
               OPEN_VIDEO_DOWNLOAD_STATUS=str(root / "logs/h3_download.status"))
    return subprocess.run(
        ["bash", "scripts/h3_download.sh"],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )


def _status(root: Path) -> str:
    return (root / "logs" / "h3_download.status").read_text().strip()


@pytest.fixture
def sandbox(tmp_path: Path):
    yield tmp_path
    shutil.rmtree(tmp_path, ignore_errors=True)


def test_corrupt_same_size_weight_exits_nonzero(sandbox: Path):
    """Same-size corrupt file: sizes pass but sha256 fails — the script must
    write VERIFY_FAILED and exit nonzero instead of exiting 0."""
    root, stub = sandbox / "repo", sandbox / "py-stub.sh"
    _fixture(root, stub, corrupt=True)
    r = _run(root, stub)
    assert _status(root) == "VERIFY_FAILED"
    assert r.returncode != 0


def test_valid_weight_exits_zero(sandbox: Path):
    """Correct size + sha256: DOWNLOAD_COMPLETE and exit 0."""
    root, stub = sandbox / "repo", sandbox / "py-stub.sh"
    _fixture(root, stub, corrupt=False)
    r = _run(root, stub)
    assert _status(root) == "DOWNLOAD_COMPLETE"
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.parametrize("manifest_text", [None, "not-json"])
def test_invalid_manifest_exits_before_download(sandbox: Path, manifest_text):
    root, stub = sandbox / "repo", sandbox / "py-stub.sh"
    _fixture(root, stub, corrupt=False)
    manifest = root / "models/h3_manifest.json"
    if manifest_text is None:
        manifest.unlink()
    else:
        manifest.write_text(manifest_text)
    result = _run(root, stub)
    assert result.returncode != 0
    assert not (sandbox / "stub.calls").exists()
