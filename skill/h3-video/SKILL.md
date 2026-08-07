---
name: h3-video
description: >
  OpenVideo v0.0.1 harness — Ollama for MiniMax H3. Use whenever the user (or you as an agent)
  should generate high-quality local video: install/pull H3, status check, craft the official
  3-field prompt, validate, T2V/I2V/FL2VA generate, and review. Default skill for any agent host
  (Claude Code, Cursor, Codex, OpenCode, …). Prefer this over raw ComfyUI clicking.
---

# OpenVideo · H3 skill harness (v0.0.1)

**Product:** OpenVideo. **v0.0.1:** local MiniMax H3 (Ollama-style) + skill harness so **any agent** can generate high-quality video.

| | |
|---|---|
| Product | OpenVideo |
| Version | **0.0.1** |
| Model | MiniMax H3 |
| Engine | ComfyUI |
| Repo | https://github.com/open-video-ai/open-video |
| Install | https://open-video.ai/install |

You are the **agent driver**. Do not invent prompt formats — follow this file and `backends/h3/PROMPT_GRAMMAR.md`.

```text
install → pull h3 → status → craft 3-field prompt → run → review mp4
```

## 0. Non-negotiables (quality)

1. **Always** use the official **3-field** H3 prompt (not a bare one-liner) for final generates.
2. **Validate** before spending GPU (`--dry-run` or validator issues = fix first).
3. Respect **4–15s / shot**, 17k+5 frame grid, short edge ≤768 local, **no NVFP4 on 5090**.
4. Prefer **INT8 ConvRot** unless `recommend-quant` says otherwise.
5. Record output path + short receipt for the user.

## 1. Ollama-shaped commands

```bash
curl -fsSL https://open-video.ai/install | bash   # once per machine
# or: ./scripts/install.sh --yes

open-video pull h3                 # ~54 GB, resumable
open-video pull h3 --check-only
open-video status                  # alias: ps
open-video recommend-quant

open-video run "<concept or full 3-field prompt>" --duration 5
open-video "sunset waves" --dry-run
```

| Env | Meaning |
|---|---|
| `OPEN_VIDEO_MODELS` | Weights root |
| `OPEN_VIDEO_COMFYUI` | ComfyUI URL (default `http://127.0.0.1:8188`) |
| `OPEN_VIDEO_MODEL` | Default `h3` |
| `OPEN_VIDEO_REPO` | Clone URL override for install |

## 2. Procedure (run in order)

**Step A — Host ready.** `open-video status`.  
- Weights incomplete → `open-video pull h3`  
- ComfyUI down → start via install or `python ComfyUI/main.py --lowvram --use-sage-attention`

**Step B — Mode.** Text only → T2V; 1 image → I2V; first+last → FL2VA.

**Step C — Craft prompt** (quality lever #1). Structure:

```text
[<instruction line for I2V/FL2VA only>]

integrated_multimodal_description: [Shot 1] <style first>, …
overall_soundscape: …
non_diegetic_music: …   # instrumentation/tempo — no vague mood words
```

Full rules: `backends/h3/PROMPT_GRAMMAR.md`.  
Simple NL → expand into 3-field; never ship a bare phrase as the only prompt for “high quality.”

**Step D — Dry-run** when unsure: `open-video run "…" --dry-run`

**Step E — Generate:** `open-video run "…" --duration 5` (defaults favor 1344×768-class when backend allows).

**Step F — Review.** Spot-check motion/identity/audio; refine prompt and re-run if weak.  
Ship bar (optional): cross-model visual review if the user’s rules require it.

**Step G — Deliver** `output/*.mp4` path + seed/settings if known.

### Python (same contract)

```python
from backends.h3.backend import H3Backend
from core.backend import ShotRequest
from engines.comfyui.adapter import ComfyUIAdapter

engine = ComfyUIAdapter(server="http://127.0.0.1:8188")
backend = H3Backend()
req = ShotRequest(
    prompt=<3-field string>, mode="t2v",
    width=1344, height=768, duration_s=5.0, seed=0,
)
result = backend.generate(req, engine=engine)
```

## 3. Hard constraints

- Duration **4–15s** per shot; longer → multi-shot / `skill/open-video` (later)
- Frame grid **17k+5 @ 24fps**; resolution multiple of **32**
- **2K** = API upscale only (not local H3)
- Weight licenses follow MiniMax / upstream — code is Apache-2.0

## 4. Docs

| Doc | Why |
|---|---|
| `backends/h3/PROMPT_GRAMMAR.md` | Official craft |
| `docs/h3_ecosystem.md` | Quants / known issues |
| `docs/QUICKSTART.md` | Human install |
| `skill/open-video/SKILL.md` | Long director (beyond 0.0.1 focus) |

## 5. Skill choice

| User intent | Skill |
|---|---|
| High-quality H3 clip / agent generate video | **h3-video (this) — v0.0.1 default** |
| Multi-minute film, judge loop, stitch | `open-video` |
| New model backend | CONTRIBUTING + templates |
