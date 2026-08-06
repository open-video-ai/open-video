# open-video

**The open-source autonomous director layer for video generation — Seedance-grade long films, open.**

open-video sits **on top of** an engine (ComfyUI) and an open model (MiniMax H3 baseline) and
**directs** them: you describe a film, it plans the shots, generates each, judges quality, refines,
and stitches into a coherent multi-minute video with synced audio. The thing closed products
(Seedance/Sora/Veo) bake in — the agentic brain — but **open, local-first, model-agnostic,
community-driven.**

> Status: **v0 / planning**. Baseline model: **MiniMax H3** (the #1 open video model, at Arena
> parity with closed). Domain: **open-video.ai**. License: TBD (open-core lean).

## What it is / isn't
- ✅ **IS**: the autonomous **director** — planner, prompt-crafter, validator, **judge→refine loop**,
  multi-shot **stitcher**, reference-pack builder. Model-agnostic core, pluggable model backends.
- ❌ **IS NOT**: a video engine (ComfyUI won that — 124k★, we drive it, don't replace it), nor a
  model (H3/Wan/etc. are the backends), nor a closed SaaS.

## The thesis (evidence-based)
1. **Open models have closed the quality gap.** MiniMax H3 = Artificial Analysis Arena **T2V #2 /
   I2V #3 overall, #1 open** (Elo 1238/1189) — **within noise of closed #1** (Gemini Omni Flash
   1244 / Seedance 1197). The raw quality is already there.
2. **The remaining gap is the AGENT layer**, not the model: closed products ship a director
   (Seedance has an agentic long-video pipeline; Sora/Veo have polished UX). Open models ship as
   **single-shot engines** (ComfyUI = manual node-graph; no judge/refine/stitch).
3. **open-video is that layer, open.** It turns H3's arena-parity quality into **delivered
   parity/beating**: long films (stitching beyond the 15s ceiling), consistency (reference-packing),
   prompt-adherence (craft + validator + judge loop), 2K (API upscale).

## Flagship demo / north star
**A 5-minute, high-quality, coherent short film — generated end-to-end from a concept.**
No single model does >15–30s; a 5-min film is impossible without an agent (plan → multi-shot →
chain → judge → refine → stitch → audio). It's the proof that open-video's layer matters, and the
open answer to Seedance's closed long-video pipeline. Target: open 5-min film that holds up
alongside a Seedance/Sora short.

## Why it can win
- **Open + local + free** vs closed API cost/lock-in/region-restrictions.
- **Model-agnostic** vs single-model wrappers; the director survives model churn (H3 today,
  Wan3/FLUX3-Dev tomorrow).
- **Community recipes** (prompts, reference-packs, coherence bibles, style LoRAs) = a compounding
  moat closed vendors can't match (their know-how is internal; ours is a shared library).
- **Partners with ComfyUI**, doesn't fight it — the agent brain on the community's engine.

## Repo layout (v0 plan)
```
open-video/
  README.md  PLAN.md  ARCHITECTURE.md
  core/            # model-agnostic agent: planner, crafter, validator, judge-loop, stitcher, ref-pack
  backends/        # model plugins: h3/ (now), wan3/, flux3/ (later) — each: capabilities, prompt_grammar, workflow, constraints, settings
  engines/         # engine adapters: comfyui/ (now) — open-video drives the engine via its API
  skill/           # open-video skill (Claude Code / agent hosts)
  cli/             # `open-video "..."` for non-agent users
  library/         # community: prompts, reference-packs, coherence-recipes, style profiles
  bench/           # auto-profile harness (per model/GPU → evidence-based defaults)
  docs/
```

See `PLAN.md` for the phased roadmap + open decisions, `ARCHITECTURE.md` (next) for the core/contract.
