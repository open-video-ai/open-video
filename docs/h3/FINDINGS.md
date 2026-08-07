# Findings — MiniMax H3 research synthesis (2026-08-05)

Sources surveyed (priority: official → big community/company): `MiniMaxAI/MiniMax-H3` HF card,
`MiniMax-AI/MiniMax-H3` GitHub, `minimax.io` blog, ComfyUI tutorial @ docs.comfy.org, official
prompt guide, Comfy-Org HF + discussions, comfyui-wiki, Reddit r/StableDiffusion + r/LocalLLaMA,
HF discussions, X/MiniMax_AI, the `wildminder/awesome-minimax-H3` list.

## Official updates since deploy (2026-08-03 → 08-05)
- **HF card updated today (08-05)**: public load entry moved `modular_model_index.json` → `model_index.json`; README updates; **official prompt-writing guides added** (`docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md` + `_ref_en.md`); `docs/QA-about-License.md`.
- **Comfy-Org new weights (08-04/05)**: `minimax_h3_{fl2va,ref2va}_pruned_bf16.safetensors` and `_pruned_fp8_scaled.safetensors` — higher-quality pruned options beyond the int8 we use.
- **diffusers PR #14355 merged to `main` (08-05)**, NOT in any pip release (latest = 0.39.0). Even H100 84 GB OOMs on `.to("cuda")` → single 5090 must use sharded/group-offload load (ComfyUI remains the easier path).
- **NVFP4 bug #14157 still OPEN** (since 2026-05-28; pre-dates H3, generic Blackwell/nvfp4). No maintainer fix. Workaround: `EXTRA_RESERVED_VRAM` +4 GB for ≥16 GB cards.
- **License unchanged**: still excludes US/EU/UK/Korea; licensor = Nanonoble Pte. Ltd. (HK law). Confirmed by MiniMax X post + SCMP/Forbes/TechTimes.
- **Tech report**: still "coming soon" — not published. No official benchmark numbers.

## Official GitHub (`MiniMax-AI/MiniMax-H3`)
- Provides weights + serving configs (SGLang/vLLM **4-GPU** `--ulysses-degree 4`, diffusers, ComfyUI) + reproducible 768p shell scripts (t2va/fl2va) + a **full-2K workflow script** (`full-2k-t2v-h3-base.sh`: local 768p base → API H3-Regenerate-2K).
- No training code, no benchmarks, no tech report. Architecture detail: VisualVAE = "f16t4d24" (16× spatial / 4× temporal, 24 latent ch); AudioVAE 40 Hz token rate; 33B dense.

## Community verdict
- **Open-weight class**: H3 clearly beats **Wan 2.2** and **LTX 2.3** (HF discussion #8: "LTX2.3 looks like trash next to H3"). Competitive with **Seedance 2.0/2.5** — H3 wins on short clips + audio; Seedance on longer clips.
- **vs closed (Sora/Veo/Kling)**: weaker direct consensus; Veo/Sora still lead physics/textures; H3 positioned as **best local/open model**, not overall best.
- **Native stereo audio** is a real differentiator — widely praised.
- **5090/32 GB experience**: works with int8_convrot + dynamic offload; **speed is the pain** (community: 45 min for 10 s 1080p on RTX PRO 6000). NVFP4 users hit #14157 OOM. Reported glitch: **wide-angle face corruption** (#30). License region risk confirmed for US/EU/UK/KR.
- **Best community recipes**: provide strong **multimodal references** (R2V > pure T2V for consistency); use the official **IT2V system prompt**; Omni-Reference (text+image+video+audio in one gen) for best consistency.
- **China download**: ModelScope + `aria2c -x16 -s16` (no H3-specific secret route — standard pattern; matches what we did).

## Ecosystem (awesome-minimax-H3 + community)
- **Quant ladder** (stock ComfyUI unless noted): Comfy-Org int8_convrot (our pick) / fp8_scaled / bf16; **DmitryDB/MiniMax-H3-ComfyUI-Quants** W4 ConvRot **9.7 GB** (lowest stock-compatible); **DiffSynth-Studio NF4 8 GB min** (different engine); OrbitQuant W4A4 (needs custom node); GGUF (Abiray Q3–Q5, realrebelai Q2–Q4); tsolful INT4MixedConvRot; Kijai W4A8 experimental ("0.073 weight relL2 vs NVFP4 ~0.094").
- **Custom nodes**: `ComfyUI-MiniMax-H3-Guide` (prompt enhancement via Heretic encoder tail), `ComfyUI-KJNodes` (`ModelPreviewOverride` for TAE preview), `ComfyUI-OrbitQuant` (W4A4).
- **Text encoders**: Comfy-Org bf16/int8/nvfp4_awq; **Ultra-Heretic uncensored** (ethanfel) — bypasses alignment layers.
- **VAEs**: TAE preview (Kijai, 9 MB, preview-only); FP8 video VAE (dummy9996, 4.85→2.60 GB).
- **Speed**: SageAttention ~2× (official tutorial); MXFP8 "better audio at 5/8 steps" (rzgar).

## Open community requests (unmet)
INT4 official, non-CFG-distilled variant, open post-training pipeline, LoRA tooling, 2K upscaler node, FP32 VAE, Apple Silicon support.

## What this means for our 5090 deploy
- Our choices validated: **ComfyUI** (not diffusers — RAM), **int8_convrot** (not nvfp4 — #14157), **dynamic VRAM** (42.5 GB > 32 GB).
- **New levers to apply**: SageAttention (~2× speedup); the new `pruned_bf16`/`pruned_fp8` weights if we want to re-benchmark quality (RAM-tight); official prompt structure for quality; DmitryDB W4 (9.7 GB) if we want to cut VRAM/RAM pressure.
- **Hard limits unchanged**: local = 768p; 2K = API only; license region.
