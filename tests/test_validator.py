"""Tests for the mode-aware prompt validator."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Reuse the validator from core/ (ported from early lab/scripts/validate_prompt.py)
# The validator checks: 3 required fields, duration range, mode-specific constraints,
# timeline cut times, dialogue tags.
from open_video.core.validator import validate, detect_mode

FIELDS = ["integrated_multimodal_description", "overall_soundscape", "non_diegetic_music"]

GOOD_T2V = f"""{FIELDS[0]}: [Shot 1] Live-action, cinematic, a medium shot frames a lighthouse on a cliff at dusk. The camera pushes in with small amplitude at slow speed as the keeper looks out to sea.
{FIELDS[1]}: Wind howls, waves crash against rocks, the lighthouse mechanism groans.
{FIELDS[2]}: A solitary cello sustains a low, mournful note at a slow tempo."""

GOOD_I2V = f"""For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

{FIELDS[0]}: [Shot 1] The scene from <Picture 1> continues as the camera tracks right.
{FIELDS[1]}: Ambient environmental sounds.
{FIELDS[2]}: N/A"""

BAD_MISSING_FIELD = f"""{FIELDS[0]}: A shot of a cat.
{FIELDS[1]}: Meow sounds."""

BAD_DURATION = f"""{FIELDS[0]}: A shot of a cat.
{FIELDS[1]}: Meow sounds.
{FIELDS[2]}: N/A"""

BAD_DIALOGUE_TAG = f"""{FIELDS[0]}: [Shot 1] A character says <d>hello world</d>.
{FIELDS[1]}: Ambient.
{FIELDS[2]}: N/A"""


def test_good_t2v():
    mode, issues, warns = validate(GOOD_T2V, duration=10)
    assert mode == "t2v", f"Expected t2v, got {mode}"
    assert len(issues) == 0, f"Expected no issues, got {issues}"


def test_good_i2v():
    mode, issues, warns = validate(GOOD_I2V, duration=5, n_images=1)
    assert mode == "i2v", f"Expected i2v, got {mode}"
    assert len(issues) == 0, f"Expected no issues, got {issues}"


def test_missing_field():
    mode, issues, warns = validate(BAD_MISSING_FIELD, duration=5)
    assert len(issues) > 0, "Should detect missing non_diegetic_music field"


def test_bad_duration():
    mode, issues, warns = validate(BAD_DURATION, duration=20)
    assert len(issues) > 0, "Should detect duration 20s outside 4-15s range"


def test_bad_dialogue_tag():
    mode, issues, warns = validate(BAD_DIALOGUE_TAG, duration=5)
    # the validator should warn about <d> without [language] prefix
    assert len(warns) > 0 or len(issues) > 0, "Should flag dialogue tag without [language]"


def test_detect_mode_t2v():
    mode = detect_mode(GOOD_T2V, n_images=0)
    assert mode == "t2v"


def test_detect_mode_i2v():
    mode = detect_mode(GOOD_I2V, n_images=1)
    assert mode == "i2v"


if __name__ == "__main__":
    test_good_t2v()
    test_good_i2v()
    test_missing_field()
    test_bad_duration()
    test_bad_dialogue_tag()
    test_detect_mode_t2v()
    test_detect_mode_i2v()
    print("✅ All validator tests passed")
