"""Regression tests for recipe metadata embedding."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from open_video.core import recipe as recipe_module


class Result:
    def __init__(self, returncode=0, stderr=b""):
        self.returncode = returncode
        self.stderr = stderr


def ffmpeg_calls(calls):
    """embed_recipe probes input tags via ffprobe first; select ffmpeg calls."""
    return [c for c in calls if c[0] == "ffmpeg"]


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
    calls = ffmpeg_calls(calls)
    assert len(calls) == 1
    assert f"openvideo_prompt={big_prompt}" in calls[0]
    assert "openvideo_recipe_json=" in calls[0]
    assert "warning" in capsys.readouterr().out.lower()


def test_embed_recipe_oversized_reencode_also_skips_json_tag(monkeypatch):
    calls = []
    results = iter([Result(1, b"stream copy failed"), Result(0)])

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if cmd[0] == "ffprobe":
            return Result(0)
        return next(results)

    monkeypatch.setattr(subprocess, "run", fake_run)
    big_prompt = "x" * 40000
    monkeypatch.setattr(
        recipe_module, "read_recipe", lambda path: {"prompt": big_prompt}
    )

    recipe_module.embed_recipe(
        "input.mp4", {"prompt": big_prompt}, "output.mp4"
    )

    calls = ffmpeg_calls(calls)
    assert len(calls) == 2
    assert "libx264" in calls[1]
    assert f"openvideo_prompt={big_prompt}" in calls[1]
    assert "openvideo_recipe_json=" in calls[1]


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

    assert len(ffmpeg_calls(calls)) == 2


def test_embed_recipe_passes_movflags_use_metadata_tags(monkeypatch):
    """MP4 muxer drops non-standard keys unless -movflags use_metadata_tags."""
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return Result(0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    recipe = {"prompt": "test"}
    monkeypatch.setattr(recipe_module, "read_recipe", lambda path: recipe)

    recipe_module.embed_recipe("input.mp4", recipe, "output.mp4")

    calls = ffmpeg_calls(calls)
    assert len(calls) == 1
    movflags = calls[0][calls[0].index("-movflags") + 1]
    assert movflags == "use_metadata_tags"


def test_embed_recipe_reencode_also_passes_movflags(monkeypatch):
    calls = []
    results = iter([Result(1, b"stream copy failed"), Result(0)])

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if cmd[0] == "ffprobe":
            return Result(0)
        return next(results)

    monkeypatch.setattr(subprocess, "run", fake_run)
    recipe = {"prompt": "test"}
    monkeypatch.setattr(recipe_module, "read_recipe", lambda path: recipe)

    recipe_module.embed_recipe("input.mp4", recipe, "output.mp4")

    calls = ffmpeg_calls(calls)
    assert len(calls) == 2
    assert "libx264" in calls[1]
    movflags = calls[1][calls[1].index("-movflags") + 1]
    assert movflags == "use_metadata_tags"


def test_embed_recipe_in_place_uses_temp_file_and_replaces(monkeypatch, tmp_path):
    """In-place embed must mux to a sibling temp file, verify it, then
    atomically os.replace the original (ffmpeg cannot overwrite its input)."""
    src = tmp_path / "film.mp4"
    src.write_bytes(b"original")
    calls = []
    probed = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if cmd[0] == "ffmpeg":
            Path(cmd[-1]).write_bytes(b"muxed")
        return Result(0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    recipe = {"prompt": "test"}
    monkeypatch.setattr(
        recipe_module,
        "read_recipe",
        lambda path: probed.append(path) or recipe,
    )

    out = recipe_module.embed_recipe(str(src), recipe)

    assert out == str(src)
    ffmpeg_out = ffmpeg_calls(calls)[0][-1]
    assert ffmpeg_out != str(src)
    assert Path(ffmpeg_out).parent == src.parent  # same dir → atomic os.replace
    # verification ran on the temp file before it replaced the original
    assert probed == [ffmpeg_out]
    assert src.read_bytes() == b"muxed"


def test_embed_recipe_in_place_failure_preserves_original(monkeypatch, tmp_path):
    src = tmp_path / "film.mp4"
    src.write_bytes(b"original")

    def fake_run(cmd, **kwargs):
        return Result(1, b"broken ffmpeg")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="ffmpeg metadata embedding failed"):
        recipe_module.embed_recipe(str(src), {"prompt": "test"})

    assert src.read_bytes() == b"original"
    assert list(tmp_path.iterdir()) == [src]  # temp file cleaned up


def test_embed_recipe_in_place_ffmpeg_timeout_cleans_temp(monkeypatch, tmp_path):
    src = tmp_path / "film.mp4"
    src.write_bytes(b"original")

    def fake_run(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout") or 60)

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(subprocess.TimeoutExpired):
        recipe_module.embed_recipe(str(src), {"prompt": "test"})

    assert src.read_bytes() == b"original"
    assert list(tmp_path.iterdir()) == [src]


def test_embed_recipe_in_place_reencode_timeout_cleans_temp(monkeypatch, tmp_path):
    src = tmp_path / "film.mp4"
    src.write_bytes(b"original")
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if len(calls) == 1:
            return Result(1, b"stream copy failed")
        raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout") or 300)

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(subprocess.TimeoutExpired):
        recipe_module.embed_recipe(str(src), {"prompt": "test"})

    assert src.read_bytes() == b"original"
    assert list(tmp_path.iterdir()) == [src]


def test_embed_recipe_in_place_probe_timeout_cleans_temp(monkeypatch, tmp_path):
    src = tmp_path / "film.mp4"
    src.write_bytes(b"original")

    def fake_run(cmd, **kwargs):
        if cmd[0] == "ffprobe":
            raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout") or 15)
        if cmd[0] == "ffmpeg":
            Path(cmd[-1]).write_bytes(b"muxed")
        return Result(0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(subprocess.TimeoutExpired):
        recipe_module.embed_recipe(str(src), {"prompt": "test"})

    assert src.read_bytes() == b"original"
    assert list(tmp_path.iterdir()) == [src]


def test_embed_recipe_in_place_unserializable_recipe_cleans_temp(
    monkeypatch, tmp_path
):
    src = tmp_path / "film.mp4"
    src.write_bytes(b"original")
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: Result(0))

    with pytest.raises(TypeError):
        recipe_module.embed_recipe(str(src), {"prompt": object()})

    assert src.read_bytes() == b"original"
    assert list(tmp_path.iterdir()) == [src]


def test_embed_recipe_in_place_verification_failure_cleans_temp(
    monkeypatch, tmp_path
):
    src = tmp_path / "film.mp4"
    src.write_bytes(b"original")

    def fake_run(cmd, **kwargs):
        if cmd[0] == "ffmpeg":
            Path(cmd[-1]).write_bytes(b"muxed")
        return Result(0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(
        recipe_module, "read_recipe", lambda path: {"prompt": "wrong"}
    )

    with pytest.raises(RuntimeError, match="verification failed"):
        recipe_module.embed_recipe(str(src), {"prompt": "test"})

    assert src.read_bytes() == b"original"
    assert list(tmp_path.iterdir()) == [src]


def test_embed_recipe_clears_stale_owned_tags(monkeypatch):
    """Replacing a recipe must clear every openvideo_* tag already on the
    input — omitted keys, None values and case variants — while leaving
    unrelated metadata alone."""
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if cmd[0] == "ffprobe":
            r = Result(0)
            r.stdout = json.dumps({"format": {"tags": {
                "openvideo_seed": "7",
                "OPENVIDEO_LORA": "old",
                "openvideo_recipe_json": "{}",
                "comment": "keep",
            }}})
            return r
        return Result(0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    recipe = {"prompt": "new", "seed": None}
    monkeypatch.setattr(
        recipe_module, "read_recipe",
        lambda path: json.loads(json.dumps(recipe)),
    )

    recipe_module.embed_recipe("input.mp4", recipe, "output.mp4")

    ffmpeg_cmd = next(c for c in calls if c[0] == "ffmpeg")
    md = [ffmpeg_cmd[i + 1] for i, a in enumerate(ffmpeg_cmd)
          if a == "-metadata"]
    assert "openvideo_seed=" in md
    assert "OPENVIDEO_LORA=" in md
    assert md[-1].startswith("openvideo_recipe_json={")
    assert md.index("openvideo_recipe_json=") < len(md) - 1
    assert "openvideo_prompt=new" in md
    # clears precede sets so keys present in the new recipe win
    assert md.index("openvideo_seed=") < md.index("openvideo_prompt=new")
    assert not any(m.startswith("comment=") for m in md)


def test_embed_recipe_probe_failure_still_sets_metadata(monkeypatch):
    """If the input can't be probed (missing/corrupt), embed still writes the
    new recipe tags rather than crashing."""
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if cmd[0] == "ffprobe":
            return Result(1, b"no such file")
        return Result(0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(
        recipe_module, "read_recipe", lambda path: {"prompt": "new"}
    )

    recipe_module.embed_recipe("input.mp4", {"prompt": "new"}, "output.mp4")

    ffmpeg_cmd = next(c for c in calls if c[0] == "ffmpeg")
    assert "openvideo_prompt=new" in ffmpeg_cmd


NEEDS_FFMPEG = pytest.mark.skipif(
    not shutil.which("ffmpeg") or not shutil.which("ffprobe"),
    reason="requires ffmpeg and ffprobe",
)


def _make_video(path):
    subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
         "color=c=blue:s=64x64:d=0.2", "-c:v", "mpeg4", str(path)],
        check=True, capture_output=True, timeout=20,
    )


def _probe_tags(video):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-of", "json", str(video)],
        check=True, capture_output=True, text=True, timeout=15,
    )
    return json.loads(r.stdout)["format"].get("tags", {})


@NEEDS_FFMPEG
def test_replacing_recipe_clears_stale_seed_and_case_variants(tmp_path):
    video = tmp_path / "film with spaces.mp4"
    _make_video(video)
    recipe_module.embed_recipe(str(video), {"prompt": "old", "seed": 7})
    # plant a mixed-case stale tag plus an unrelated tag via ffmpeg itself
    staged = tmp_path / "staged.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(video),
         "-metadata", "OPENVIDEO_LORA=old", "-metadata", "comment=keep",
         "-movflags", "use_metadata_tags", "-c", "copy", str(staged)],
        check=True, capture_output=True, timeout=20,
    )
    staged.replace(video)

    recipe_module.embed_recipe(str(video), {"prompt": "new"})

    assert recipe_module.read_recipe(str(video)) == {"prompt": "new"}
    tags = _probe_tags(video)
    owned = {k.lower() for k in tags if k.lower().startswith("openvideo_")}
    assert owned == {"openvideo_prompt", "openvideo_recipe_json"}
    assert tags.get("comment") == "keep"
    assert list(tmp_path.iterdir()) == [video]


@NEEDS_FFMPEG
def test_oversized_replacement_clears_stale_seed(tmp_path):
    """seed=7 -> oversized replacement with no seed: no stale seed remains."""
    video = tmp_path / "film.mp4"
    _make_video(video)
    recipe_module.embed_recipe(str(video), {"prompt": "old", "seed": 7})

    replacement = {"prompt": "x" * 33000}
    recipe_module.embed_recipe(str(video), replacement)

    assert recipe_module.read_recipe(str(video)) == replacement
    tags = _probe_tags(video)
    assert not any(k.lower() == "openvideo_seed" for k in tags)
    assert not any(k.lower() == "openvideo_recipe_json" for k in tags)
    assert list(tmp_path.iterdir()) == [video]


@NEEDS_FFMPEG
def test_embed_empty_recipe_roundtrips(tmp_path):
    video = tmp_path / "film.mp4"
    _make_video(video)
    recipe_module.embed_recipe(str(video), {"prompt": "old", "seed": 7})
    recipe_module.embed_recipe(str(video), {})
    assert recipe_module.read_recipe(str(video)) == {}
    assert list(tmp_path.iterdir()) == [video]


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"),
                    reason="requires ffmpeg and ffprobe")
def test_oversized_recipe_replaces_existing_json_metadata(tmp_path):
    video = tmp_path / "film.mp4"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
         "color=c=blue:s=64x64:d=0.2", "-c:v", "mpeg4", str(video)],
        check=True, capture_output=True, timeout=20,
    )
    recipe_module.embed_recipe(str(video), {"prompt": "old recipe"})
    replacement = {"prompt": "x" * 33000}
    recipe_module.embed_recipe(str(video), replacement)
    assert recipe_module.read_recipe(str(video)) == replacement
    assert list(tmp_path.iterdir()) == [video]
