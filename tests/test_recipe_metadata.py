"""Regression tests for recipe metadata embedding."""

import json
import subprocess

import pytest

from open_video.core import recipe as recipe_module


class Result:
    def __init__(self, returncode=0, stderr=b""):
        self.returncode = returncode
        self.stderr = stderr


def test_embed_recipe_oversized_skips_json_tag_keeps_per_key(monkeypatch, capsys):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return Result(0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    big_prompt = "x" * 40000
    monkeypatch.setattr(
        recipe_module, "read_recipe", lambda path: {"prompt": big_prompt}
    )

    out = recipe_module.embed_recipe(
        "input.mp4", {"prompt": big_prompt}, "output.mp4"
    )

    assert out == "output.mp4"
    assert len(calls) == 1
    assert f"openvideo_prompt={big_prompt}" in calls[0]
    assert not any("recipe_json" in arg for arg in calls[0])
    assert "warning" in capsys.readouterr().out.lower()


def test_embed_recipe_oversized_reencode_also_skips_json_tag(monkeypatch):
    calls = []
    results = iter([Result(1, b"stream copy failed"), Result(0)])

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return next(results)

    monkeypatch.setattr(subprocess, "run", fake_run)
    big_prompt = "x" * 40000
    monkeypatch.setattr(
        recipe_module, "read_recipe", lambda path: {"prompt": big_prompt}
    )

    recipe_module.embed_recipe(
        "input.mp4", {"prompt": big_prompt}, "output.mp4"
    )

    assert len(calls) == 2
    assert "libx264" in calls[1]
    assert f"openvideo_prompt={big_prompt}" in calls[1]
    assert not any("recipe_json" in arg for arg in calls[1])


def test_embed_recipe_oversized_fails_on_bad_perkey_metadata(monkeypatch):
    def fake_run(cmd, **kwargs):
        return Result(0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(
        recipe_module, "read_recipe", lambda path: {"prompt": "wrong"}
    )

    with pytest.raises(RuntimeError, match="verification failed"):
        recipe_module.embed_recipe(
            "input.mp4", {"prompt": "x" * 40000}, "output.mp4"
        )


def test_embed_recipe_verification_uses_json_round_trip(monkeypatch):
    def fake_run(cmd, **kwargs):
        return Result(0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    recipe = {"prompt": "test", "order": (1, 2)}
    # what ffprobe reads back after the JSON blob round-trips through the file
    monkeypatch.setattr(
        recipe_module,
        "read_recipe",
        lambda path: json.loads(json.dumps(recipe)),
    )

    out = recipe_module.embed_recipe("input.mp4", recipe, "output.mp4")

    assert out == "output.mp4"


def test_embed_recipe_fails_when_ffmpeg_fails(monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return Result(1, b"broken ffmpeg")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="ffmpeg metadata embedding failed"):
        recipe_module.embed_recipe(
            "input.mp4",
            {"prompt": "test"},
            "output.mp4",
        )

    assert len(calls) == 2
