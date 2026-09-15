"""Regression tests for issue #17 — _bind_engine double-passed `engine`.

cli/open_video.py wraps backend.generate to inject the CLI-configured engine,
while core/pipeline.py calls backend.generate(req, engine=self.engine). The old
wrapper forwarded the caller's kwargs AND injected engine=..., so every
pipeline-style call died with
    TypeError: generate() got multiple values for keyword argument 'engine'

Chosen semantic: the bound engine is authoritative — a caller-supplied
`engine` kwarg is overridden. _bind_engine exists so the engine built from
--server is the one every generate() call uses; honoring a caller-supplied
engine instead would let that flag be silently ignored again.
"""
from open_video.backends.h3.backend import H3Backend
from open_video.cli.open_video import _bind_engine
from open_video.core.backend import ShotRequest


class _RecordingEngine:
    """Engine double: logs which engine object ran each submission."""

    def __init__(self, log, name):
        self.id = name
        self._log = log

    def submit_and_wait(self, wf, timeout=1800, save_node=None):
        self._log.append(self)
        return {"status": {"status_str": "success"}, "prompt_id": "spy-1",
                "outputs": ["/tmp/ov_spy.mp4"]}


def _req():
    return ShotRequest(prompt="a test pattern", mode="t2v", width=64,
                       height=36, duration_s=2.0, seed=1)


def test_bind_engine_pipeline_style_call():
    """backend.generate(req, engine=...) through the patch must not raise
    TypeError (issue #17); the bound engine wins over the caller's."""
    log = []
    bound = _RecordingEngine(log, "bound")
    caller = _RecordingEngine(log, "caller")
    backend = H3Backend()
    _bind_engine(backend, bound)
    # this is exactly what core/pipeline.py:90 does
    res = backend.generate(_req(), engine=caller)
    assert res.ok, res.error
    assert len(log) == 1 and log[0] is bound
    assert res.receipt["engine"] == bound.id


def test_bind_engine_fills_default():
    """A bare generate(req) still gets the bound engine injected."""
    log = []
    bound = _RecordingEngine(log, "bound")
    backend = H3Backend()
    _bind_engine(backend, bound)
    res = backend.generate(_req())
    assert res.ok, res.error
    assert len(log) == 1 and log[0] is bound
