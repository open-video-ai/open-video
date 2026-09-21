"""Tests for benchmark resume behavior."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from bench.profile import is_complete  # noqa: E402


def test_is_complete_requires_existing_video_artifact(tmp_path):
    video = tmp_path / "result.mp4"
    entry = {
        "status": "ok",
        "wall_s": 12.5,
        "video_path": str(video),
    }

    assert is_complete(entry) is False

    video.write_bytes(b"fake-video")
    assert is_complete(entry) is True
