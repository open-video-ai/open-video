#!/usr/bin/env python3
"""
MiniMax H3 headless generation + benchmark via ComfyUI HTTP API (RTX 5090).

Loads workflows/h3_t2v_api.json, injects prompt/seed/size/length, POSTs to
ComfyUI /prompt, polls /history, downloads the output, times it, samples peak
VRAM, and writes a benchmark receipt JSON.

Prereqs:
  * ComfyUI server:  cd ComfyUI && ../venv/bin/python main.py --listen 127.0.0.1 --port 8188 --lowvram
  * H3 weights present in h3_models/ (mapped via ComfyUI/extra_model_paths.yaml)
  * workflows/h3_t2v_api.json (built + graph-validated against /object_info)
"""
import argparse, json, time, urllib.request, urllib.error, threading, subprocess
from pathlib import Path

import os
PRODUCT = Path(__file__).resolve().parent.parent
LAB = Path(os.environ.get("OPEN_VIDEO_LAB", PRODUCT.parent / "lab")).resolve()
ROOT = PRODUCT
SERVER = os.environ.get("OPEN_VIDEO_COMFYUI", "http://127.0.0.1:8188")
WORKFLOWS = PRODUCT / "backends" / "h3" / "workflows"
OUT_DIR = ROOT / "output"
RECEIPT_DIR = ROOT / "artifacts/verify"
OUT_DIR.mkdir(parents=True, exist_ok=True)
RECEIPT_DIR.mkdir(parents=True, exist_ok=True)

# role -> (node_id, input_key) for workflows/h3_t2v_api.json
NODE_ROLES = {
    "prompt": ("h3_i2v", "prompt"),
    "seed":   ("noise",  "noise_seed"),
    "width":  ("h3_i2v", "width"),
    "height": ("h3_i2v", "height"),
    "length": ("h3_i2v", "length"),
    "save":   ("save_video", None),
}

def duration_to_length(duration_s: float) -> int:
    """H3 num_frames snapped to 17*n + 5 (video-VAE temporal constraint), ~24fps."""
    base = max(5, round(duration_s * 24))
    return base + (5 - (base % 17)) % 17

class VRAMSampler:
    def __init__(self, interval=2.0):
        self.interval, self.peak, self.samples, self._stop = interval, 0, [], False
    def start(self):
        self.t = threading.Thread(target=self._run, daemon=True); self.t.start()
    def _run(self):
        while not self._stop:
            try:
                out = subprocess.check_output(
                    ["nvidia-smi","--query-gpu=memory.used","--format=csv,noheader,nounits"],
                    text=True, timeout=5).strip()
                mb = int(out.splitlines()[0]); self.samples.append(mb); self.peak = max(self.peak, mb)
            except Exception: pass
            time.sleep(self.interval)
    def stop(self):
        self._stop = True; self.t.join(timeout=5)

def ram_used_mb():
    try:
        mi = {l.split(":")[0]: int(l.split()[1]) for l in open("/proc/meminfo")}
        return (mi["MemTotal"] - mi["MemAvailable"]) / 1024
    except Exception: return -1

def http_json(url, data=None, timeout=30):
    req = urllib.request.Request(url, headers={"Content-Type":"application/json"})
    if data is not None: req.data = json.dumps(data).encode()
    with urllib.request.urlopen(req, timeout=timeout) as r: return json.loads(r.read())

def queue_prompt(wf): return http_json(f"{SERVER}/prompt", {"prompt": wf, "client_id":"h3bench"}, timeout=30)
def get_history(pid):
    try: return http_json(f"{SERVER}/history/{pid}", timeout=10)
    except urllib.error.HTTPError: return {}

def fetch_output(pid, save_node):
    hist = get_history(pid)
    if not hist or pid not in hist: return None, "no history"
    outputs = hist[pid].get("outputs", {})
    node_out = outputs.get(str(save_node)) or next(iter(outputs.values()), {})
    files = []
    for g in node_out.get("gifs") or node_out.get("videos") or node_out.get("images") or []:
        fn, sub = g.get("filename"), g.get("subfolder","")
        if fn: files.append((fn, sub))
    if not files: return None, f"no output in {save_node}: {node_out}"
    saved = []
    for fn, sub in files:
        url = f"{SERVER}/view?filename={fn}&subfolder={sub}&type=output"
        p = OUT_DIR / f"{int(time.time())}_{fn}"
        urllib.request.urlretrieve(url, p); saved.append(str(p))
    return saved, "ok"

def run(args):
    wf = json.loads(Path(args.workflow).read_text())
    def setval(node_id, key, val):
        if node_id and key: wf[node_id]["inputs"][key] = val
    setval(*NODE_ROLES["prompt"], args.prompt)
    setval(*NODE_ROLES["seed"], args.seed)
    setval(*NODE_ROLES["width"], args.width)
    setval(*NODE_ROLES["height"], args.height)
    setval(*NODE_ROLES["length"], duration_to_length(args.duration))

    if args.dry_run:
        try:
            resp = queue_prompt(wf)
            return {"dry_run": True, "prompt_id": resp.get("prompt_id"),
                    "queued": bool(resp.get("prompt_id")), "node_count": len(wf),
                    "server_errors": resp.get("node_errors") or resp.get("error")}
        except urllib.error.HTTPError as e:
            return {"dry_run": True, "rejected": True, "http": e.code, "body": e.read().decode()[:800]}
        except Exception as e:
            return {"dry_run": True, "error": repr(e)}

    sampler = VRAMSampler(2.0); sampler.start(); ram0 = ram_used_mb(); t0 = time.time()
    try:
        resp = queue_prompt(wf)
    except Exception as e:
        sampler.stop(); return {"error": f"queue failed: {e}"}
    pid = resp.get("prompt_id")
    status = None
    while time.time() - t0 < args.timeout:
        h = get_history(pid)
        if pid in h: status = h[pid].get("status", {}); break
        time.sleep(3)
    t_done = time.time(); sampler.stop()
    out, msg = fetch_output(pid, NODE_ROLES["save"][0])
    receipt = {
        "model": "MiniMax H3 (Comfy-Org pruned_int8_convrot FL2VA + int8 text enc)",
        "gpu": "RTX 5090 32GB",
        "params": {"prompt": args.prompt, "seed": args.seed, "width": args.width,
                   "height": args.height, "duration_s": args.duration,
                   "length_frames": duration_to_length(args.duration)},
        "prompt_id": pid, "wall_seconds": round(t_done - t0, 1),
        "status": status, "peak_vram_mb": sampler.peak,
        "ram_start_mb": round(ram0, 0), "ram_end_mb": round(ram_used_mb(), 0),
        "outputs": out, "fetch_msg": msg,
    }
    rp = RECEIPT_DIR / f"bench_{int(t0)}_{args.width}x{args.height}_{args.duration}s.json"
    rp.write_text(json.dumps(receipt, indent=2))
    return receipt

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", default=str(WORKFLOWS / "h3_t2v_api.json"))
    ap.add_argument("--prompt", default="A cinematic shot of waves crashing on a rocky shore at sunset, slow motion, detailed, natural light.")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--width", type=int, default=960)
    ap.add_argument("--height", type=int, default=544)
    ap.add_argument("--duration", type=float, default=5.0)
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    print(json.dumps(run(a), indent=2, default=str))
