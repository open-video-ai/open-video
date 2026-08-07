# Official MiniMax H3 — features, examples, prompts, tutorials (catalog)

Sourced from `MiniMaxAI/MiniMax-H3` (HF card), `MiniMax-AI/MiniMax-H3` (GitHub), `minimax.io` blog,
ComfyUI tutorial (docs.comfy.org), official prompt guides. 2026-08-05.

## Modes (which weights / node)
| Mode | Weights | ComfyUI node | Inputs | Use |
|---|---|---|---|---|
| **T2VA** | `fl2va` | `MiniMaxH3ImageToVideo` | prompt only | text → video+audio |
| **I2VA** | `fl2va` | `MiniMaxH3ImageToVideo` | prompt + `first_frame` (1 img) | animate one image |
| **FL2VA** | `fl2va` | `MiniMaxH3ImageToVideo` | prompt + `first_frame` + `last_frame` (2 img) | interpolate between keyframes (single-shot) |
| **L2VA** | `fl2va` | `MiniMaxH3ImageToVideo` | prompt + `last_frame` (1 img, lands on it) | infer the lead-in to a final frame |
| **R2VA** | `ref2va` (DIFFERENT weights) | `MiniMaxH3ReferenceToVideo` | ≤9 img + ≤3 video + ≤3 audio (12 files) | lock identity/style/motion/voice |

R2V input limits: images ≤9; videos ≤3 (2–15 s each, ≤15 s total); audio ≤3 (2–15 s, can't be sole input); mixed ≤12 files. `ref_image_size`: `match` (fast) / `max` (≤2048 px, stronger identity).

## The 3-module system (only the middle is open)
1. **H3-Context-IR** — hosted preprocessor: free-form multimodal → structured context IR. **API-only** (multi-stage, multiple hosted models).
2. **H3-Base** (`FL2VA`/`Ref2VA`) — open. Generates audio+video @ 768p from context IR (or direct prompt). ← **this is what runs locally**.
3. **H3-Regenerate-2K** — in-context regeneration: 768p + original context → 2K. **API-only, not yet open**.

→ **Local ceiling = 768p + stereo audio. 2K needs the API's full chain (and won't accept a local 768p render — it needs the paired Context-IR).**

## Output specs
- Resolution: 768 px short edge (capped 768×1344); 2K via API only. Aspects: 21:9, 16:9, 4:3, 1:1, 3:4, 9:16.
- 24 fps; **4–15 s**; **32 kHz stereo** audio (dialogue + SFX + music in one pass). 11 languages.
- Architecture: 33B dense single-stream transformer; VisualVAE f16t4d24 (16× spatial / 4× temporal, 24 latent ch); AudioVAE 40 Hz token rate; CFG-distilled (no negative prompt/guidance).

## API endpoints (global `api.minimax.io` / CN `api.minimaxi.com`)
- `POST /video-generation-v2-create` — create
- `POST /video-generation-v2-h3-context-ir` — Context-IR
- `POST /video-generation-v2-regeneration` — Regenerate-2K
- `GET /v2/query/video_generation/{task_id}` — poll
- Params: `model=MiniMax-H3`, `content[]` (text/video_url/audio_url + reference roles), `resolution`, `duration` 4–15, `ratio`, `callback_url`.
- **Pricing**: 2K **$0.13/s** ($7.80/min, min $0.52/clip); 768p $0.09/s (closed beta); ref images first 5 free then $0.04 each; ref audio free.

## Official GitHub (`MiniMax-AI/MiniMax-H3`) scripts
Reproducible (768p, call SGLang `:30010`): `scripts/readme/reproducible-768p-{t2va,fl2va,ref2va}-request.sh`.
Full-2K (local Base + API chain): `scripts/readme/full-2k-{t2va,i2va,ref2va}-h3-{base,context-ir,regenerate-2k}.sh` + `-reference-{768p,2k}-result-by-directly-calling-open-platform-api.sh`.
SGLang serve: `sglang serve --model-path MiniMaxAI/MiniMax-H3 --num-gpus 4 --ulysses-degree 4 --performance-mode speed --model-variant fl2va`. (4-GPU; single 5090 uses ComfyUI instead.)

## Official prompts & guides (in HF `docs/`)
- `VIDEO_PROMPT_WRITING_GUIDE_base_en.md` — T2V/I2V/FL2VA/L2VA prompting (3-field structure; 4 example cases: baker T2VA, train-woman I2VA, cyclist FL2VA, glass L2VA).
- `VIDEO_PROMPT_WRITING_GUIDE_ref_en.md` — R2V prompting (reference tagging, role assignment).
- `QA-about-License.md` — license Q&A.
- These are also mirrored in our `docs/PROMPT_GUIDE.md` (condensed) + the example prompts in `prompts/`.

## Official tutorials
- ComfyUI: `docs.comfy.org/tutorials/video/minimax/minimax-h3` (T2V + I2V; Resolution Selector; SageAttention; node settings).
- ComfyUI Template Library (v0.30+): search "MiniMax H3" → t2v/i2v/r2v/flf2v workflows (UI format; we built API-format equivalents in `workflows/`).

## Our reproductions (this repo)
- `prompts/reproducible-768p-{t2va,fl2va,ref2va}-request.sh` — official scripts (raw).
- `prompts/official_t2va_starship.txt` — extracted starship T2VA prompt.
- `inputs/ramen_firstframe.png` (+ staged `ComfyUI/input/`) — official FL2VA first-frame.
- `workflows/h3_{t2v,flf2v}_api.json` — graph-validated ComfyUI API workflows (T2V + FL2VA).
- `prompts/cinematic_cityspeed.txt` — a guide-compliant T2V example we authored.
