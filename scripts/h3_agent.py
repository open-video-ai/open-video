#!/usr/bin/env python3
"""Agentic MiniMax H3 video generator — request -> best-quality video.

Pipeline:
  1. Choose MODE from inputs: no image -> T2V; 1 image -> I2V; 2 images -> FL2VA.
  2. PROMPT: use --prompt (preferred, e.g. agent/LLM-crafted per docs/PROMPT_GUIDE.md),
     or expand a simple --request into the official 3-field structure (basic template).
  3. Load the matching workflow (h3_t2v_api.json / h3_flf2v_api.json), inject best
     settings (default 1344x768, 20 steps), stage images for FL2VA.
  4. Generate via ComfyUI /prompt, poll, fetch mp4, sample peak VRAM, write receipt.
  5. Optionally extract frames for cross-model visual review.

Best quality defaults per docs/BEST_PRACTICES.md. For the highest quality, the prompt
should be crafted to the official 3-field guide (integrated_multimodal_description +
overall_soundscape + non_diegetic_music) — pass it via --prompt.
"""
import argparse, json, time, urllib.request, urllib.error, shutil, sys, os
from pathlib import Path

# Product root = this open-video checkout; lab runtime = sibling lab/ (ComfyUI + weights)
PRODUCT = Path(__file__).resolve().parent.parent
LAB = Path(os.environ.get("OPEN_VIDEO_LAB", PRODUCT.parent / "lab")).resolve()
ROOT = PRODUCT  # receipts/output under product
WORKFLOWS = PRODUCT / "backends" / "h3" / "workflows"
COMFY_DIR = Path(os.environ.get("OPEN_VIDEO_COMFYUI_DIR", LAB / "ComfyUI"))
SERVER = os.environ.get("OPEN_VIDEO_COMFYUI", "http://127.0.0.1:8188")
OUT = Path(os.environ.get("OPEN_VIDEO_OUTPUT", PRODUCT / "output"))
REC = Path(os.environ.get("OPEN_VIDEO_RECEIPTS", PRODUCT / "artifacts" / "verify"))
# dirs are created lazily at write time — importing this module must not
# touch the filesystem (it ships inside the wheel as open_video.scripts.*)
sys.path.insert(0, str(PRODUCT / "scripts"))
from h3_generate_benchmark import (VRAMSampler, ram_used_mb, http_json,
    queue_prompt, get_history, fetch_output, duration_to_length)

def expand_prompt(request, mode):
    """Basic 3-field template expander for a simple request. (Best quality: pass --prompt.)"""
    if mode == "t2v":
        instr = ""
    elif mode == "i2v":
        instr = ("For the target video, at 0.00 seconds into the target video, "
                 "<Picture 1> (from [Shot 1]) is fully referenced.\n\n")
    else:  # flf2v
        instr = ("How the reference pictures align with the target video — Picture 1 (from Shot 1) "
                 "aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) "
                 "aligns with the final timestamp of the target video.\n\n")
    return (f"{instr}integrated_multimodal_description: [Shot 1] Live-action, cinematic, "
            f"a medium shot frames {request}. The camera pushes in with small amplitude at slow "
            f"speed as the scene unfolds with natural, continuous motion and consistent lighting.\n\n"
            f"overall_soundscape: Ambient environmental sounds fitting the scene, with subtle "
            f"physical motion sounds and gentle texture throughout.\n\n"
            f"non_diegetic_music: A soft, minimal ambient score at a slow tempo that supports the "
            f"mood without dominating.")

def load_workflow(mode, prompt, w, h, dur, seed, ff, lf):
    if mode == "t2v":
        wf = json.loads((WORKFLOWS/"h3_t2v_api.json").read_text())
    else:
        wf = json.loads((WORKFLOWS/"h3_flf2v_api.json").read_text())
        (COMFY_DIR/"input").mkdir(parents=True, exist_ok=True)
        if ff: shutil.copy(ff, COMFY_DIR/"input/firstframe.png")
        if mode == "flf2v" and lf: shutil.copy(lf, COMFY_DIR/"input/lastframe.png")
        if mode == "i2v":  # single image -> drop last_frame branch
            wf["h3_i2v"]["inputs"].pop("last_frame", None); wf.pop("load_lastframe", None)
        wf["save_video"]["inputs"]["filename_prefix"] = f"h3_{mode}"
    wf["h3_i2v"]["inputs"].update({"prompt": prompt, "width": w, "height": h, "length": duration_to_length(dur)})
    wf["noise"]["inputs"]["noise_seed"] = seed
    return wf

def run(a):
    mode = "t2v" if not a.first_frame else ("flf2v" if a.last_frame else "i2v")
    prompt = a.prompt if (a.prompt and a.prompt.strip()) else expand_prompt(a.request, mode)
    # pre-delivery validation gate (mode-aware hard-constraint check; Seedance woodfantasy pattern)
    from validate_prompt import validate as _validate
    n_img = (1 if a.first_frame else 0) + (1 if a.last_frame else 0)
    _vmode, _issues, _warns = _validate(prompt, mode, a.duration, n_img)
    if _issues:
        return {"error": "prompt_validation_failed", "mode": _vmode, "issues": _issues, "warnings": _warns}
    wf = load_workflow(mode, prompt, a.width, a.height, a.duration, a.seed, a.first_frame, a.last_frame)
    if a.dry_run:
        try:
            r = queue_prompt(wf); return {"dry_run": True, "mode": mode, "length_frames": duration_to_length(a.duration),
                                         "queued": bool(r.get("prompt_id")), "errors": r.get("node_errors") or r.get("error")}
        except urllib.error.HTTPError as e:
            return {"dry_run": True, "rejected": True, "body": e.read().decode()[:600]}
    sampler = VRAMSampler(1.5); sampler.start(); ram0 = ram_used_mb(); t0 = time.time()
    try:
        r = queue_prompt(wf); pid = r.get("prompt_id")
    except Exception as e:
        sampler.stop(); return {"error": f"queue failed: {e}", "mode": mode}
    ne = r.get("node_errors") or r.get("error")
    if ne:
        sampler.stop(); return {"error": "validation", "details": str(ne)[:500], "mode": mode}
    st = None
    while time.time() - t0 < a.timeout:
        h = get_history(pid)
        if pid in h: st = h[pid].get("status", {}); break
        time.sleep(3)
    t1 = time.time(); sampler.stop()
    out, msg = fetch_output(pid, "save_video")
    receipt = {"mode": mode, "params": {"prompt": prompt, "seed": a.seed, "width": a.width,
               "height": a.height, "duration_s": a.duration, "length_frames": duration_to_length(a.duration),
               "first_frame": a.first_frame, "last_frame": a.last_frame},
               "wall_s": round(t1-t0, 1), "peak_vram_mb": sampler.peak,
               "ram_used_mb": round(ram_used_mb()), "status": st, "outputs": out, "fetch_msg": msg}
    REC.mkdir(parents=True, exist_ok=True)
    rp = REC/f"agent_{mode}_{int(t0)}.json"; rp.write_text(json.dumps(receipt, indent=2, default=str))
    return receipt

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", default="", help="simple NL request (expanded to 3-field template)")
    ap.add_argument("--prompt", default="", help="full guide-compliant prompt (overrides --request; best quality)")
    ap.add_argument("--first-frame"); ap.add_argument("--last-frame")
    ap.add_argument("--width", type=int, default=1344); ap.add_argument("--height", type=int, default=768)
    ap.add_argument("--duration", type=float, default=5.0); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--timeout", type=int, default=1800); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    print(json.dumps(run(a), indent=2, default=str))
