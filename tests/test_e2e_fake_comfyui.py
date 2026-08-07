"""End-to-end generation-path test against a fake ComfyUI server.

The first regression protection for the main path: a real local HTTP server
implements /prompt, /history/{id}, /view; H3Backend builds the real workflow
JSON, ComfyUIAdapter does real urllib polling and file download, and Stitcher
runs real ffmpeg on the downloaded clip. Requires ffmpeg/ffprobe (CI installs
them; locally they're already a runtime dependency).
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest
from conftest import CannedJSONHandler, serve

from open_video.backends.h3.backend import H3Backend
from open_video.core.backend import ShotRequest
from open_video.core.stitcher import Stitcher
from open_video.engines.comfyui.adapter import ComfyUIAdapter

assert shutil.which("ffmpeg") and shutil.which("ffprobe"), (
    "ffmpeg/ffprobe are required for the e2e test (runtime deps of the product)"
)


def _tiny_mp4(path: Path, seconds: float = 0.5) -> bytes:
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
         "-i", f"color=c=blue:s=64x36:d={seconds}:r=8", "-pix_fmt", "yuv420p", str(path)],
        check=True,
    )
    return path.read_bytes()


def _duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


class FakeComfy:
    """Minimal ComfyUI HTTP facade: /prompt, /history/{id}, /view, /system_stats."""

    def __init__(self, clip_bytes: bytes, pending_polls: int = 2):
        self.submitted = []
        self.history_calls = 0
        fake = self

        class Handler(CannedJSONHandler):
            def do_GET(self):
                if self.path.startswith("/system_stats"):
                    self.reply({"system": {"comfyui_version": "fake"}})
                elif self.path.startswith("/history/"):
                    fake.history_calls += 1
                    pid = self.path.rsplit("/", 1)[1]
                    if fake.history_calls <= pending_polls:
                        self.reply({})  # still running
                    else:
                        self.reply({pid: {
                            "status": {"status_str": "success", "completed": True},
                            "outputs": {"save_video": {
                                "gifs": [{"filename": "clip.mp4", "subfolder": ""}]}},
                        }})
                elif self.path.startswith("/view"):
                    self.reply(raw=clip_bytes, ctype="video/mp4")
                else:
                    self.send_error(404)

            def do_POST(self):
                fake.submitted.append(self.read_json())
                self.reply({"prompt_id": f"fake-{len(fake.submitted)}"})

        self.url, self._close = serve(Handler)

    def close(self):
        self._close()


def test_backend_generate_end_to_end(tmp_path):
    clip = _tiny_mp4(tmp_path / "src.mp4")
    fake = FakeComfy(clip)
    try:
        engine = ComfyUIAdapter(server=fake.url, output_dir=str(tmp_path / "out"))
        assert engine.health()
        backend = H3Backend()
        req = ShotRequest(prompt="a blue test pattern, static camera", mode="t2v",
                          width=64, height=36, duration_s=2.0, seed=42)
        # fast polling for the test: exercise the pending→success transition
        orig_wait = engine.wait
        engine.wait = lambda pid, timeout=1800, poll=3.0: orig_wait(pid, timeout=30, poll=0.05)
        res = backend.generate(req, engine=engine)
    finally:
        fake.close()

    assert res.ok, res.error
    assert res.video_path and Path(res.video_path).stat().st_size == len(clip)
    assert res.receipt["prompt_id"] == "fake-1"
    # the real workflow JSON reached the server with our prompt + seed injected
    wf = fake.submitted[0]["prompt"]
    assert wf["h3_i2v"]["inputs"]["prompt"] == "a blue test pattern, static camera"
    assert wf["noise"]["inputs"]["noise_seed"] == 42
    assert wf["save_video"]["inputs"]["filename_prefix"] == "ov_t2v"
    assert fake.history_calls >= 3  # polled through the pending phase


def test_workflow_rejection_is_loud(tmp_path):
    """A server-side node_errors reply must raise from ComfyUIAdapter.submit."""

    class RejectingHandler(CannedJSONHandler):
        def do_POST(self):
            self.read_json()
            self.reply({"prompt_id": "x", "node_errors": {"h3_i2v": "missing input"}})

    url, close = serve(RejectingHandler)
    try:
        engine = ComfyUIAdapter(server=url, output_dir=str(tmp_path / "out"))
        with pytest.raises(RuntimeError, match="workflow rejected"):
            engine.submit({"any": "workflow"})
    finally:
        close()


def test_stitcher_concat_real_ffmpeg(tmp_path):
    a = tmp_path / "a.mp4"
    b = tmp_path / "b.mp4"
    _tiny_mp4(a, 0.5)
    _tiny_mp4(b, 0.5)
    out = Stitcher(output_dir=str(tmp_path)).concat([str(a), str(b)], str(tmp_path / "film.mp4"))
    assert out and Path(out).exists()
    assert 0.8 <= _duration(out) <= 1.3  # two 0.5s clips stitched
