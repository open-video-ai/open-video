"""open-video — open-source autonomous video generation.

The agent director layer on ComfyUI + open models (MiniMax H3 baseline).
"Ollama for video": one-command local run + cheap SaaS + community LoRAs +
a judge->refine->best-of-N quality loop.

This package is a thin facade over the top-level ``core`` / ``backends`` /
``engines`` packages (kept flat so the existing ``from core.backend import ...``
imports work both from source and when pip-installed). It exposes the
high-level objects users and integrators import.

Public API:
    Planner          -- concept -> coherence bible + shot plan        (core.planner)
    LongFilmPipeline -- plan -> per-shot generate+judge -> FL2VA chain (core.pipeline)
                        -> stitch -> film  (the flagship 5-min-film orchestrator)
    H3Backend        -- MiniMax H3 model plugin                       (backends.h3.backend)
    ComfyUIAdapter   -- ComfyUI HTTP engine adapter                   (engines.comfyui.adapter)

Run the CLI via ``python -m open_video`` or the installed ``open-video`` script:

    open-video "A cinematic shot of waves at sunset" --duration 10 --model h3
    open-video gen "..."            # `gen` is accepted as an alias of the default action
    open-video list-models
"""
from __future__ import annotations

__version__ = "0.1.0"

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
