"""open-video — Ollama for MiniMax H3 + agent skill harness (v0.0.1).

v0.0.1 scope: local install/pull/run for H3, plus ``skill/h3-video`` so any
agent host can generate high-quality video. Longer director pipelines exist
in-tree but are not the release thesis.

Facade over the ``open_video.core`` / ``open_video.backends`` /
``open_video.engines`` subpackages (which live as sibling top-level dirs in the
source tree — see the ``__path__`` block below — and inside ``open_video/`` in
an installed wheel).

Public API:
    H3Backend        -- MiniMax H3 model plugin
    ComfyUIAdapter   -- ComfyUI HTTP engine adapter
    Planner          -- concept -> shot plan
    LongFilmPipeline -- multi-shot orchestrator (evolving)

CLI::

    open-video pull h3
    open-video run "waves at sunset" --duration 5
    open-video status
"""
from __future__ import annotations

# --- source-tree subpackage resolution ---------------------------------------
# In the repo, core/, backends/, engines/, judges/, cli/ live beside this
# package so documented paths (`python cli/open_video.py`, backends/h3/...)
# keep working. Extending __path__ with the repo root lets `open_video.core`
# etc. resolve in source checkouts; in an installed wheel these subpackages are
# physically inside open_video/ ([tool.setuptools.package-dir]) and the
# pyproject.toml probe below fails, making this a no-op.
import os as _os

_repo = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _os.path.isfile(_os.path.join(_repo, "pyproject.toml")) and _os.path.isdir(
    _os.path.join(_repo, "core")
):
    __path__.append(_repo)
del _os, _repo

__version__ = "0.0.1"

# --- re-export the key classes (the public surface the task pins) -----------
# These imports are side-effect-free (all stdlib at import time); safe to eager-load.
from open_video.core.planner import Planner
from open_video.core.pipeline import LongFilmPipeline
from open_video.backends.h3.backend import H3Backend
from open_video.engines.comfyui.adapter import ComfyUIAdapter

__all__ = [
    "Planner",
    "LongFilmPipeline",
    "H3Backend",
    "ComfyUIAdapter",
    "__version__",
]
