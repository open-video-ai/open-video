#!/usr/bin/env python3
"""Multi-shot stitcher — chain H3 clips into videos longer than the 15 s ceiling.
This is the key "match/beat Seedance on length" mechanism (Seedance 2.5 does 30 s single-take;
H3 caps at 15 s locally). Approach: plan N<=15s shots; shot 1 generated (T2V or FL2VA from a
seed image); each subsequent shot is FL2VA with its first_frame = the PREVIOUS shot's last frame
(extracted via ffmpeg), giving continuous handoff. Then ffmpeg-concat all shot mp4s into one.

Usage:
  scripts/h3_multishot.py --plan plans/multishot_demo.json --out output/long_demo.mp4
Plan JSON: { "shots":[ {"prompt_file":"prompts/shot1.txt","duration":10,"first_frame":null},
                        {"prompt_file":"prompts/shot2.txt","duration":8}, ... ] }
"""
import argparse, json, subprocess, time, urllib.request, urllib.error, sys
from pathlib import Path
import os
PRODUCT = Path(__file__).resolve().parent.parent
LAB = Path(os.environ.get("OPEN_VIDEO_LAB", PRODUCT.parent / "lab")).resolve()
ROOT = PRODUCT
WORKFLOWS = PRODUCT / "backends" / "h3" / "workflows"
SERVER = "http://127.0.0.1:8188"
sys.path.insert(0, str(ROOT/"scripts"))
from h3_generate_benchmark import queue_prompt, get_history, fetch_output, duration_to_length

def extract_last_frame(mp4, out_png):
    subprocess.run(["ffmpeg","-y","-v","error","-sseof","-0.1","-i",mp4,"-frames:v","1",out_png], check=False)
    return out_png.exists()

def gen_shot(prompt, duration, seed, first_frame, shot_name):
    """Generate one shot via FL2VA workflow (first_frame optional). Returns mp4 path or None."""
    import shutil
    wf = json.loads((ROOT/"workflows/h3_flf2v_api.json").read_text())
    wf["h3_i2v"]["inputs"].update({"prompt": prompt, "width": 1344, "height": 768,
                                   "length": duration_to_length(duration)})
    wf["noise"]["inputs"]["noise_seed"] = seed
    (ROOT/"ComfyUI/input").mkdir(parents=True, exist_ok=True)
    if first_frame:
        shutil.copy(first_frame, ROOT/"ComfyUI/input/firstframe.png")
        wf["save_video"]["inputs"]["filename_prefix"] = shot_name
    else:  # pure T2V for shot 1: drop both frame branches
        wf["h3_i2v"]["inputs"].pop("first_frame", None); wf["h3_i2v"]["inputs"].pop("last_frame", None)
        wf.pop("load_firstframe", None); wf.pop("load_lastframe", None)
        wf["save_video"]["inputs"]["filename_prefix"] = shot_name
    r = queue_prompt(wf); pid = r.get("prompt_id")
    if r.get("node_errors") or r.get("error"): return None, str(r.get("node_errors") or r.get("error"))
    t0 = time.time()
    while time.time()-t0 < 1800:
        h = get_history(pid)
        if pid in h: break
        time.sleep(3)
    else: return None, "timeout"
    out, msg = fetch_output(pid, "save_video")
    return (out[0] if out else None), msg

def concat(mp4s, out_mp4):
    lst = ROOT/"logs/_concat.txt"
    lst.write_text("\n".join(f"file '{m}'" for m in mp4s))
    r = subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",str(lst),
                        "-c","copy",out_mp4], capture_output=True, text=True)
    return r.returncode == 0, r.stderr[-400:]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", default=str(ROOT/"output/multishot.mp4"))
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    plan = json.loads((ROOT/a.plan).read_text()) if not str(a.plan).startswith("{") else json.loads(a.plan)
    shots = plan["shots"]
    print(f"multi-shot: {len(shots)} shots -> {a.out}", flush=True)
    mp4s, prev_last = [], None
    for i, s in enumerate(shots):
        prompt = Path(s["prompt_file"]).read_text() if s.get("prompt_file") else s.get("prompt","")
        ff = s.get("first_frame") or prev_last
        out, msg = gen_shot(prompt, s.get("duration",8), a.seed+i, ff, f"ms_shot{i}")
        if not out: print(f"shot {i} FAILED: {msg}", flush=True); break
        print(f"shot {i} -> {out}", flush=True)
        mp4s.append(out)
        prev_last_png = ROOT/f"logs/ms_lastframe_{i}.png"
        if extract_last_frame(out, prev_last_png): prev_last = str(prev_last_png)
    if len(mp4s) > 1:
        ok, err = concat(mp4s, a.out)
        print(f"concat {'OK' if ok else 'FAIL'}: {a.out}" + ("" if ok else f" :: {err}"), flush=True)
    elif mp4s:
        print(f"single shot only -> {mp4s[0]}", flush=True)
