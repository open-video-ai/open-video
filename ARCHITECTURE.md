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
                  [core: judge] ────→ vision-assess vs intent + quality bar
                                     │        ↓ below bar → diagnose → refine → regenerate
                  [core: stitcher] ─→ concat shots + audio continuity + 2K upscale (opt)
                                     │
                                     ──→ delivered multi-minute film + receipts
```

## Layers
### core/ (model-agnostic — the brain)
- **planner.py** — concept → coherence bible (5 state groups: identity/wardrobe/geography/story-knowledge/audio) + acts→scenes with time allocation + per-transition state vectors. Ported from woodfantasy methodology.
- **crafter.py** — intent → model-specific prompt (calls backend.craft_prompt / prompt_guide). LLM-driven; structured per the official model guide.
- **validator.py** — mode-aware hard constraint check (backend.constraints + timeline/refs/dialogue). Ported from early lab/scripts/validate_prompt.py.
- **judge.py** — the QUALITY LOOP (core IP). Extracts frames → vision-assesses (via analyze_image / cross-model cx+Opus) vs prompt intent + quality bar → diagnoses issues → returns verdict (PASS/refine-issues) + targeted fix suggestions. This is the VISTA/VideoWeaver pattern productized for open models.
- **pipeline.py** — the LONG-FILM ORCHESTRATOR (flagship). Orchestrates: plan → craft → validate → generate (w/ FL2VA chaining) → judge → refine → stitch. The 5-min film engine.
- **stitcher.py** — ffmpeg concat + cross-shot audio continuity (music theme/dialogue language/ambient crossfade) + optional 2K API upscale.
- **selector.py** — per-request model selection (from backends' capabilities.strengths). H3 for audio+adherence, Wan2.2 for physics, LTX for speed.
- **backend.py** — the contract (ModelBackend ABC + Capabilities + ShotRequest/Result + EngineAdapter).

### backends/<model>/ (plugins — one per open model)
- **h3/** — MiniMax H3: 3-field prompt grammar, FL2VA/T2V/R2V workflows, constraints (17k+5, 4-15s, ref limits), int8_convrot settings, ComfyUI generate. **Ported from early lab (proven working).**
- **wan2/** — (future) Wan 2.2: Apache-2.0 clean-license global anchor.
- **ltx/** — (future) LTX-2.3: real-time speed tier.
- Each backend: `backend.py` (implements ModelBackend) + `workflows/` + `PROMPT_GRAMMAR.md` + `__init__.py`.

### engines/<engine>/ (adapters — open-video drives the engine)
- **comfyui/** — ComfyUI HTTP API client (submit/wait/fetch). **Ported from early lab (proven working).**
- (future) diffusers/, sglang/ — direct engine adapters.

### interfaces/ (user entry points)
- **skill/** — Claude Code / agent-host skill (SKILL.md) — the director in any agent.
- **cli/** — `open-video "concept" --duration 300 --model h3` for non-agent users.
- (future) web/ — a GUI app (LTX Desktop pattern).

### library/ (community flywheel — the compounding moat)
- **prompts/** — curated prompt recipes (official + Seedance-port + community).
- **reference_packs/** — turnaround sheets + lighting boards for identity consistency.
- **coherence_recipes/** — pre-built coherence bibles for common film types.
- **style_profiles/** — style LoRAs + aesthetic presets.

### bench/ (evidence-based defaults)
- Auto-profiles each model+GPU → optimal settings (steps/sampler/quant/offload). Ported from early lab/scripts/h3_full_benchmark.py.

## The quality loop (core IP — how open delivers closed-grade quality)
```
generate(shot) → extract_frames(shot) → judge(frames, prompt_intent, quality_bar)
                                            │
                                     ┌──────┴──────┐
                                     PASS           REFINE
                                     │              │
                                  keep shot    diagnose(issues) → fix(prompt/mode/settings) → regenerate
```
This loop — proven by Google VISTA (+46.3% win rate via best-of-N tournament + triple-eval + refine)
and VideoWeaver (evidence-grounded agent-as-judge) — is what NO open video project has.
OpenMontage (45K★) lacks it; ViMax (11.7K★) is closed-API-only. **open-video owns this for open models.**

## The long-film pipeline (flagship — the 5-min film)
```
concept → planner(coherence_bible) → for each scene:
            craft(prompt) → validate(hard-gate) → generate(via backend+engine)
            → judge(quality-loop) → [refine if needed] → extract_last_frame
            → next_scene(first_frame = prev_last_frame)  # FL2VA chain
          → stitcher(concat + audio_continuity) → deliver(film.mp4 + receipts)
```
This is what Seedance does MODEL-natively (180s single generation); open-video does via
ORCHESTRATION (stitching + coherence-bible + state-vector handoff + per-shot judge). The
honest gap: stitched coherence < native coherence (drift accumulates); mitigated by the judge
loop catching drift at each transition.
