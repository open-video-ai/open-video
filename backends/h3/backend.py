"""MiniMax H3 backend for open-video.

Ports the proven H3 generation (from early lab) behind the model-agnostic
ModelBackend interface. H3 = the #1 open video model (Arena T2V #2 / I2V #3 overall, #1 open,
at parity with closed). Baseline backend for open-video.
"""
from __future__ import annotations
import json, shutil, subprocess
from pathlib import Path
from core.backend import ModelBackend, Capabilities, ShotRequest, ShotResult

HERE = Path(__file__).parent
WORKFLOWS = {"t2v": HERE / "workflows" / "h3_t2v_api.json",
             "i2v": HERE / "workflows" / "h3_flf2v_api.json",
             "flf2v": HERE / "workflows" / "h3_flf2v_api.json"}
COMFY_INPUT = Path("ComfyUI/input")  # engine-relative; the adapter/engine host stages images here


def _snap_17k5(duration_s: float) -> int:
    """H3 num_frames snaps to 17k+5 @ 24fps (video-VAE temporal constraint)."""
    b = max(5, round(duration_s * 24))
    return b + (5 - (b % 17)) % 17


class H3Backend(ModelBackend):
    id = "minimax-h3"
    display_name = "MiniMax H3 (Hailuo 3.0)"
    capabilities = Capabilities(
        t2v=True, i2v=True, flf2v=True, r2v=True, native_audio=True,
        max_duration_s=15.0, max_short_edge_px=768,
        aspects=("21:9", "16:9", "4:3", "1:1", "3:4", "9:16"),
        strengths=("native-stereo-audio", "prompt-adherence", "arena-top-open"),
    )

    # --- prompt grammar (the official 3-field guide; condensed) ---
    def prompt_guide(self) -> str:
        if (HERE / "PROMPT_GRAMMAR.md").exists():
            return (HERE / "PROMPT_GRAMMAR.md").read_text()
        return ("H3 3-field: integrated_multimodal_description (style-first [Shot 1], bracketed shots w/ "
                "increasing cut times, camera type+amplitude+speed prose, <d>[lang] verbatim</d> dialogue "
                "w/ (S1)/(S2) IDs) + overall_soundscape (1-4 sent) + non_diegetic_music (1-3 sent, "
                "instrumentation/tempo only). Optional instruction line for I2V/FL2VA/L2VA.")

    def craft_prompt(self, intent: dict, mode: str) -> str:
        """intent = {subject, action, camera, environment, soundscape, music, dialogue[], first_frame_ref?}.
        Basic template; the core's LLM crafter can override with a richer model-specific prompt."""
        instr = ""
        if mode == "i2v":
            instr = ("For the target video, at 0.00 seconds into the target video, <Picture 1> "
                     "(from [Shot 1]) is fully referenced.\n\n")
        elif mode == "flf2v":
            instr = ("How the reference pictures align with the target video — Picture 1 (from Shot 1) "
                     "aligns with the 0.00-second mark; Picture 2 aligns with the final timestamp.\n\n")
        cam = intent.get("camera", "The camera pushes in with small amplitude at slow speed")
        d = intent.get("dialogue") or []
        dlg = ""
        for i, line in enumerate(d):
            sp = line.get("speaker", f"S{i+1}")
            lang = line.get("lang", "English")
            dlg += f" {sp} says: <d>[{lang}] {line['text']}</d>"
        return (f"{instr}integrated_multimodal_description: [Shot 1] Live-action, cinematic, "
                f"a medium shot frames {intent.get('subject','the subject')}. {cam} as "
                f"{intent.get('action','the scene unfolds with natural motion')}.{dlg}\n\n"
                f"overall_soundscape: {intent.get('soundscape','ambient environmental sounds with subtle physical motion.')}\n\n"
                f"non_diegetic_music: {intent.get('music','a soft minimal ambient score at a slow tempo.')}")

    def constraints(self) -> dict:
        return {"duration_range_s": (4, 15), "frame_grid": "17k+5 @ 24fps",
                "max_refs": {"images": 9, "videos": 3, "audios": 3, "total": 12},
                "resolution_multiple": 32, "min_short_edge_px": 384,
                "audio": "32kHz stereo native", "guidance": "CFG-distilled (no neg prompt/guidance)"}

    def default_settings(self) -> dict:
        return {"steps": 20, "sampler": "res_multistep", "scheduler": "simple",
                "shift_video": 12.0, "shift_audio": 3.0,
                "diffusion_quant": "minimax_h3_fl2va_pruned_int8_convrot.safetensors",
                "text_encoder_quant": "qwen3vl_32b_minimax_h3_int8_convrot.safetensors",
                "video_vae": "minimax_h3_video_vae_fp16.safetensors",
                "audio_vae": "minimax_h3_audio_vae_fp32.safetensors",
                "engine_flags": "--lowvram --use-sage-attention",
                "known_issues": {"NVFP4": "avoid on 5090 (ComfyUI #14157)"}}

    def duration_to_length(self, duration_s: float) -> int:
        return _snap_17k5(duration_s)

    def resolution_for(self, aspect: str, megapixels: float = 1.0) -> tuple:
        # native canvas = 768 short edge, capped 768x1344, multiple of 32
        from math import sqrt
        ax = {"21:9": (21, 9), "16:9": (16, 9), "4:3": (4, 3), "1:1": (1, 1),
              "3:4": (3, 4), "9:16": (9, 16)}.get(aspect, (16, 9))
        short = 768
        aw, ah = ax
        if aw >= ah:
            w = int(round(short * aw / ah / 32) * 32); h = short
        else:
            h = int(round(short * ah / aw / 32) * 32); w = short
        return (w, h)

    def generate(self, req: ShotRequest, engine=None) -> ShotResult:
        """Build the ComfyUI workflow for this shot, stage any images, run via the engine adapter."""
        wf_path = WORKFLOWS.get(req.mode)
        if not wf_path:
            return ShotResult(ok=False, error=f"H3 mode '{req.mode}' unsupported")
        wf = json.loads(wf_path.read_text())
        s = self.default_settings()
        wf["h3_i2v"]["inputs"].update({"prompt": req.prompt, "width": req.width,
                                       "height": req.height, "length": _snap_17k5(req.duration_s)})
        wf["noise"]["inputs"]["noise_seed"] = req.seed
        wf["sigmashift"]["inputs"].update({"shift_video": s["shift_video"], "shift_audio": s["shift_audio"]})
        wf["scheduler"]["inputs"]["steps"] = s["steps"]
        # LoRA support (community fine-tuned style/domain enhancers — the SD-flywheel for video)
        if req.lora:
            wf["lora_loader"] = {"class_type": "LoraLoader", "inputs": {
                "model": ["load_unet", 0], "clip": ["load_clip", 0], "lora_name": req.lora,
                "strength_model": req.lora_weight, "strength_clip": 0.0}}
            wf["sigmashift"]["inputs"]["model"] = ["lora_loader", 0]  # rewire model through LoRA
        if req.trigger_word:
            wf["h3_i2v"]["inputs"]["prompt"] = f"{req.trigger_word}, {req.prompt}"
        # stage reference frames for I2V/FL2VA
        if req.mode in ("i2v", "flf2v"):
            COMFY_INPUT.mkdir(parents=True, exist_ok=True)
            if req.first_frame:
                shutil.copy(req.first_frame, COMFY_INPUT / "firstframe.png")
            if req.mode == "flf2v" and req.last_frame:
                shutil.copy(req.last_frame, COMFY_INPUT / "lastframe.png")
            else:  # i2v: drop the last-frame branch
                wf["h3_i2v"]["inputs"].pop("last_frame", None); wf.pop("load_lastframe", None)
        wf["save_video"]["inputs"]["filename_prefix"] = f"ov_{req.mode}"
        # run
        if engine is None:
            from engines.comfyui.adapter import ComfyUIAdapter
            engine = ComfyUIAdapter()
        try:
            res = engine.submit_and_wait(wf, timeout=1800, save_node="save_video")
        except Exception as e:
            return ShotResult(ok=False, error=f"engine: {e}")
        if res["status"].get("status_str") != "success":
            return ShotResult(ok=False, error=res["status"].get("status_str", "failed"),
                              receipt={"prompt_id": res["prompt_id"], "status": res["status"]})
        return ShotResult(ok=True, video_path=(res["outputs"][0] if res["outputs"] else None),
                          receipt={"prompt_id": res["prompt_id"], "engine": engine.id,
                                   "outputs": res["outputs"]})
