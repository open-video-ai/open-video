---
name: open-video
description: Generate, edit, or direct videos via open-source models (MiniMax H3 baseline; Wan2.2 / LTX future). Use when the user wants to turn a concept, script, or reference image into a finished video or multi-shot film — single shots, image-to-video, first-last-frame interpolation, reference-video/audio styling, or stitched long films beyond the 15s model ceiling. Covers prompt crafting, hard validation, ComfyUI-driven generation, vision judging, refine loop, and ffmpeg stitching.
---

# open-video — autonomous director skill

> **v0.0.1 default for high-quality H3 clips is [`skill/h3-video`](../h3-video/SKILL.md)**  
> (Ollama for H3 + harness). Use **this** skill when the user wants multi-shot / long-film
> director behavior (plan → judge → stitch) beyond a single strong clip.

## 1. What open-video does

open-video is the **autonomous director** layer on top of open video models. It turns a concept
into a finished film by running the loop no open engine ships natively:

**plan → craft → validate → generate → judge → refine → stitch → deliver**

- **Model-agnostic core** (`core/`): planner (coherence bible), crafter, validator, judge-loop,
  stitcher, selector, ref-pack builder.
- **Pluggable backends** (`backends/<model>/`): baseline = **MiniMax H3** (#1 open model, Arena
  parity with closed, native stereo audio). Future: Wan2.2 (physics), LTX-2.3 (speed).
- **Engine adapter** (`engines/comfyui/`): drives ComfyUI via its HTTP API. open-video is the brain;
  ComfyUI is the hands.

It is NOT a video engine (ComfyUI is the engine) and NOT a model (H3/Wan/LTX are backends). It is
the agent brain ComfyUI lacks: the judge→refine loop + multi-shot stitcher + coherence planner.
Flagship output: a multi-minute coherent film from a concept (impossible with any single open
model, which all cap at ≤15–30s).

## 2. Agentic procedure — run these steps in order

**Step 1 — Understand the request.** Classify the job: single shot vs multi-shot film; target
duration; did the user supply reference image(s) / video / audio; desired aspect; quality bar. If
the request is ambiguous *and* the target is a film >30s, ask ONE focused question (subject +
mood + length). Do not generate a long film on guesswork.

**Step 2 — Pick the mode.** Mode is auto-derived from inputs (see `backends/h3/backend.py` and
`scripts/validate_prompt.py` `detect_mode`):
- **T2V / T2VA** — text only, no image. Native audio + video.
- **I2V / I2VA** — one image (first frame). Instruction line: `"For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced."`
- **FL2VA** — two images (first + last frame). Continuous interpolation. **This is the multi-shot
  chain mode**: previous shot's last frame → next shot's first frame for continuous handoff.
- **L2VA** — one image referenced at the **final** timestamp.
- **R2V / Ref2VA** — reference video/audio for identity / style / motion / voice. Tag refs
  `<Picture 1>`, `<Video 1>`, `<Audio 1>` and explicitly assign each a role.

**Step 3 — Craft the 3-field prompt** (per `backends/h3/PROMPT_GRAMMAR.md`). Exact structure:
```
[<instruction line>     # ONLY for I2V/FL2VA/L2VA — first line, then a blank line]

integrated_multimodal_description: [Shot 1] <style first>, <composition/subjects/scene>. <camera type + amplitude + speed>. [Shot 2] At 00:0X.XXX, the camera cuts to <next beat>.
overall_soundscape: <1–4 sentences: ambient / physical / non-verbal human sound>
non_diegetic_music: <1–3 sentences: instrumentation / tempo / rhythm / dynamics — NO mood words>
```
Hard rules: state **style first** in Shot 1 (Cinematic / live-action / 2D-animated / 3D CG / claymation / watercolor / vintage film); **don't timestamp Shot 1**; later shots use **strictly increasing** cut times within the duration; keep identity/wardrobe/color/objects/spatial relations consistent across shots; camera motion = natural prose combining **type + amplitude + speed** (Push In / Pull Out / Pan / Truck / Tilt / Arc / Tracking / Static / POV / Roll — omit amplitude/speed when medium/normal); dialogue as `<d>[lang] verbatim words</d>` with stable `(S1)/(S2)` speaker IDs (first appearance gives age/gender/on-screen/pitch/timbre/rate/accent); on-screen text in English double quotes, verbatim; **every detail must be visible or audible — no abstract mood/emotion words**; prefer camera motion over a cut for mere distance/angle changes.

**Step 4 — Validate before generate** (`core/validator.py`, hard gate — never skip). Checks: all 3
required fields present; duration within 4–15s; mode matches the instruction line; image/ref counts
match the mode; cut times strictly increasing and within duration; `<d>[lang]…</d>` well-formed.
**Fix every issue before spending GPU.** A shot that fails validation will fail the judge.

**Step 5 — Generate** via ComfyUI (`backends/h3/backend.py` + `engines/comfyui/adapter.py`).
Confirm the server is up first (§3). H3 defaults: 1344×768, 20 steps, `res_multistep` / `simple`
scheduler, `shift_video=12.0` / `shift_audio=3.0`, INT8 ConvRot quants, engine flags
`--lowvram --use-sage-attention`. `length` snaps to the 17k+5 grid.

**Step 6 — Judge the output** (`core/judge.py` — the core IP). Extract ~5 frames; vision-assess
each vs the prompt intent + a quality bar (drift, dropped element, bad motion, identity break,
audio/video desync). Verdict: **PASS / REFINE / FAIL**. Record frames + verdict in the receipt.
This loop — not the model — is open-video's reason to exist.

**Step 7 — Refine if REFINE or FAIL.** Diagnose the *specific* issue, apply a *targeted* fix (prompt
tweak / +steps / different mode / ref-pack for identity lock / different seed), regenerate. Strategy
is **refine-primary, not best-of-N**: H3 raw quality is already at parity — the loop fixes
adherence, length, and consistency, which is where the gap actually lives. Best-of-N is an optional
escape hatch, not the default.

**Step 8 — Stitch multi-shot** (`core/pipeline.py` `LongFilmPipeline.make_film`). Each subsequent
shot's `first_frame` = the previous shot's last frame (ffmpeg-extracted at `-sseof -0.1`); a `t2v`
shot is auto-upgraded to `i2v` when a handoff frame exists. Then ffmpeg concat (`-f concat -c copy`)
+ cross-shot audio continuity (music theme / dialogue language / ambient crossfade). Optional 2K
upscale via API as a final step.

**Step 9 — Deliver.** One coherent film + per-shot receipts (prompt, seed, settings, judge verdict,
extracted frames). Persist receipts under `artifacts/verify/`.

## 3. Key commands

**Server — start ComfyUI first (the engine), on `http://127.0.0.1:8188`:**
```bash
cd /path/to/ComfyUI && python main.py --lowvram --use-sage-attention   # H3 default flags
```
Health check: `curl -s http://127.0.0.1:8188/system_stats` (returns JSON when up). In Python:
`ComfyUIAdapter(server="http://127.0.0.1:8188").health()`.

**Generate one shot — open-video Python API (the contract; lives in `backends/` + `engines/`):**
```python
from backends.h3.backend import H3Backend
from core.backend import ShotRequest
from engines.comfyui.adapter import ComfyUIAdapter

engine = ComfyUIAdapter(server="http://127.0.0.1:8188")
backend = H3Backend()
req = ShotRequest(prompt=<3-field prompt string>, mode="t2v",
                  width=1344, height=768, duration_s=10.0, seed=0)
result = backend.generate(req, engine=engine)   # → ShotResult(ok, video_path, receipt)
```
- User-facing CLI (planned in `cli/`): `open-video "<concept>" --duration 300 --model h3`.
- Proven baseline scripts (same workflows, ported from the early lab):
  - Single shot: `scripts/h3_agent.py --request "<simple NL>" --duration 5 --width 1344 --height 768`
    (use `--prompt "<full 3-field prompt>"` for best quality; `--first-frame`/`--last-frame` for I2V/FL2VA).
  - Validate: `scripts/validate_prompt.py` (exit 0 = clean, 1 = issues).

**Multishot / long film — `core/pipeline.py` `LongFilmPipeline.make_film(plan, out_path)`:**
`plan` is a `list[Shot(scene_id, prompt, mode, duration_s, seed, …)]`. The pipeline generates each
shot → judges → extracts last frame → chains (FL2VA handoff) → stitches → writes `output/film.mp4`
and returns `(film_path, plan_with_receipts)`.
- Proven baseline: `scripts/h3_multishot.py --plan plans/multishot_demo.json --out output/long_demo.mp4`
  where plan JSON = `{"shots": [{"prompt_file": "...", "duration": 10, "first_frame": null}, …]}`.

## 4. Constraints (H3 baseline — hard, evidence-based)

- **Duration: 4–15s per shot** (`backends/h3/backend.py` `constraints()` → `duration_range_s: (4, 15)`).
  No single shot >15s. For longer content, use multishot — that is the entire point of the stitcher.
- **Frame grid: num_frames snaps to 17k+5 @ 24fps** (video-VAE temporal constraint; `_snap_17k5`).
  Valid lengths: 5, 22, 39, 56, … Do **not** pass arbitrary frame counts.
- **Resolution: local ceiling = 768 short edge** (native canvas 768×1344), multiples of 32
  (`resolution_multiple: 32`). **2K = API upscale only** — never attempt 2K locally.
- **Refs: ≤9 images, ≤3 videos, ≤3 audios, ≤12 total** (`max_refs`).
- **Quant — use INT8 ConvRot** (`minimax_h3_fl2va_pruned_int8_convrot.safetensors`, ~21 GB, proven on
  RTX 5090). **Avoid NVFP4 on RTX 5090 — ComfyUI issue #14157 bug** (recorded in
  `backends/h3/backend.py` `default_settings()["known_issues"]` and `docs/h3_ecosystem.md`).
  Other quants: NF4 (~8 GB, lowest VRAM), W4 ConvRot (~10 GB, stock-compatible), BF16 (~62 GB, multi-GPU only).
- **Audio: 32 kHz stereo native; CFG-distilled** (no negative prompt, no guidance scale).
- **Known issues to guard against** (`docs/h3_ecosystem.md` "Known issues"): wide-shot face
  corruption (Comfy-Org #30), 2K upscale fails in ref2va (#19), ref2va persistent noise (HF #50),
  AMD/Apple Silicon partial support (#17/#24/#33), prompt metadata embedded in output files (#13).

## 5. Docs — read these for depth (do not guess from memory)

- `README.md` — what/why, three interfaces (App / CLI / Skill), the thesis.
- `ARCHITECTURE.md` — core / backends / engines / library layers; the quality loop; the long-film pipeline diagram.
- `PLAN.md` — phased roadmap, open decisions, the make-or-break success metric.
- `backends/h3/PROMPT_GRAMMAR.md` — the official H3 3-field prompt guide (condensed). **Read before crafting any H3 prompt.**
- `docs/h3_ecosystem.md` — quants, multishot tools, speed nodes, known issues, build-on targets.
- `templates/model_backend.py` — the plugin template (§6).
- `CONTRIBUTING.md` — plugin points + good-first-issues.

## 6. Adding a model backend (Wan2.2, LTX, …)

The core never changes — add a plugin. Copy `templates/model_backend.py` →
`backends/<model>/backend.py` and implement the `ModelBackend` ABC (`core/backend.py`):

1. **`capabilities`** (`Capabilities(...)`) — which modes (`t2v`/`i2v`/`flf2v`/`r2v`),
   `native_audio`, `max_duration_s`, `max_short_edge_px`, `strengths` (the `selector` keys on these).
2. **`prompt_guide()` + `craft_prompt(intent, mode)`** — your model's prompt grammar.
3. **`constraints()`** — duration range, frame grid (or `None`), `max_refs`, resolution multiple.
4. **`generate(req, engine)` + `_build_workflow(req)`** — build the engine workflow (e.g. ComfyUI
   JSON loaded from `workflows/`), run via the engine adapter, return `ShotResult(ok, video_path, receipt)`.
5. **`default_settings()`** — steps / sampler / scheduler / quant (evidence-based via `bench/`).
6. **`duration_to_length()` / `resolution_for()`** — model-specific frame/fps and resolution-grid math.

Then add `backends/<model>/workflows/` (engine JSON), `PROMPT_GRAMMAR.md`, and `__init__.py`.
**See `backends/h3/backend.py` for a complete working example** — the H3 backend is the reference
implementation. PR it; `CONTRIBUTING.md` lists plugin points as good-first-issues.
