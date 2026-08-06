"""open-video model backend contract.

A backend is a plugin that adapts ONE open video model (H3, Wan3, FLUX3-Dev, ...) to open-video's
model-agnostic core. The core (planner/crafter/validator/judge/stitcher) never touches a model
directly — it goes through this interface. Adding a model = implement this contract; core unchanged.

Inspired by what we learned shipping H3 (see sibling repo 55-ai-video): each model has its own
prompt grammar, modes, workflow, constraints, and optimal settings.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Capabilities:
    """What a model can do. The planner/selector/routing use this."""
    t2v: bool = True
    i2v: bool = False          # first-frame image-to-video
    flf2v: bool = False        # first + last frame
    r2v: bool = False          # multi-reference (identity/style/voice)
    native_audio: bool = False
    max_duration_s: float = 15.0
    max_short_edge_px: int = 768
    aspects: tuple = ("16:9", "9:16", "1:1", "4:3", "3:4", "21:9")
    strengths: tuple = ()      # free-text tags the selector uses, e.g. ("audio","prompt-adherence")


@dataclass
class ShotRequest:
    """One shot the core asks the backend to generate."""
    prompt: str
    mode: str                   # t2v | i2v | flf2v | r2v
    width: int
    height: int
    duration_s: float
    seed: int
    first_frame: Optional[str] = None   # path (i2v/flf2v)
    last_frame: Optional[str] = None    # path (flf2v)
    references: tuple = ()              # (kind, path) for r2v
    lora: Optional[str] = None          # community LoRA filename (e.g. "cinematic-v2.safetensors")
    lora_weight: float = 0.8            # LoRA strength (0.0-1.0)
    trigger_word: Optional[str] = None  # optional trigger word prepended to prompt for LoRA
    extra: dict = field(default_factory=dict)


@dataclass
class ShotResult:
    ok: bool
    video_path: Optional[str] = None
    receipt: dict = field(default_factory=dict)   # timings, vram, engine ids
    error: Optional[str] = None
    frames_dir: Optional[str] = None              # extracted frames for the judge


class ModelBackend:
    """Contract every model plugin implements. Core ↔ model seam."""

    id: str = "base"
    display_name: str = "base"
    capabilities: Capabilities = Capabilities()

    # --- 1. prompt grammar: how to write a good prompt for THIS model ---
    def prompt_guide(self) -> str:
        """Markdown describing this model's prompt structure (the crafter reads it)."""
        raise NotImplementedError

    def craft_prompt(self, intent: dict, mode: str) -> str:
        """Turn a structured intent (subject/action/camera/audio/music/dialogue) into a
        model-specific prompt. Default: a generic template; override per model."""
        raise NotImplementedError

    # --- 2. validation: hard constraints for this model (fed to the validator) ---
    def constraints(self) -> dict:
        """e.g. {'duration_range_s': (4,15), 'frame_grid': '17k+5', 'max_refs': {'images':9,'videos':3,'audios':3,'total':12}, 'resolution_multiple': 32}"""
        return {}

    # --- 3. generation: produce one shot via the engine adapter ---
    def generate(self, req: ShotRequest) -> ShotResult:
        """Run one shot through the engine (ComfyUI/etc.). Backend owns model-specific
        workflow/quantization/offload; returns the video + frames for the judge."""
        raise NotImplementedError

    # --- 4. settings profile: evidence-based optimal settings (from bench/) ---
    def default_settings(self) -> dict:
        """e.g. {'steps':20,'sampler':'res_multistep','scheduler':'simple','shift_video':12.0,'shift_audio':3.0,'quant':'int8_convrot'}"""
        return {}

    # --- 5. model-specific extras (e.g. the 17k+5 frame snap, aspect→pixels) ---
    def duration_to_length(self, duration_s: float) -> int:
        """Map seconds → model frame count (e.g. H3's 17k+5 grid @ 24fps)."""
        raise NotImplementedError

    def resolution_for(self, aspect: str, megapixels: float = 1.0) -> tuple:
        """Map aspect + megapixels → (width, height) on this model's grid."""
        raise NotImplementedError


# --- engine adapter seam (open-video drives the engine, doesn't replace it) ---
class EngineAdapter:
    """open-video talks to a generation engine (ComfyUI first) via this. The backend uses it."""
    id: str = "base"

    def submit_and_wait(self, workflow: dict, timeout: int) -> dict:
        """POST a workflow to the engine, poll, return outputs + timings."""
        raise NotImplementedError
