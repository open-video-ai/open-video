# Changelog

## v0.1.0-alpha (2026-08-07)

The first public release of OpenVideo — the open-source autonomous video generation platform.

### What works
- **H3 video generation** via ComfyUI (T2V + I2V + FL2VA chain for multi-shot films)
- **Quality loop** (generate → judge → refine — the core IP; judge v0 stub, ready for VLM wiring)
- **Multi-shot pipeline** (plan → generate → FL2VA chain → stitch → embed recipe → deliver)
- **Recipe-in-render** (embed full generation metadata in output MP4 — self-documenting + remixable)
- **LoRA support** (community fine-tuned style/domain enhancers via LoraLoader)
- **CLI** (`open-video "prompt"` + list-models + list-presets + serve + dry-run)
- **Plugin architecture** (ModelBackend + EngineAdapter + QualityJudge contracts)
- **One-click installer** (scripts/install.sh — 783 lines)
- **Pinokio** one-click config
- **pip-installable** (`pip install -e .`)
- **Benchmark harness** (bench/profile.py — model-agnostic)
- **9 coherence recipe presets** (cinematic short, product ad, music video, trailer, etc.)
- **7 validated prompt recipes** (official H3 prompts + Seedance-ported)
- **Demo film** verified GOOD (18s, 2-shot lighthouse, 1344×768, native stereo audio)

### What's v0 / known limitations
- "Try it" web page is a UI mockup (no live backend yet)
- Quality judge is a stub (PASS only — vision model wiring is v1)
- Planner prompts are templates (LLM crafter wiring is v1)
- Recipe embed via ffmpeg stream-copy may not persist in all MP4 containers
- Tests are smoke-level (no end-to-end generation tests in the test suite)
- No hosted SaaS/API yet (planned — see docs/SAAS_API.md)
- No 2K upscaling (API-only, not in open weights)

### Architecture
- **11 core modules** (backend, pipeline, judge, planner, validator, crafter, stitcher, selector, config, recipe, __init__)
- **H3 backend** (3-field prompt grammar, T2V+FL2VA workflows, constraints, settings, LoRA)
- **ComfyUI adapter** (HTTP API client)
- **Vision judge plugin** (judges/vision.py)
- **101 files** · Apache 2.0

### Verified
- 3/3 test suites pass (backend + pipeline + validator + LoRA)
- All GitHub star claims verified via API
- Arena Elo (H3 = #2, 1238) verified via Artificial Analysis
- Cross-model reviewed (8 issues found + fixed)
- User-tested (3 personas: PM, developer, creator)
- Pipeline consumes its own modules (no duplication)

### Documentation (19 strategy docs + tutorial + quickstart)
- POSITIONING · FEATURES · COMMUNITY · SAAS_API · PARTNERSHIPS
- CONTENT_CALENDAR · LAUNCH_PLAN · TUTORIAL · QUICKSTART
- OPEN_VS_CLOSED · GROWTH_PLAYBOOK · PLUGIN_REGISTRY
- COMPETITOR_DEEP_DIVE · REDDIT_LAUNCH_POSTS · X_LAUNCH_THREAD
- Plus: ARCHITECTURE · GOVERNANCE · CONTRIBUTING · getting-started · model-comparison

### Built on
- **ComfyUI** (124K★) — generation engine
- **MiniMax H3** (33B, Arena #2) — baseline model
- **VideoScore** (TIGER-AI-Lab) — judge primitive (planned)
- **woodfantasy** methodology (MIT-0) — coherence bible pattern
