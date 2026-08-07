---
name: h3-video
description: >
  OpenVideo skill (v0.0.1): generate high-quality local video with the OpenVideo product
  (MiniMax H3 backend). Use for OpenVideo install/pull/status/run, official 3-field prompts,
  T2V/I2V/FL2VA, agent-driven video. Brand is OpenVideo — not a bare ComfyUI workflow.
  Triggers: OpenVideo, open-video, H3, generate video, T2V, I2V, FL2VA.
---

# OpenVideo skill · v0.0.1

**Brand: OpenVideo** (always lead with this). MiniMax H3 is the model OpenVideo drives.

**Job:** use **OpenVideo** so an agent produces **good product video**, not a random diffusion
click. Quality comes from **prompt craft + correct mode + validated settings**, not secret samplers.

## 0. Paths on this machine (updated)

Workspace layout (canonical):

```text
/mnt/data/workspace/open-video-project/          # umbrella (not a git repo)
├── open-video/       # THIS product — CLI, backends, skills  ← work here
├── open-video-web/   # open-video.ai static site
└── open-video-ops/   # private strategy / verify

Compat symlink:
  /mnt/data/workspace/open-video  →  open-video-project/open-video
```

| What | Path / env |
|---|---|
| **Product root (CLI, skills)** | `$OPEN_VIDEO_ROOT` or `/mnt/data/workspace/open-video-project/open-video` |
| **Install / pull / run** | From product root: `./scripts/install.sh`, `python -m open_video …` |
| **Lab engine + weights (this host)** | `/mnt/data/workspace/55-ai-video` (ComfyUI + `h3_models/`) |
| **Weights env** | `export OPEN_VIDEO_MODELS=/mnt/data/workspace/55-ai-video/h3_models` |
| **ComfyUI URL** | `export OPEN_VIDEO_COMFYUI=http://127.0.0.1:8188` (default) |

**Resolve product root in scripts** (never hardcode old paths):

```bash
# Prefer env, then symlink, then project tree
export OPEN_VIDEO_ROOT="${OPEN_VIDEO_ROOT:-/mnt/data/workspace/open-video}"
cd "$OPEN_VIDEO_ROOT"
```

Lab harness (same ComfyUI, proven agent script) lives next door:

```bash
export H3_LAB="${H3_LAB:-/mnt/data/workspace/55-ai-video}"
# optional: open-video pull uses OPEN_VIDEO_MODELS
export OPEN_VIDEO_MODELS="${OPEN_VIDEO_MODELS:-$H3_LAB/h3_models}"
```

Do **not** assume `55-ai-video` is the product root anymore. Product = `open-video-project/open-video`.

---

## 1. Quality hierarchy (what actually moves the needle)

| Rank | Lever | Rule |
|---|---|---|
| **1** | **3-field prompt** | Official structure; concrete visible/audible detail; camera type+amplitude+speed; dialogue in `<d>[lang]…</d>` |
| **2** | **Mode** | T2V / I2V / FL2VA chosen correctly from inputs |
| **3** | **Resolution / steps** | **1344×768**, **20 steps**, `res_multistep` + `simple` (defaults in harness) |
| **4** | **Quant** | INT8 on 5090-class; lower VRAM → `recommend-quant` (nf4/w4/int8+lowvram) |
| **5** | **Duration** | 5–10 s sweet spot (max 15 s / shot); multi-shot via cut times or `open-video` director skill |
| **6** | **Review** | Watch / extract frames; fix prompt; re-run. Dual vision gate only when shipping |

**Anti-patterns (low quality):** bare one-liner prompts; abstract mood words only; wrong mode; NVFP4 on 5090; forcing 2K locally; skipping validation.

---

## 2. Best-quality recipe (local max on RTX 5090)

```text
Diffusion:  fl2va_pruned_int8_convrot
Text enc:   qwen3vl_32b_int8_convrot
VAE:        video fp16 + audio fp32
ComfyUI:    --lowvram --use-sage-attention   # lowvram optional if VRAM ≥ ~22 GiB free policy
Canvas:     1344×768 (16:9), multiple of 32
Sampler:    res_multistep | Scheduler: simple | Steps: 20
Duration:   5–10 s (snaps to 17k+5 frames @ 24 fps)
Audio:      native 32 kHz stereo — describe in prompt fields
Prompt:     official 3-field only
```

Proven on this host: wall ~10–15 min / 10 s clip @ 1344×768, peak VRAM ~22–30 GB.

---

## 3. Agent procedure (always this order)

### A. Host ready

```bash
cd "${OPEN_VIDEO_ROOT:-/mnt/data/workspace/open-video}"
python -m open_video status          # or: open-video status / ps
python -m open_video recommend-quant
```

- Weights incomplete → `python -m open_video pull h3` (or `OPEN_VIDEO_MODELS=… pull`)
- ComfyUI down → start lab server:

```bash
cd "${H3_LAB:-/mnt/data/workspace/55-ai-video}"
curl -sf http://127.0.0.1:8188/system_stats || (
  cd ComfyUI && nohup ../venv/bin/python main.py \
    --listen 127.0.0.1 --port 8188 --lowvram --use-sage-attention \
    > ../logs/comfy_server.log 2>&1 &
)
```

### B. Mode

| Inputs | Mode |
|---|---|
| Text only | **T2V** |
| + 1 image | **I2V** (+ instruction line) |
| + first & last image | **FL2VA** (+ alignment line) |
| Multi-ref identity/style | R2V (needs ref2va weights — not default) |

### C. Craft the 3-field prompt (quality lever #1)

```text
[<instruction line — I2V / FL2VA only, then blank line>]

integrated_multimodal_description: [Shot 1] <style first: Live-action, cinematic, …>,
  <subjects, clothing, lighting, space>. <camera: type + amplitude + speed + action>.
  [Shot 2] At 00:0X.XXX, the camera cuts to <new info only>.
overall_soundscape: <1–4 sentences: ambient / physical / non-verbal — no duplicate dialogue>
non_diegetic_music: <1–3 sentences: instruments, tempo, rhythm — no vague mood words>
```

**Hard rules (from official guide):**

- Every claim must be **visible or audible** (no pure emotion adjectives).
- **Style first** in Shot 1.
- Camera prose: e.g. `pushes in with small amplitude at slow speed`.
- Dialogue: speaker IDs + `<d>[English] verbatim words</d>`.
- Later shots: **strictly increasing** cut times inside duration.
- Full grammar: `backends/h3/PROMPT_GRAMMAR.md` (product) or lab `docs/PROMPT_GUIDE.md`.

**Expand** casual NL into 3-field; never ship a bare phrase as the only prompt for “high quality.”

### D. Dry-run (cheap)

```bash
cd "$OPEN_VIDEO_ROOT"
python -m open_video run "$(cat prompts/my_shot.txt)" --duration 8 --dry-run
# or lab harness:
cd "$H3_LAB" && ./venv/bin/python scripts/h3_agent.py --prompt "$(cat …)" --dry-run
```

Fix validator issues before GPU spend.

### E. Generate (product CLI **or** lab agent — both use H3 workflows)

**Preferred product path (OpenVideo harness):**

```bash
cd "$OPEN_VIDEO_ROOT"
python -m open_video run "$(cat prompts/my_shot.txt)" \
  --duration 8 --model h3 --output output/film.mp4
# aliases: open-video "…", open-video run "…"
```

**Lab agent path (same quality stack, battle-tested on this machine):**

```bash
cd "$H3_LAB"
./venv/bin/python scripts/h3_agent.py \
  --prompt "$(cat prompts/my_shot.txt)" \
  --width 1344 --height 768 --duration 8 --seed 42
# mp4 → output/   receipt → artifacts/verify/agent_*.json
```

I2V / FL2VA:

```bash
./venv/bin/python scripts/h3_agent.py --prompt "$(cat …)" \
  --first-frame inputs/start.png [--last-frame inputs/end.png] \
  --width 1344 --height 768 --duration 8
```

### F. Review & iterate

1. Play the mp4 (native audio matters).
2. Extract a contact sheet:  
   `ffmpeg -y -i out.mp4 -vf "fps=1,scale=320:-1,tile=4x2" contact.png`
3. If weak: fix **prompt** first (specificity, camera, continuity), then seed, then duration.
4. Shipping / public claim: dual visual review per org rules if required.

### G. Deliver

Tell the user: **path · duration · resolution · seed · mode · wall time** (from receipt).

---

## 4. Ollama-shaped command cheat sheet

```bash
# Install (once)
curl -fsSL https://open-video.ai/install | bash          # Linux/macOS
# Windows: irm https://open-video.ai/install.ps1 | iex   # prefers WSL for GPU

cd "$OPEN_VIDEO_ROOT"
python -m open_video pull h3              # download / verify weights
python -m open_video pull h3 --check-only
python -m open_video status               # = ps
python -m open_video recommend-quant

python -m open_video run "<3-field or concept>" --duration 8
python -m open_video "concept" --dry-run
python -m open_video list-models
```

| Env | Meaning |
|---|---|
| `OPEN_VIDEO_ROOT` | Product checkout |
| `OPEN_VIDEO_MODELS` | Weights root (`h3_models` or ComfyUI/models) |
| `OPEN_VIDEO_COMFYUI` | ComfyUI base URL |
| `OPEN_VIDEO_MODEL` | Default backend (`h3`) |
| `H3_LAB` | Optional lab tree with ComfyUI + h3_agent |

---

## 5. Prompt micro-templates (copy & fill)

**T2V cinematic single beat**

```text
integrated_multimodal_description: [Shot 1] Live-action, cinematic, <wide/medium> shot frames <subject + clothing + age/gender if speaking>. <lighting + location>. The camera <push/pull/pan/track/arc> with <small|medium|large> amplitude at <slow|medium|fast> speed as <concrete action>.
overall_soundscape: <ambient>… <physical>…
non_diegetic_music: <instruments + tempo + dynamics>…
```

**T2V multi-shot (cut adds new info)**

```text
integrated_multimodal_description: [Shot 1] … [Shot 2] At 00:05.000, the camera cuts to …
overall_soundscape: …
non_diegetic_music: …
```

**I2V**

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Live-action, cinematic, starting from Picture 1, …
overall_soundscape: …
non_diegetic_music: …
```

---

## 6. Hard constraints

| Constraint | Limit |
|---|---|
| Duration / shot | **4–15 s** |
| Frame grid | **17k+5 @ 24 fps** |
| Local res | Short edge ≤ **768**; multiple of **32** |
| 2K | **API only** — cannot upscale local 768p with open weights |
| NVFP4 on 5090 | **Forbidden** (ComfyUI #14157) |
| License | MiniMax weight terms (region/commercial) + code Apache-2.0 |

---

## 7. When to use which skill

| Intent | Skill |
|---|---|
| **High-quality H3 clip, agent generate video** | **`h3-video` (this file) — default** |
| Multi-minute film, judge→refine→stitch | `skill/open-video` |
| Website / Pages | work in `open-video-web/` |
| Launch / strategy | `open-video-ops/` (private) |

---

## 8. Docs (read these, don't invent)

| Doc | Location |
|---|---|
| Prompt grammar | `$OPEN_VIDEO_ROOT/backends/h3/PROMPT_GRAMMAR.md` |
| Lab prompt guide | `$H3_LAB/docs/PROMPT_GUIDE.md` |
| Best practices | `$H3_LAB/docs/BEST_PRACTICES.md` |
| Quants / issues | `$OPEN_VIDEO_ROOT/docs/h3_ecosystem.md` |
| Quickstart | `$OPEN_VIDEO_ROOT/docs/QUICKSTART.md` |

---

## 9. Commit / path hygiene

- Product commits: inside `open-video-project/open-video` only (own git repo).
- Do not hardcode `/mnt/data/workspace/55-ai-video` as the **product** root in new code; use `Path(__file__).resolve()` or `OPEN_VIDEO_ROOT` / `H3_LAB`.
- Lab scripts under `55-ai-video/scripts/` should resolve `ROOT` from `__file__` (relative), not a frozen absolute path.
