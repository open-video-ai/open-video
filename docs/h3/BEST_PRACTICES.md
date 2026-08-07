# Best Practices — MiniMax H3 on RTX 5090 (32 GB)

Consolidated from official docs (model card, `MiniMax-AI/MiniMax-H3` GitHub, ComfyUI tutorial
@ docs.comfy.org, official prompt-writing guide), Comfy-Org, and community (HF discussions,
comfyui-wiki). Unverified items marked ⚠️.

## 1. Optimal generation settings

| Param | Best value | Notes / source |
|---|---|---|
| **Resolution** | **1344×768** (16:9, ~1.0 MP) | Native trained canvas = 768 px short edge, capped 768×1344. Multiple must be **32**. (ComfyUI tutorial) |
| Draft / fast | ~0.4 MP (e.g. 960×544) | ~2.3× faster per step than 1344×768. |
| Floor | 384 px short edge | "256p fails entirely." (comfyui-wiki) |
| **Steps** | **20** | 15 = floor; 25 = marginal gain. Model is **CFG-distilled** → no negative prompt / guidance. (comfyui-wiki) |
| **Sampler** | `res_multistep` | T2V/I2V baseline. |
| **Scheduler** | `simple` | T2V/I2V. For **R2V** use `beta` or `normal` (better for reference-dense). |
| **Shift** | video=12 / audio=3 ⚠️ | **Unverified officially** — community-inherited from Hailuo-02. `MiniMaxH3SigmaShift` node; trust node defaults if unsure. |
| Duration | 5–10 s (max 15) | Snaps to **17k+5** frame grid @ 24 fps (e.g. 5 s → 124 frames). |
| Audio | 32 kHz stereo, native | Modeled jointly in one pass — describe dialogue/SFX/music in prompt. |

No official quality/speed table exists; qualitative tradeoff = steps (15→20→25) and megapixels (0.4→1.0).

## 2. Modes — which weights / node to use

| Mode | Weights | Node | Inputs | Use when |
|---|---|---|---|---|
| **T2V** | `fl2va` | `MiniMaxH3ImageToVideo` | prompt only (no frames) | pure text → video |
| **I2V** | `fl2va` | `MiniMaxH3ImageToVideo` | + `first_frame` (1 image) | animate one image |
| **FLF2V** | `fl2va` | `MiniMaxH3ImageToVideo` | + `first_frame` + `last_frame` | interpolate between 2 keyframes (favors single shot) |
| **R2V** | `ref2va` (different weights!) | `MiniMaxH3ReferenceToVideo` | ≤9 img + ≤3 video + ≤3 audio (12 files max) | lock identity/style/motion/voice across shots |

- `first_frame` / `last_frame` are **always optional**; I2V and FLF2V are the same node, differ only in how many keyframes you wire.
- R2V `ref_image_size`: **`match`** = scale refs to gen res (faster); **`max`** = up to 2048 px short edge (stronger identity, slower).
- R2V: tag refs in connection order (`<Picture 1>`, `<Video 1>`, `<Audio 1>`) and **explicitly assign** each ref to a role (identity/style/motion/camera/voice) — "explicit assignments work much better."

## 3. RTX 5090 (32 GB) tuning — critical

- **Weight choice**: `*_pruned_int8_convrot` (FL2VA 21 GB / Ref2VA 21 GB) + `qwen3vl_32b_int8_convrot` (27 GB) text encoder + fp16/fp32 VAEs. Total staged ~42.5 GB > 32 GB → **dynamic VRAM offload is mandatory** (`--lowvram`).
- **Avoid NVFP4** on 5090: ComfyUI issue **#14157** — nvfp4 native ops bypass the PyTorch allocator → ComfyUI underestimates VRAM → VAE-decode OOM/stall (150–300 s instead of ~10 s) on 2nd+ run. Affects the otherwise-recommended `qwen3vl_32b_nvfp4_awq` text encoder.
  - If you must use NVFP4: patch `comfy/model_management.py` → `EXTRA_RESERVED_VRAM` from +100 MB to **+4 GB** for ≥16 GB cards (community-confirmed stable for 20+ runs).
- **Sage Attention** ≈ **2× speedup**, minimal quality loss:
  - `pip install sageattention` (match torch/CUDA) + install **KJNodes** → `Patch Sage Attention KJ` node between `UNETLoader` → `BasicGuider` (`sage_attention=auto`); **or** launch with `--use-sage-attention`.
  - Caveat: needs fp16/bf16 tensors; H3 runs some layers in other dtypes → some layers fall back (expected).
- `--disable-pinned-memory` reportedly restores fast loading on some setups.
- **RAM-bound**: with 62 GB system RAM + 54 GB weights, expect heavy swap during model switches (slower warm restarts). Keep other big processes off the box.

## 4. Weight selection (Comfy-Org/MiniMax-H3)

| Component | Recommended (5090) | Alternatives |
|---|---|---|
| Diffusion (FL2VA) | `minimax_h3_fl2va_pruned_int8_convrot` (21 GB) | `pruned_fp8_scaled` (21 GB, slightly different quality); `pruned_bf16` (~40 GB, max quality, RAM-tight); bf16 full (66 GB) |
| Diffusion (Ref2VA) | `minimax_h3_ref2va_pruned_int8_convrot` (21 GB) | same ladder |
| Text encoder | `qwen3vl_32b_minimax_h3_int8_convrot` (27 GB) | bf16 (51 GB); **nvfp4_awq (15.7 GB) — avoid on 5090 (#14157)** |
| Video VAE | `minimax_h3_video_vae_fp16` (5.2 GB) | — |
| Audio VAE | `minimax_h3_audio_vae_fp32` (0.6 GB) | — |

Community quants for lower VRAM: DmitryDB W4 ConvRot (9.7 GB, stock ComfyUI), DiffSynth NF4 (8 GB min, different engine), OrbitQuant W4A4, GGUF (Abiray/realrebelai).

## 5. The 2K path (API-only)

Local open weights cap at **768p**. Native 2K requires the hosted **H3-Regenerate-2K** module
(not open). The official `MiniMax-AI/MiniMax-H3` GitHub ships `scripts/readme/full-2k-t2va-h3-base.sh`.

- Endpoints (global `api.minimax.io` / CN `api.minimaxi.com`): `/video-generation-v2-create`,
  `/video-generation-v2-h3-context-ir`, `/video-generation-v2-regeneration`.
- **Price**: 2K = **$0.13/s** ($7.80/min, min $0.52/clip); 768p = $0.09/s (closed beta).
- ⚠️ **You cannot feed a local 768p render into Regenerate-2K** — it needs the Context-IR
  intermediate from the API's own pipeline. For 2K, run the whole thing via API.

## 6. Recommended "best result" recipe (local max quality, 5090)

```
Diffusion:  fl2va_pruned_int8_convrot   |  Text enc: qwen3vl int8_convrot
VAE:        video fp16 + audio fp32      |  ComfyUI: --lowvram --use-sage-attention
Resolution: 16:9, ~1.0 MP → 1344×768, multiple=32
Sampler:    res_multistep  |  Scheduler: simple  |  Steps: 20  |  shift 12/3 (⚠️ unverified)
Duration:   5 s (124 frames)
Prompt:     official 3-field structure (see PROMPT_GUIDE.md)
```
For R2V: swap to `ref2va_pruned_int8_convrot`, scheduler `beta`/`normal`, `ref_image_size=max`.
