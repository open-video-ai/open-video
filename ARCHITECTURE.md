# open-video — Architecture

## Overview
```
User concept ──→ [core: planner] ──→ coherence bible (acts/scenes/state-vectors)
                                     │
                  [core: crafter] ──→ per-shot prompts (model-specific 3-field)
                                     │
                  [core: validator] ─→ hard-gate (duration/refs/timeline/dialogue)
                                     │
                  [backends/<model>] ─→ generate shot (via engines/<engine>)
                                     │        ↑ FL2VA chain: prev last-frame → next first-frame
                  [core: judge] ────→ vision-assess vs intent + quality bar  (design; needs vision_fn)
                                     │        ↓ below bar → diagnose → refine → regenerate
                  [core: stitcher] ─→ concat shots + audio continuity + 2K upscale (opt)
                                     │
                                     ──→ multi-shot film + receipts  (partial / roadmap)
```

**Honest v0.0.1:** H3 single-shot generate + CLI/skill are the reliable path. Planner / judge /
long-film pipeline exist as code scaffolds; the live vision judge is not fully wired
(`core/judge.py` PASSes when no `vision_fn` is provided).

## Layers
### core/ (model-agnostic — the brain)
- **planner.py** — concept → coherence bible (5 state groups: identity/wardrobe/geography/story-knowledge/audio) + acts→scenes with time allocation + per-transition state vectors.
- **crafter.py** — intent → model-specific prompt (calls backend.craft_prompt / prompt_guide).
- **validator.py** — mode-aware hard constraint check (backend.constraints + timeline/refs/dialogue).
- **judge.py** — quality-loop **scaffold**: extract frames → optional vision assess → PASS/REFINE. Wire a real `vision_fn` for production judging.
- **pipeline.py** — long-film orchestrator (plan → craft → validate → generate → judge → stitch). **Partial.**
- **stitcher.py** — ffmpeg concat + cross-shot audio continuity + optional 2K API upscale.
- **selector.py** — per-request model selection from backends' capabilities.
- **backend.py** — the contract (ModelBackend ABC + Capabilities + ShotRequest/Result + EngineAdapter).

### backends/<model>/ (plugins — one per open model)
- **h3/** — MiniMax H3: 3-field prompt grammar, FL2VA/T2V/R2V workflows, constraints, ComfyUI generate. **Working path.**
- **wan2/** — (future) Wan 2.2.
- **ltx/** — (future) LTX-2.3.
- Each backend: `backend.py` + `workflows/` + `PROMPT_GRAMMAR.md` + `__init__.py`.

### engines/<engine>/ (adapters — open-video drives the engine)
- **comfyui/** — ComfyUI HTTP API client (submit/wait/fetch). **Working path.**
- (future) diffusers/, sglang/ — direct engine adapters.

### interfaces/ (user entry points)
- **skill/** — agent-host skills (`h3-video` for quality clips; `open-video` for director intent).
- **cli/** — `open-video` / `python -m open_video` for install, pull, status, run.
- (future) web app / HTTP API / MCP — not current product surfaces.

### library/ (community assets)
- **prompts/** — curated prompt recipes.
- **reference_packs/** — turnaround sheets + lighting boards (as they land).
- **coherence_recipes/** — pre-built templates for common film types.
- **loras/** — LoRA recipes (weights off-repo).

### bench/ (evidence-based defaults)
- Profiles model+GPU → settings (steps/sampler/quant). See `docs/h3/BENCHMARK.md`.

## The quality loop (design — not a shipped live critic by default)
```
generate(shot) → extract_frames(shot) → judge(frames, prompt_intent, quality_bar)
                                            │
                                     ┌──────┴──────┐
                                     PASS           REFINE
                                     │              │
                                  keep shot    diagnose(issues) → fix → regenerate
```
Research (e.g. Google VISTA-style judge + best-of-N, VideoWeaver-style agent-as-judge) motivates
this design. open-video implements the **hooks and receipts shape**; a wired vision backend is
required for real PASS/REFINE decisions. Competitors that lack an open, auditable loop are
context — not a claim that open-video already owns a finished product feature.

## The long-film pipeline (flagship design)
```
concept → planner(coherence_bible) → for each scene:
            craft(prompt) → validate(hard-gate) → generate(via backend+engine)
            → judge(quality-loop) → [refine if needed] → extract_last_frame
            → next_scene(first_frame = prev_last_frame)  # FL2VA chain
          → stitcher(concat + audio_continuity) → deliver(film.mp4 + receipts)
```
Some closed products generate long clips model-natively; open-video aims to do longer stories via
**orchestration** (stitch + coherence handoff + per-shot checks). Honest gap: stitched coherence
is weaker than native long generation; a real judge helps catch drift — when it is wired.
