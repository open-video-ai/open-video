"""Tests for the LongFilmPipeline + Shot dataclass."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from open_video.core.pipeline import Shot, LongFilmPipeline


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


def test_pipeline_init():
    """LongFilmPipeline can be initialized (without a running engine)."""
    # init without backend/engine — should not crash
    try:
        pipeline = LongFilmPipeline(backend=None, engine=None, output_dir="/tmp/ov_test")
        assert pipeline.out.exists()
        assert pipeline.frames.exists()
    except Exception as e:
        assert False, f"Pipeline init should not crash: {e}"


if __name__ == "__main__":
    test_shot_creation()
    test_shot_i2v()
    test_plan_construction()
    test_pipeline_init()
    print("✅ All pipeline tests passed")
