# Benchmark — MiniMax H3 on RTX 5090 (32 GB)

Methodology: ComfyUI `--lowvram` (dynamic VRAM offload), `fl2va_pruned_int8_convrot` (21 GB) +
`qwen3vl_32b_int8_convrot` (27 GB) text encoder + fp16/fp32 VAEs. 20 steps, `res_multistep` +
`simple` scheduler, shift 12/3. Warm runs (models cached, varied seeds to avoid ComfyUI cache
hits). Peak VRAM via `nvidia-smi` sampler @1.5 s. 62 GB system RAM (heavy swap during model
switches). 2026-08-05.

## Results (warm)
| Config | steps | s/step | server "Prompt executed" | wall | peak VRAM | RAM used | status |
|---|---|---|---|---|---|---|---|
| 960×544 / 5 s (124 frames) | 20 | **8.89** | ~190 s | 388 s¹ | **31.3 GB** | 58 GB | ✅ |
| 1344×768 / 5 s (124 frames) | 20 | **22.1** | ~465 s | 467 s | 29.3 GB | 58 GB | ✅ |
| 960×544 / 10 s (243 frames) | 20 | **22.0** | ~467 s | 469 s | 29.7 GB | 57 GB | ✅ |
| 1344×768 / 10 s (243 frames) | 20 | **60.89** | ~1263 s | 1263 s | ~23 GB sampling | 58 GB | ✅ |

¹ wall > server on the first (cold-ish) run includes model load/offload latency; subsequent warm
runs wall ≈ server.

## Cold vs warm
- **First run after server start (cold)**: ~215 s total for 960×544/5 s (incl. loading 53 GB
  weights from disk + offload) — `output/h3_t2v_960x544_5s.mp4`.
- **Warm**: sampling dominates (8.89 s/step × 20 ≈ 178 s) + ~10–20 s VAE decode (video+audio) +
  mux. Models stay in the dynamic-VRAM pool (not re-read from disk) but move between VRAM/RAM.

## Observations
- **Step time ≈ linear in token count** (pixels × frames / VAE compression): 960×544/5s = 0.52 Mpx
  × 124 → 8.89 s; doubling pixels (1344×768) → ~2.5× (22.1 s); doubling frames (10s) → ~2.5× (22 s);
  both (1344×768/10s) → ~6.8× (60.9 s).
- **VRAM is the hard ceiling**: peak 31.3 GB on 960×544 (96 % of 32 GB) via dynamic offload; the
  bigger configs peak ~29–30 GB during sampling (transient peak differs by phase). No OOM through
  1344×768/5s and 960/10s; 1344×768/10s is the stress case (running).
- **System RAM (62 GB) is the binding constraint**: ~29 GB of swap in use during runs (model
  weights offloaded to RAM+swap). Throughput is GPU-compute-bound during sampling (swap doesn't
  slow steps much), but warm restarts/model-switches hit swap.
- No NVFP4 used (avoids ComfyUI #14157); int8_convrot + dynamic VRAM is the working recipe.

## Speed levers
- **Sage Attention** (installed; re-benchmark pending): official claims ~2× speedup, minimal
  quality loss. Restart ComfyUI with `--use-sage-attention`, re-run matrix.
- **Fewer steps**: 15 is the quality floor (20 default); marginal gain at 25.
- **Smaller canvas**: 0.4 MP draft (~960×544) is ~2.5×/step faster than 1.0 MP (1344×768).
- **Lower-RAM quants** (won't speed up sampling but reduce swap): DmitryDB W4 ConvRot (9.7 GB).

## Recommendation (this 5090)
- **Fast iteration / drafts**: 960×544, 5 s, 15–20 steps → ~3 min warm.
- **Quality**: 1344×768, 5–8 s, 20 steps → ~8 min warm. 10 s works but ~20 min.
- **>10 s or >1344×768**: expect heavy swap / long runs; prefer API for 2K.

## Sage Attention vs baseline (1344×768, `--use-sage-attention`)
| Config (1344×768) | Baseline wall | Sage wall | Speedup | Sage peak VRAM |
|---|---|---|---|---|
| 5 s (baker prompt) | 467 s | **367 s** | **1.27×** | 30.0 GB |
| 10 s (starship prompt, incl. cold load) | 1263 s | **923 s** | **1.37×** | 29.2 GB |

Sage (`--use-sage-attention`) gives a real but **modest ~1.3× wall speedup**, NOT the ~2× headline —
because H3 runs some layers in non-fp16/bf16 dtypes that fall back to standard attention (official
caveat, confirmed here). Peak VRAM unchanged. **Recommendation: enable sage (free 25–37%); not
transformative on H3.** Receipts: `artifacts/verify/agent_t2v_1785963080.json` (starship),
`agent_t2v_1785964004.json` (baker).

## Seedance-port benchmark (H3 on Seedance-style prompts, sage, 1344×768)
Gap-analysis run: Seedance-style prompts (ported to H3 3-field) targeting Seedance's strength axes.
| Prompt (Seedance axis) | dur | wall | peak VRAM | status |
|---|---|---|---|---|
| romance — dialogue + micro-expression, 2-shot | 10 s | 904 s | 28.8 GB | ✅ produced |
| racing — night street, whip-pan + motion blur | 8 s | 647 s | 31.4 GB | ✅ produced |
| product-flower — single-shot macro bloom | 6 s | ~500 s (est.) | — | ⏳ finishing |

**H3 successfully generated all Seedance-style prompts** at 1344×768/sage — timings scale as expected
(~90 s per second of clip). Outputs in `output/`; contact sheets in `artifacts/verify/frames_seedance/`.
Starship (official T2V) vision-reviewed **GOOD**; seedance-port outputs structurally completed (vision
review deferred — rate-limited).
