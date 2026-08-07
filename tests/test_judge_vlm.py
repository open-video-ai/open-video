"""Real-path tests for the OpenAI-compatible VLM judge wiring.

A local HTTP server plays the vision endpoint (no mocks of our own code):
make_vision_fn does real urllib POSTs; parsing, diagnosis, and env activation
are asserted against captured requests and real return values.
"""
import base64
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from open_video.judges.openai_compat import (  # noqa: E402
    make_vision_fn,
    vision_fn_from_env,
    _parse_verdict,
)
from open_video.core.judge import QualityJudge  # noqa: E402

# 1x1 transparent PNG
_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


class _Endpoint:
    """Local OpenAI-style chat endpoint capturing requests, serving a canned verdict."""

    def __init__(self, verdict_content: str):
        self.requests = []
        endpoint = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                endpoint.requests.append({"headers": dict(self.headers), "body": body})
                reply = {"choices": [{"message": {"content": verdict_content}}]}
                data = json.dumps(reply).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *a):
                pass

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}/v1/chat/completions"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def _frames(tmp_path, n=2):
    paths = []
    for i in range(n):
        p = tmp_path / f"f{i}.png"
        p.write_bytes(_PNG)
        paths.append(str(p))
    return paths


def test_vision_fn_posts_frames_and_parses_verdict(tmp_path):
    ep = _Endpoint(json.dumps({"score": 0.9, "missing_elements": [], "artifacts": "",
                               "motion_quality": "good", "incoherence": False}))
    try:
        fn = make_vision_fn(ep.url, "test-vlm", api_key="sk-test")
        out = fn(_frames(tmp_path), "waves at sunset")
    finally:
        ep.close()
    assert out["score"] == 0.9
    req = ep.requests[0]
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
    ep = _Endpoint(f"```json\n{json.dumps(verdict)}\n```")  # fenced reply tolerated
    try:
        judge = QualityJudge(vision_fn=make_vision_fn(ep.url, "test-vlm"))
        raw = judge.vision_fn(_frames(tmp_path), "astronaut plants a flag")
        issues = judge.diagnose(raw, "astronaut plants a flag")
        verdict_out = "PASS" if raw["score"] >= judge.bar and not issues else "REFINE"
    finally:
        ep.close()
    assert raw["score"] == 0.3
    types = {i.type for i in issues}
    assert {"dropped_element", "artifact", "bad_motion"} <= types
    assert verdict_out == "REFINE"


def test_non_json_reply_raises(tmp_path):
    ep = _Endpoint("Sure! The video looks great to me.")
    try:
        fn = make_vision_fn(ep.url, "test-vlm")
        try:
            fn(_frames(tmp_path), "anything")
            raised = False
        except ValueError:
            raised = True
    finally:
        ep.close()
    assert raised, "a judge that cannot parse a verdict must raise, not silently PASS"


def test_parse_verdict_requires_score():
    try:
        _parse_verdict('{"notes": "no score here"}')
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_env_activation(monkeypatch):
    monkeypatch.delenv("OPEN_VIDEO_VLM_URL", raising=False)
    monkeypatch.delenv("OPEN_VIDEO_VLM_MODEL", raising=False)
    assert vision_fn_from_env() is None
    assert QualityJudge.from_env().vision_fn is None

    monkeypatch.setenv("OPEN_VIDEO_VLM_URL", "http://127.0.0.1:9/v1/chat/completions")
    monkeypatch.setenv("OPEN_VIDEO_VLM_MODEL", "test-vlm")
    assert vision_fn_from_env() is not None
    assert QualityJudge.from_env().vision_fn is not None
