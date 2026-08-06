# H3 Ecosystem — Build-On Reference for open-video

> Source: [wildminder/awesome-minimax-H3](https://github.com/wildminder/awesome-minimax-H3) + HF discussions + community agents (2026-08-07).
> **Rule: if it exists and works, integrate as a plugin — don't rewrite.**

## Direct integration targets (map to open-video components)

### Multi-shot orchestration → `core/pipeline.py` or `core/steps/`
- **ComfyUI-H3-Multishot** (jlucasmcrell) — script → N chained shots → seamless master.
  URL: https://github.com/jlucasmcrell/ComfyUI-H3-Multishot
  **open-video use:** replace our from-scratch stitcher with this (or wrap as a pipeline step plugin).

### Director / storyboard UI → `app/` frontend
- **ComfyUI-MiniMaxH3-Director** (seesee75-commits) — timeline editor + storyboard → per-shot prompts → render.
  URL: https://github.com/seesee75-commits/ComfyUI-MiniMaxH3-Director
  **open-video use:** reference for the app's storyboard UX; wrap as a plugin.

### Fast-path preset → `backends/h3/settings.py`
- **Turbo LoRA** (larryvrh/drbaph) — 4-step generation (vs 20-step default).
- **Dual-Clock Euler Sampler** (shuaixn) — fixes audio popping in 4-step Turbo mode.
  URL: https://github.com/shuaixn/ComfyUI-MiniMaxH3DualClockSampler
  **open-video use:** a "fast" preset (4 steps + Dual-Clock = ~5× faster, usable for drafts/preview).

### Prompt templates → `library/prompts/`
- **IT2V system prompt** (cushycrux, HF #47) — the "correct" I2V prompt generator.
  URL: https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/47
- **rzgar IT2V** (HF #28) — time-segmented variant.
  **open-video use:** import as the H3 crafter's system-prompt template.
- **Official prompt guide** — `docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md` (3-field structure).
  Already ported to `backends/h3/PROMPT_GRAMMAR.md`.

### Quants (per-GPU selection) → `backends/h3/settings.py`
- **NF4 (8 GB min)** — DiffSynth-Studio/MiniMax-H3-NF4. Lowest VRAM entry point.
- **W4 ConvRot (~10 GB)** — DmitryDB/MiniMax-H3-ComfyUI-Quants. Stock-compatible, balanced.
- **INT8 ConvRot (~21 GB)** — Comfy-Org. Our current default (proven on 5090).
- **BF16 (~62 GB)** — full quality, multi-GPU only.
- **NVFP4 (avoid on 5090 — ComfyUI #14157 bug).**

### Preview / thumbnails → `core/steps/`
- **Kijai TAE** (9 MB preview VAE) — ultra-cheap latent preview for the orchestrator.
  URL: https://huggingface.co/Kijai/MiniMax-H3-TAE

### 2K upscale → `core/steps/`
- **MiniMaxH3 LatentUpscaler** (Tr1dae) — spatial upsampler for H3's nested-tensor AV latents.
  URL: https://huggingface.co/Tr1dae/... (see awesome-list)

### Video tiling (for >768p or low VRAM)
- **comfyui-video-tiler** (maDcaDDie2000) — memory-aware tiling with overlap/gap/feather.

### Hybrid conditioning (advanced R2V + I2V)
- **minimax-h3-hybrid-cond** (kitsune123150) — R2V + I2V in one pass (single-pass ref+I2V).

### Speed nodes (45%+ speedup)
- **TE-Speed-MiniMaxH3-OSS** (HELPMEEADICE) — ~45% speedup patching the 50-layer DiT loop.
- **Block Cache T8** (T8mars) — F1B0 pattern: compute Block 0, reuse for Blocks 1-49.
- **SolAttention Triton** (kijai) — zero-copy SM89-SM120 attention kernel.

### Community finetune pipeline
- **HF #27 ka1029** — a working finetune pipeline (since MiniMax shipped no trainer).
  URL: https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/27

### Cross-model integration
- **vLLM-Omni + ComfyUI** (HF #36 shunyang90) — serving layer for all 3 H3 modes (T2VA/FL2VA/Ref2VA).
- **Prompt Enhancer** (T8mars) — calls doubao-seed-evolving for multimodal prompt analysis.
- **Ultra-Heretic TE** (ethanfel) — uncensored Qwen3-VL text encoder (⚠️ MiniMax takedown risk — private use only).

### macOS
- **minimax-h3-mlx** (mrbizarro) — full H3 pipeline ported to Apple Silicon.

## Known issues (open-video must guard against)
- **Wide-shot face corruption** (Comfy-Org #30 LabMike3D).
- **Long video 2K upscaling fails in ref2va** (Comfy-Org #19).
- **Ref2VA persistent noise** (HF #50).
- **AMD/Apple Silicon partially unsupported** (Comfy-Org #17, #24, #33).
- **CFG distillation ambiguity** (HF #44 — unclear if H3 is CFG-distilled or trained CFG-free).
- **Prompt metadata embedded in output files** (Comfy-Org #13).

## How open-video integrates these
Each tool above maps to an open-video **plugin point** (backend setting / pipeline step / library recipe / engine feature).
**Contributors:** wrapping any of these as an open-video plugin is a `good first issue` — see `CONTRIBUTING.md`.
