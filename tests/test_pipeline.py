"""Tests for the LongFilmPipeline + Shot dataclass."""
import shutil
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from open_video.core.backend import ShotResult
from open_video.core.pipeline import Shot, LongFilmPipeline
from open_video.core.stitcher import Stitcher

_has_ffmpeg = shutil.which("ffmpeg") and shutil.which("ffprobe")


def test_shot_creation():
    """Shot dataclass creates correctly with all fields."""
    shot = Shot(scene_id=1, prompt="test prompt", mode="t2v", duration_s=10.0, seed=42)
    assert shot.scene_id == 1
    assert shot.prompt == "test prompt"
    assert shot.mode == "t2v"
    assert shot.duration_s == 10.0
    assert shot.seed == 42
    assert shot.video_path is None
    assert shot.verdict == ""


def test_shot_i2v():
    """Shot can be created for I2V mode with first_frame."""
    shot = Shot(scene_id=2, prompt="continuation", mode="i2v", duration_s=8.0, seed=100,
                first_frame="/path/to/frame.png")
    assert shot.mode == "i2v"
    assert shot.first_frame == "/path/to/frame.png"


def test_plan_construction():
    """A manual plan can be constructed from shot data."""
    shots = [
        Shot(scene_id=1, prompt="establishing shot", mode="t2v", duration_s=10.0, seed=1),
        Shot(scene_id=2, prompt="close-up", mode="i2v", duration_s=8.0, seed=2),
        Shot(scene_id=3, prompt="wide reveal", mode="i2v", duration_s=10.0, seed=3),
    ]
    assert len(shots) == 3
    assert shots[0].mode == "t2v"  # first shot is T2V
    assert shots[1].mode == "i2v"  # subsequent shots are I2V (FL2VA chain)
    total_duration = sum(s.duration_s for s in shots)
    assert total_duration == 28.0


def test_pipeline_init(tmp_path):
    """LongFilmPipeline can be initialized (without a running engine)."""
    # init without backend/engine — should not crash
    try:
        pipeline = LongFilmPipeline(backend=None, engine=None, output_dir=str(tmp_path / "ov"))
        assert pipeline.out.exists()
        assert pipeline.frames.exists()
    except Exception as e:
        assert False, f"Pipeline init should not crash: {e}"


def test_stitcher_single_shot_honors_output_path(tmp_path):
    """A single-shot film is copied to the requested output destination."""
    source = tmp_path / "generated.mp4"
    output = tmp_path / "custom" / "film.mp4"
    source.write_bytes(b"fake-video")

    result = Stitcher(output_dir=str(tmp_path)).concat([str(source)], str(output))

    assert result == str(output)
    assert output.exists()
    assert output.read_bytes() == b"fake-video"


# --- best-take bookkeeping + partial-film honesty ---

class _StubBackend:
    """Serves pre-rendered clips (or failures) in call order."""

    id = "stub"

    def __init__(self, results):
        self._results = list(results)
        self.seeds = []

    def resolution_for(self, _aspect):
        return (64, 36)

    def generate(self, req, engine=None):
        self.seeds.append(req.seed)
        item = self._results.pop(0)
        if isinstance(item, ShotResult):
            return item
        receipt = {"take_index": len(self.seeds), "gen_seed": req.seed}
        if len(self.seeds) == 2:
            receipt["second_take_only"] = True
        return ShotResult(ok=True, video_path=str(item), receipt=receipt)


def _tiny_mp4(path: Path, color: str):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
                    "-i", f"color=c={color}:s=64x36:d=0.5:r=8", "-pix_fmt", "yuv420p",
                    str(path)], check=True)


@pytest.mark.skipif(not _has_ffmpeg, reason="ffmpeg/ffprobe required")
def test_earlier_best_take_restores_seed_receipt_and_frames(tmp_path, monkeypatch):
    """Take 1 REFINEs (0.6), take 2 is worse (0.3): the shot must keep take 1's
    seed, generation receipt, judge score/issues, and take-1 frame paths."""
    monkeypatch.setenv("OPEN_VIDEO_JUDGE_RETRIES", "1")
    clip1, clip2 = tmp_path / "c1.mp4", tmp_path / "c2.mp4"
    _tiny_mp4(clip1, "red")
    _tiny_mp4(clip2, "blue")
    backend = _StubBackend([clip1, clip2])
    scores = iter([0.6, 0.3])
    vision_fn = lambda *_: {"score": next(scores), "missing_elements": [],
                            "artifacts": "", "motion_quality": "good", "incoherence": False}
    pipe = LongFilmPipeline(backend=backend, engine=None,
                            output_dir=str(tmp_path / "out"), vision_fn=vision_fn)
    shot = Shot(scene_id=1, prompt="clip", mode="t2v", duration_s=0.5, seed=42)

    assert pipe._run_shot(shot) is True  # REFINE is not a failure

    assert backend.seeds == [42, 142]
    assert shot.seed == 42, "shot must record the chosen take's seed, not the original bump"
    assert shot.video_path == str(clip1)
    assert shot.verdict == "REFINE"
    assert shot.receipt["judge_score"] == 0.6
    assert shot.receipt["take_index"] == 1, "generation receipt must be take 1's"
    assert shot.receipt["gen_seed"] == 42
    assert "second_take_only" not in shot.receipt
    frames = shot.receipt["judge_frames"]
    assert frames and all("/take1/" in f and Path(f).exists() for f in frames)
    take2_frames = list((tmp_path / "out" / "frames" / "take2").glob("*.png"))
    assert take2_frames, "take 2 frames stay on disk, distinct from take 1"
    takes = shot.receipt["takes"]
    assert [t["seed"] for t in takes] == [42, 142]
    assert [t["judge_score"] for t in takes] == [0.6, 0.3]


def test_failed_second_shot_yields_no_partial_film(tmp_path, monkeypatch):
    """If any requested shot fails, make_film returns (None, plan) and writes no
    film file — a partial concat must never be reported as the completed film."""
    monkeypatch.delenv("OPEN_VIDEO_VLM_URL", raising=False)
    monkeypatch.delenv("OPEN_VIDEO_VLM_MODEL", raising=False)
    monkeypatch.setenv("OPEN_VIDEO_JUDGE_RETRIES", "0")
    backend = _StubBackend([tmp_path / "shot1.mp4", ShotResult(ok=False, error="boom")])
    pipe = LongFilmPipeline(backend=backend, engine=None, output_dir=str(tmp_path / "out"))
    # shot 1 is "generated" but unjudged (SKIPPED) — extraction and the FL2VA
    # last-frame handoff are stubbed so no real clip/ffmpeg is needed here
    monkeypatch.setattr(pipe._judge, "extract_frames", lambda *_a, **_k: ["f.png"])
    monkeypatch.setattr(pipe._stitcher, "extract_last_frame", lambda *_a, **_k: None)

    out_path = tmp_path / "film.mp4"
    plan = [Shot(scene_id=1, prompt="one", seed=1), Shot(scene_id=2, prompt="two", seed=2)]
    film, final_plan = pipe.make_film(plan, out_path=str(out_path))

    assert film is None
    assert final_plan is plan
    assert not out_path.exists()
    assert plan[0].verdict == "SKIPPED"
    assert plan[1].verdict == "FAIL"
    assert plan[1].receipt["error"] == "boom"


def test_build_recipe_propagates_skipped(tmp_path):
    """quality_verdict reports SKIPPED honestly instead of claiming PASS."""
    pipe = LongFilmPipeline(backend=None, engine=None, output_dir=str(tmp_path / "out"))

    def plan_with(*verdicts):
        return [Shot(scene_id=i + 1, prompt="p", video_path=f"v{i}.mp4", verdict=v)
                for i, v in enumerate(verdicts)]

    assert pipe._build_recipe(plan_with("SKIPPED"), "f.mp4")["quality_verdict"] == "SKIPPED"
    assert pipe._build_recipe(plan_with("PASS", "SKIPPED"), "f.mp4")["quality_verdict"] == "SKIPPED"
    assert pipe._build_recipe(plan_with("REFINE", "SKIPPED"), "f.mp4")["quality_verdict"] == "REFINE"
    assert pipe._build_recipe(plan_with("PASS", "PASS"), "f.mp4")["quality_verdict"] == "PASS"


def test_recipe_distinguishes_model_engine_and_generated_duration(tmp_path):
    from types import SimpleNamespace
    pipe = LongFilmPipeline(backend=SimpleNamespace(id="minimax-h3"),
                            engine=SimpleNamespace(id="comfyui"), output_dir=str(tmp_path))
    shot = Shot(scene_id=1, prompt="p", seed=107, duration_s=4,
                video_path="clip.mp4", verdict="SKIPPED",
                receipt={"duration_s": 107 / 24, "width": 1344, "height": 768,
                         "steps": 20, "sampler": "res_multistep", "scheduler": "simple"})
    recipe = pipe._build_recipe([shot], "film.mp4")
    assert recipe["model"] == "minimax-h3"
    assert recipe["engine"] == "comfyui"
    assert recipe["seed"] == 107
    assert recipe["duration_s"] == 107 / 24
    assert recipe["steps"] == 20
    assert recipe["width"] == 1344


if __name__ == "__main__":
    test_shot_creation()
    test_shot_i2v()
    test_plan_construction()
    print("✅ All pipeline tests passed")
