"""Real-path tests for the OpenAI-compatible VLM judge wiring.

A local HTTP server plays the vision endpoint (no mocks of our own code):
make_vision_fn does real urllib POSTs; parsing, diagnosis, and env activation
are asserted against captured requests and real return values.
"""
import base64
import json

import pytest
from conftest import CannedJSONHandler, serve

from open_video.judges.openai_compat import (
    make_vision_fn,
    vision_fn_from_env,
    _parse_verdict,
)
from open_video.core.judge import QualityJudge

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
