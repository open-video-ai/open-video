#!/usr/bin/env python3
"""Full H3 benchmark on RTX 5090: multiple res/duration configs, warm runs.
Incremental + resumable (writes bench_full.json after each config so a kill
doesn't lose data). Captures wall, server 'Prompt executed', per-step, peak VRAM, RAM."""
import json, time, urllib.request, urllib.error, threading, subprocess, os, re
from pathlib import Path

SERVER="http://127.0.0.1:8188"
ROOT = Path(__file__).resolve().parent.parent
WF=ROOT/"workflows/h3_t2v_api.json"
RECEIPT=ROOT/"artifacts/verify/bench_full.json"
SLOG=ROOT/"logs/comfy_server.log"
PROMPT="A cinematic shot of waves crashing on a rocky shore at sunset, slow motion, detailed, natural light."
R={"prompt":("h3_i2v","prompt"),"seed":("noise","noise_seed"),"width":("h3_i2v","width"),"height":("h3_i2v","height"),"length":("h3_i2v","length")}

def dur2len(d):
    b=max(5,round(d*24)); return b+(5-(b%17))%17

class VRAM:
    def __init__(s,iv=1.5): s.iv=iv; s.peak=0; s._stop=False
    def start(s): threading.Thread(target=s._r,daemon=True).start(); s.t=time.time()
    def _r(s):
        while not s._stop:
            try:
                o=subprocess.check_output(["nvidia-smi","--query-gpu=memory.used","--format=csv,noheader,nounits"],text=True,timeout=5).strip()
                s.peak=max(s.peak,int(o.splitlines()[0]))
            except: pass
            time.sleep(s.iv)

def ram():
    mi={l.split(":")[0]:int(l.split()[1]) for l in open("/proc/meminfo")}
    return round((mi["MemTotal"]-mi["MemAvailable"])/1024)

def httpj(u,d=None,t=30):
    r=urllib.request.Request(u,headers={"Content-Type":"application/json"})
    if d is not None: r.data=json.dumps(d).encode()
    with urllib.request.urlopen(r,timeout=t) as x: return json.loads(x.read())
def queue(w): return httpj(f"{SERVER}/prompt",{"prompt":w,"client_id":"bench"})
def hist(pid):
    try: return httpj(f"{SERVER}/history/{pid}",t=10)
    except urllib.error.HTTPError: return {}

def last_match(pat):
    try:
        for l in reversed(open(SLOG,errors="ignore").read().splitlines()):
            m=re.search(pat,l)
            if m: return float(m.group(1))
    except: pass
    return None

def run(name,w,h,dur,seed,res):
    g=json.loads(WF.read_text())
    g[R["prompt"][0]]["inputs"][R["prompt"][1]]=PROMPT
    g[R["seed"][0]]["inputs"][R["seed"][1]]=seed
    g[R["width"][0]]["inputs"][R["width"][1]]=w
    g[R["height"][0]]["inputs"][R["height"][1]]=h
    g[R["length"][0]]["inputs"][R["length"][1]]=dur2len(dur)
    v=VRAM(); v.start(); t0=time.time()
    try:
        r=queue(g); pid=r.get("prompt_id")
    except Exception as e:
        res[name]={"error":f"queue {e}"}; RECEIPT.write_text(json.dumps(res,indent=2)); return
    ne=r.get("node_errors") or r.get("error")
    if ne:
        res[name]={"rejected":str(ne)[:300]}; RECEIPT.write_text(json.dumps(res,indent=2)); return
    st=None
    while time.time()-t0<1500:
        h=hist(pid)
        if pid in h: st=h[pid].get("status",{}); break
        time.sleep(2)
    v._stop=True
    out=res.get(name,{})
    out.update({"wall_s":round(time.time()-t0,1),"prompt_executed_s":last_match(r"Prompt executed in ([0-9.]+) seconds"),"per_step_s":last_match(r"\d+/20 \[[0-9:]+<[0-9:]+,\s+([0-9.]+)s/it"),"peak_vram_mb":v.peak,"ram_used_mb":ram(),"status":st if st else "timeout","length_frames":dur2len(dur)})
    res[name]=out; RECEIPT.write_text(json.dumps(res,indent=2))
    print(json.dumps({name:out}),flush=True)

if __name__=="__main__":
    cfgs=[("960x544_5s_warm",960,544,5,101),("1344x768_5s",1344,768,5,102),("960x544_10s",960,544,10,103),("1344x768_10s",1344,768,10,104)]
    res=json.loads(RECEIPT.read_text()) if RECEIPT.exists() else {}
    for name,w,h,dur,seed in cfgs:
        e=res.get(name)
        if e and "error" not in e and e.get("status") not in (None,"timeout") and e.get("wall_s",0)>10:
            print("skip",name,flush=True); continue
        run(name,w,h,dur,seed,res)
    print("BENCH_DONE",flush=True)
