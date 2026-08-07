"""open-video — Ollama for MiniMax H3 + agent skill harness (v0.0.1).

v0.0.1 scope: local install/pull/run for H3, plus ``skill/h3-video`` so any
agent host can generate high-quality video. Longer director pipelines exist
in-tree but are not the release thesis.

Thin facade over top-level ``core`` / ``backends`` / ``engines`` packages.

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

__version__ = "0.0.1"

# --- re-export the key classes (the public surface the task pins) -----------
# These imports are side-effect-free (all stdlib at import time); safe to eager-load.
from core.planner import Planner
from core.pipeline import LongFilmPipeline
from backends.h3.backend import H3Backend
from engines.comfyui.adapter import ComfyUIAdapter

__all__ = [
    "Planner",
    "LongFilmPipeline",
    "H3Backend",
    "ComfyUIAdapter",
    "__version__",
]
