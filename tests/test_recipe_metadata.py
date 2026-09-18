"""Regression tests for recipe metadata embedding."""

import subprocess

import pytest

from open_video.core import recipe as recipe_module


def test_embed_recipe_rejects_oversized_metadata():
    with pytest.raises(ValueError, match="exceeds"):
        recipe_module.embed_recipe(
            "input.mp4",
            {"prompt": "x" * 40000},
            "output.mp4",
        )


def test_embed_recipe_fails_when_ffmpeg_fails(monkeypatch):
    calls = []

    class Result:
        returncode = 1
        stderr = b"broken ffmpeg"

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return Result()

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="ffmpeg metadata embedding failed"):
        recipe_module.embed_recipe(
            "input.mp4",
            {"prompt": "test"},
            "output.mp4",
        )

    assert len(calls) == 2
