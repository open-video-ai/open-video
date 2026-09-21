"""Tests for benchmark receipt environment failure reporting.

A missing platform tool (e.g. nvidia-smi not on PATH) must be recorded
explicitly instead of producing a receipt that looks like a clean run
with zero VRAM samples.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from bench import profile  # noqa: E402


def test_missing_nvidia_smi_is_recorded(monkeypatch):
    """A missing VRAM tool must be visible instead of looking like a clean sample."""
    sampler = profile.ResourceSampler(interval=0)

    def missing_tool(*args, **kwargs):
        raise FileNotFoundError("nvidia-smi missing")

    monkeypatch.setattr(profile.subprocess, "check_output", missing_tool)

    loops = {"n": 0}

    def stop_after_three(_interval):
        loops["n"] += 1
        if loops["n"] >= 3:
            sampler._stop = True

    monkeypatch.setattr(profile.time, "sleep", stop_after_three)

    sampler._run()

    assert sampler.environment_failures
    assert "nvidia-smi" in sampler.environment_failures[0]
    # a repeating sample loop must not spam unbounded duplicate messages
    assert len(sampler.environment_failures) == 1


def test_run_config_receipt_includes_environment_failures(monkeypatch, tmp_path):
    """The emitted benchmark entry must carry the sampler failure record."""

    class _Result:
        ok = True
        video_path = None
        error = None

    class _Backend:
        def duration_to_length(self, dur):
            return 8

        def generate(self, req):
            return _Result()

    def missing_tool(*args, **kwargs):
        raise FileNotFoundError("nvidia-smi missing")

    monkeypatch.setattr(profile.subprocess, "check_output", missing_tool)
    monkeypatch.setattr(profile.time, "sleep", lambda *_: None)

    results = {}
    profile.run_config(_Backend(), engine=None, name="480p_5s", w=854, h=480,
                       dur=5, seed=1, prompt="p", mode="t2v", server_log=None,
                       steps_hint=None, gpu_index=0, results=results,
                       receipt_path=tmp_path / "receipt.json")

    entry = results["480p_5s"]
    assert entry["status"] == "ok"
    assert entry["environment_failures"]
    assert "nvidia-smi" in entry["environment_failures"][0]
