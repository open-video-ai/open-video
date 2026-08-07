---
name: h3-video
description: >
  Ollama-style MiniMax H3 local video via OpenVideo. Use when the user wants to
  install/pull H3, check status, generate a single shot or short film (T2V/I2V/FL2VA),
  craft the official 3-field prompt, validate, or run the open-video H3 harness.
  Prefer this for "just generate a clip"; use skill open-video for multi-minute director films.
---

# H3 video harness (Ollama for MiniMax H3)

**Product:** OpenVideo · **Model:** MiniMax H3 · **Engine:** ComfyUI  
**Repo:** `https://github.com/open-video-ai/open-video` (private until owner opens)  
**Site / install:** `https://open-video.ai`

This skill is the **agent harness** around the open-video CLI + H3 backend — same mental model as Ollama:

```text
install  →  pull h3  →  status  →  run "prompt"
```

## 1. Ollama-shaped commands (do these first)

From a checkout (or after one-line install):

```bash
# One-line host setup (engine + weights + first dry-run)
curl -fsSL https://open-video.ai/install | bash

# Or from repo root
./scripts/install.sh --yes

# Weight inventory / resume download (~54 GB INT8 package)
open-video pull h3
open-video pull h3 --check-only

# Engine + weights + quant recommendation
open-video status          # alias: open-video ps
open-video recommend-quant

# Generate (aliases)
open-video run "a red panda eating bamboo in mist" --duration 5
open-video "sunset waves" --duration 8 --dry-run   # plan only, no GPU
```

**Env (optional):**

| Var | Meaning |
|---|---|
| `OPEN_VIDEO_MODELS` | Weights root (else `<repo>/ComfyUI/models`) |
| `OPEN_VIDEO_COMFYUI` | ComfyUI base URL (default `http://127.0.0.1:8188`) |
| `OPEN_VIDEO_MODEL` | Default backend (default `h3`) |
| `OPEN_VIDEO_REPO` | Git clone URL override for install |

## 2. Agentic procedure (best quality single shot)

1. **`open-video status`** — if weights incomplete → `pull h3`; if ComfyUI down → start engine (install.sh or `python ComfyUI/main.py --lowvram --use-sage-attention`).
2. **Mode:** text only → T2V; 1 image → I2V; 2 images → FL2VA.
3. **Craft 3-field prompt** (see `backends/h3/PROMPT_GRAMMAR.md`):
   - optional instruction line (I2V/FL2VA)
   - `integrated_multimodal_description:` style first, shots, camera prose
   - `overall_soundscape:`
   - `non_diegetic_music:` (instrumentation/tempo — no vague mood words)
4. **Validate / plan:** `open-video run "…" --dry-run` or pass a full `--prompt` path via library presets.
5. **Generate:** `open-video run "…" --duration 5 --width` via defaults (1344×768 when backend allows).
6. **Review:** extract frames; refine prompt if needed. Ship-quality → cross-model visual review.
7. **Receipts:** pipeline writes under `output/` and prefer `artifacts/verify/` for agent logs.

Python contract (same as skill `open-video`):

```python
from backends.h3.backend import H3Backend
from core.backend import ShotRequest
from engines.comfyui.adapter import ComfyUIAdapter

engine = ComfyUIAdapter(server="http://127.0.0.1:8188")
backend = H3Backend()
req = ShotRequest(prompt=<3-field>, mode="t2v", width=1344, height=768, duration_s=5.0, seed=0)
result = backend.generate(req, engine=engine)
```

## 3. Hard constraints (do not violate)

- **Duration 4–15s / shot**; longer → multi-shot director (`skill/open-video` / `LongFilmPipeline`).
- **Frame grid 17k+5 @ 24fps**; resolution multiple of 32; local short edge ≤768.
- **Quant:** default **INT8 ConvRot** (~54 GB). Resource-aware: `recommend-quant` (nf4/w4/int8). **No NVFP4 on RTX 5090** (ComfyUI #14157).
- **2K** = API upscale only, not local H3.
- Weights license / regional terms follow MiniMax — not Apache-2.0 for the model files.

## 4. Docs map

| Doc | Use |
|---|---|
| `backends/h3/PROMPT_GRAMMAR.md` | Official 3-field craft |
| `docs/h3_ecosystem.md` | Quants, known issues |
| `docs/QUICKSTART.md` | User install path |
| `skill/open-video/SKILL.md` | Full director (plan→judge→stitch) |
| `ARCHITECTURE.md` | Core / backends / engines |

## 5. When to use which skill

| Request | Skill |
|---|---|
| Pull / status / one clip / H3 prompt craft | **h3-video** (this) |
| Multi-minute film, judge loop, stitch | **open-video** |
| New model backend plugin | CONTRIBUTING + `templates/model_backend.py` |
