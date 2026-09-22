"""Real-path tests for the OpenAI-compatible VLM judge wiring.

A local HTTP server plays the vision endpoint (no mocks of our own code):
make_vision_fn does real urllib POSTs; parsing, diagnosis, and env activation
are asserted against captured requests and real return values.
"""
import base64
import json
import shutil
import subprocess

import pytest
from conftest import CannedJSONHandler, serve

from open_video.judges.openai_compat import (
    make_vision_fn,
    vision_fn_from_env,
    _parse_verdict,
)
from open_video.core.judge import QualityJudge
from open_video.judges.vision import VisionJudge

# 1x1 transparent PNG
_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


def _endpoint(verdict_content: str):
    """Local OpenAI-style chat endpoint capturing requests, serving a canned verdict."""
    requests = []

    class Handler(CannedJSONHandler):
        def do_POST(self):
            requests.append({"headers": dict(self.headers), "body": self.read_json()})
            self.reply({"choices": [{"message": {"content": verdict_content}}]})

    url, close = serve(Handler)
    return f"{url}/v1/chat/completions", close, requests


def _frames(tmp_path, n=2):
    paths = []
    for i in range(n):
        p = tmp_path / f"f{i}.png"
        p.write_bytes(_PNG)
        paths.append(str(p))
    return paths


def test_vision_fn_posts_frames_and_parses_verdict(tmp_path):
    url, close, requests = _endpoint(json.dumps(
        {"score": 0.9, "missing_elements": [], "artifacts": "",
         "motion_quality": "good", "incoherence": False}))
    try:
        out = make_vision_fn(url, "test-vlm", api_key="sk-test")(_frames(tmp_path), "waves at sunset")
    finally:
        close()
    assert out["score"] == 0.9
    req = requests[0]
    assert req["headers"]["Authorization"] == "Bearer sk-test"
    assert req["body"]["model"] == "test-vlm"
    user = req["body"]["messages"][1]["content"]
    images = [part for part in user if part["type"] == "image_url"]
    assert len(images) == 2
    assert images[0]["image_url"]["url"].startswith("data:image/png;base64,")
    assert "waves at sunset" in user[0]["text"]


def test_low_score_yields_refine_with_issues(tmp_path):
    verdict = {"score": 0.3, "missing_elements": ["flag"], "artifacts": "banding",
               "motion_quality": "poor", "incoherence": False}
    url, close, _ = _endpoint(f"```json\n{json.dumps(verdict)}\n```")  # fenced reply tolerated
    try:
        judge = QualityJudge(vision_fn=make_vision_fn(url, "test-vlm"))
        raw = judge.vision_fn(_frames(tmp_path), "astronaut plants a flag")
        issues = judge.diagnose(raw, "astronaut plants a flag")
    finally:
        close()
    assert raw["score"] == 0.3
    assert {"dropped_element", "artifact", "bad_motion"} <= {i.type for i in issues}


def test_non_json_reply_raises(tmp_path):
    url, close, _ = _endpoint("Sure! The video looks great to me.")
    try:
        with pytest.raises(ValueError):
            make_vision_fn(url, "test-vlm")(_frames(tmp_path), "anything")
    finally:
        close()


def test_parse_verdict_requires_score():
    with pytest.raises(ValueError):
        _parse_verdict('{"notes": "no score here"}')


def test_env_activation(monkeypatch):
    monkeypatch.delenv("OPEN_VIDEO_VLM_URL", raising=False)
    monkeypatch.delenv("OPEN_VIDEO_VLM_MODEL", raising=False)
    assert vision_fn_from_env() is None
    assert QualityJudge.from_env().vision_fn is None

    monkeypatch.setenv("OPEN_VIDEO_VLM_URL", "http://127.0.0.1:9/v1/chat/completions")
    monkeypatch.setenv("OPEN_VIDEO_VLM_MODEL", "test-vlm")
    assert vision_fn_from_env() is not None
    assert QualityJudge.from_env().vision_fn is not None


def test_diagnose_ignores_stringly_false_flags():
    """VLMs emit 'false' as a string; it must not create spurious issues (film60 field bug)."""
    judge = QualityJudge()
    raw = {"score": 0.8, "missing_elements": [], "artifacts": "none",
           "motion_quality": "good", "incoherence": "false"}
    assert judge.diagnose(raw, "prompt") == []
    raw_bad = {"score": 0.4, "missing_elements": [], "artifacts": "heavy banding",
               "motion_quality": "good", "incoherence": "frames jump around"}
    assert {i.type for i in judge.diagnose(raw_bad, "p")} == {"artifact", "incoherence"}


def test_assess_normalizes_numeric_string_score(monkeypatch):
    """A VLM JSON payload may encode a numeric score as a string."""
    judge = QualityJudge(
        vision_fn=lambda _frames, _prompt: {
            "score": "0.9",
            "missing_elements": [],
            "artifacts": "",
            "motion_quality": "good",
            "incoherence": False,
        }
    )
    monkeypatch.setattr(judge, "extract_frames", lambda *_args, **_kwargs: ["frame.png"])

    verdict = judge.assess("clip.mp4", "a blue test clip")

    assert verdict.verdict == "PASS"
    assert verdict.score == 0.9


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("not-a-number", 0.0),
        (None, 0.0),
        (float("nan"), 0.0),
        (-0.2, 0.0),
        (1.4, 1.0),
    ],
)
def test_score_normalization_is_finite_and_bounded(value, expected):
    assert QualityJudge._score(value) == expected


@pytest.mark.parametrize("issues", [["invalid-entry"], "invalid-list", {"detail": "invalid"}])
def test_vision_plugin_rejects_malformed_issues(monkeypatch, issues):
    from open_video.judges.vision import VisionJudge
    judge = VisionJudge(vlm_api=lambda *_: {"score": 0.9, "issues": issues})
    monkeypatch.setattr(judge, "extract_frames", lambda *_: ["frame.png"])
    verdict = judge.assess("clip.mp4", "p")
    assert verdict.verdict == "FAIL"
    assert verdict.score == 0.0


# --- honest verdicts: SKIPPED / FAIL can never masquerade as PASS ---

def _judge_with_frames(vision_fn, monkeypatch):
    """QualityJudge whose extract_frames is stubbed to one fake frame."""
    judge = QualityJudge(vision_fn=vision_fn)
    monkeypatch.setattr(judge, "extract_frames", lambda *_a, **_k: ["frame.png"])
    return judge


def test_no_vision_fn_is_skipped_not_pass(monkeypatch):
    """No configured VLM must report SKIPPED 0.0 — never PASS 1.0."""
    verdict = _judge_with_frames(None, monkeypatch).assess("clip.mp4", "p")
    assert verdict.verdict == "SKIPPED"
    assert verdict.score == 0.0
    assert verdict.frames == ["frame.png"]

    vj = VisionJudge(vlm_api=None)
    monkeypatch.setattr(vj, "extract_frames", lambda *_a, **_k: ["frame.png"])
    verdict = vj.assess("clip.mp4", "p")
    assert verdict.verdict == "SKIPPED" and verdict.score == 0.0


def test_missing_frames_fail_scores_zero(monkeypatch):
    """Extraction failure is FAIL with score 0.0 (was: FAIL with default 1.0)."""
    judge = QualityJudge(vision_fn=lambda *_: {"score": 0.9})
    monkeypatch.setattr(judge, "extract_frames", lambda *_a, **_k: [])
    verdict = judge.assess("clip.mp4", "p")
    assert verdict.verdict == "FAIL" and verdict.score == 0.0

    vj = VisionJudge(vlm_api=lambda *_: {"score": 0.9})
    monkeypatch.setattr(vj, "extract_frames", lambda *_a, **_k: [])
    verdict = vj.assess("clip.mp4", "p")
    assert verdict.verdict == "FAIL" and verdict.score == 0.0


def test_empty_callback_dict_cannot_pass(monkeypatch):
    """A vision_fn returning {} has no usable score → FAIL, not default-PASS."""
    verdict = _judge_with_frames(lambda *_: {}, monkeypatch).assess("clip.mp4", "p")
    assert verdict.verdict == "FAIL"
    assert verdict.score == 0.0
    assert verdict.issues[0].type == "judge_error"


@pytest.mark.parametrize(
    "raw",
    [
        {"score": "not-a-number"},
        {"score": None},
        {"score": float("nan")},
        {"score": float("inf")},
        "not-a-dict",
        None,
    ],
)
def test_invalid_or_nonfinite_callback_result_cannot_pass(raw, monkeypatch):
    verdict = _judge_with_frames(lambda *_: raw, monkeypatch).assess("clip.mp4", "p")
    assert verdict.verdict == "FAIL"
    assert verdict.score == 0.0


def test_vision_fn_exception_fails_without_leaking_secret(monkeypatch):
    """A raising callback → FAIL; the issue detail must not echo the message
    (it can carry endpoint URLs/credentials)."""

    def boom(*_):
        raise RuntimeError("connect to https://user:sk-secret@vlm.internal failed")

    verdict = _judge_with_frames(boom, monkeypatch).assess("clip.mp4", "p")
    assert verdict.verdict == "FAIL" and verdict.score == 0.0
    detail = verdict.issues[0].detail
    assert "RuntimeError" in detail
    assert "sk-secret" not in detail and "vlm.internal" not in detail


@pytest.mark.parametrize(
    ("score", "expected"),
    [(0.9, "PASS"), (0.7, "PASS"), (0.2, "REFINE")],
)
def test_finite_scores_pass_or_refine(score, expected, monkeypatch):
    """Valid finite scores keep the original PASS/REFINE semantics."""
    raw = {"score": score, "missing_elements": [], "artifacts": "",
           "motion_quality": "good", "incoherence": False}
    verdict = _judge_with_frames(lambda *_: raw, monkeypatch).assess("clip.mp4", "p")
    assert verdict.verdict == expected
    assert verdict.score == score


def test_vision_judge_invalid_frame_score_fails(monkeypatch):
    """VisionJudge: a per-frame result without a usable score → FAIL."""
    vj = VisionJudge(vlm_api=lambda *_: {})
    monkeypatch.setattr(vj, "extract_frames", lambda *_a, **_k: ["f.png"])
    verdict = vj.assess("clip.mp4", "p")
    assert verdict.verdict == "FAIL" and verdict.score == 0.0


# --- extraction honesty: no stale frames, missing ffmpeg is a clean FAIL ---

def test_extract_frames_missing_ffmpeg_returns_empty(monkeypatch, tmp_path):
    """No ffmpeg/ffprobe on PATH → extraction returns [], assess reports FAIL."""

    def no_binary(*_a, **_k):
        raise FileNotFoundError("ffmpeg")

    monkeypatch.setattr(subprocess, "run", no_binary)
    judge = QualityJudge(vision_fn=lambda *_: {"score": 0.9})
    assert judge.extract_frames("clip.mp4", 1, str(tmp_path)) == []
    verdict = judge.assess("clip.mp4", "p", shot_id=1, frames_dir=str(tmp_path))
    assert verdict.verdict == "FAIL" and verdict.score == 0.0


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg required")
def test_extract_frames_ffmpeg_failure_drops_stale_files(tmp_path):
    """Pre-existing sel files from another take must not be recycled when the
    ffmpeg run fails (stale-frame reuse bug)."""
    frames_dir = tmp_path / "frames"
    frames_dir.mkdir()
    for k in range(1, 4):
        (frames_dir / f"shot1_sel{k}.png").write_bytes(b"stale")
    bogus = tmp_path / "not-a-video.mp4"
    bogus.write_bytes(b"this is not a video")

    judge = QualityJudge()
    assert judge.extract_frames(str(bogus), 1, str(frames_dir)) == []
    assert not list(frames_dir.glob("shot1_sel*.png")), "stale sel files must be cleared"


@pytest.mark.skipif(not (shutil.which("ffmpeg") and shutil.which("ffprobe")),
                    reason="ffmpeg/ffprobe required")
def test_extract_frames_real_ffmpeg(tmp_path):
    """Real extraction on a real clip yields real frame files."""
    clip = tmp_path / "clip.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
                    "-i", "color=c=red:s=64x36:d=0.5:r=8", "-pix_fmt", "yuv420p",
                    str(clip)], check=True)
    judge = QualityJudge(n_frames=3)
    frames = judge.extract_frames(str(clip), 1, str(tmp_path / "frames"))
    assert len(frames) == 3
    assert all((tmp_path / "frames" / f).name == f.split("/")[-1] for f in frames)
