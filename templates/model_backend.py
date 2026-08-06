"""Template: Model backend plugin for open-video.

Copy this file to backends/<your_model>/backend.py, implement the methods, add your workflows
to backends/<your_model>/workflows/, and PR. The core never changes — your model plugs in.

See backends/h3/backend.py for a complete working example.
"""
from __future__ import annotations
from core.backend import ModelBackend, Capabilities, ShotRequest, ShotResult


class YourModelBackend(ModelBackend):
    # --- identity ---
    id = "your-model"
    display_name = "Your Model Name"
    capabilities = Capabilities(
        t2v=True, i2v=False, flf2v=False, r2v=False,
        native_audio=False,           # does it generate audio natively?
        max_duration_s=10.0,
        max_short_edge_px=720,
        strengths=("your-model-strength-tag",),  # selector uses these
    )

    # --- 1. prompt grammar: how to prompt THIS model ---
    def prompt_guide(self) -> str:
        return "Describe how to write prompts for your model (the crafter reads this)."

    def craft_prompt(self, intent: dict, mode: str) -> str:
        # Turn structured intent → model-specific prompt string
        return f"Your model's prompt format for: {intent}"

    # --- 2. hard constraints (fed to the validator) ---
    def constraints(self) -> dict:
        return {
            "duration_range_s": (2, 10),
            "frame_grid": None,          # or e.g. "17k+5 @ 24fps" if model has a grid
            "max_refs": {"images": 0, "videos": 0, "audios": 0, "total": 0},
            "resolution_multiple": 16,   # or 32, 64...
        }

    # --- 3. generation: produce one shot via the engine ---
    def generate(self, req: ShotRequest, engine=None) -> ShotResult:
        # Build the engine-specific workflow (e.g. ComfyUI JSON) for this shot
        workflow = self._build_workflow(req)
        # Run via the engine adapter
        if engine is None:
            from engines.comfyui.adapter import ComfyUIAdapter
            engine = ComfyUIAdapter()
        res = engine.submit_and_wait(workflow, timeout=1800)
        if res["status"].get("status_str") != "success":
            return ShotResult(ok=False, error=res["status"].get("status_str"))
        return ShotResult(ok=True, video_path=res["outputs"][0] if res["outputs"] else None,
                          receipt={"engine": engine.id})

    def _build_workflow(self, req: ShotRequest) -> dict:
        # TODO: load your model's ComfyUI workflow JSON from workflows/ + inject req params
        # Example: see backends/h3/backend.py generate()
        raise NotImplementedError("Build your workflow here")

    # --- 4. optimal settings (from bench/) ---
    def default_settings(self) -> dict:
        return {"steps": 20, "sampler": "euler", "scheduler": "normal"}

    # --- 5. model-specific helpers ---
    def duration_to_length(self, duration_s: float) -> int:
        return int(duration_s * 24)  # adjust for your model's fps/grid

    def resolution_for(self, aspect: str, megapixels: float = 1.0) -> tuple:
        return (1280, 720)  # adjust for your model's resolution grid
