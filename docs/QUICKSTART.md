# OpenVideo Quickstart (v0.0.1)

> **v0.0.1 = Ollama for MiniMax H3 + `skill/h3-video` harness** — any agent can generate high-quality local video.  
> Canonical commands for README / site / tutorial.

## Prerequisites
- **NVIDIA GPU** (8GB+ VRAM for NF4, 32GB+ for INT8 ConvRot)
- **Linux or macOS** (Windows via WSL2)
- **~60GB disk** (for ComfyUI + H3 weights)

## 3 Steps (human / CLI)

### 1. Install
```bash
curl -fsSL https://open-video.ai/install | bash
# or: git clone … && bash scripts/install.sh
```
First run downloads ~54GB of H3 weights (resumable).

### 2. Pull / status (Ollama-shaped)
```bash
open-video pull h3
open-video status
```

### 3. Generate
```bash
open-video run "a cinematic lighthouse on a cliff at dusk, golden light, stormy sea"
# dry-run without GPU:
open-video "sunset waves" --dry-run
```

## Agent path (any host)

1. Load **`skill/h3-video/SKILL.md`**
2. Agent runs install/pull/status as needed
3. Agent crafts **official 3-field H3 prompt** (not a bare one-liner)
4. Agent runs `open-video run …` and returns the mp4

## What happens (v0.0.1)
1. Weights + ComfyUI ready (`pull` / `status`)
2. Skill or human crafts H3 3-field prompt (quality lever)
3. H3 generates clip (local GPU; typical 5–10s, 1344×768-class)
4. Output under `output/` — review and refine prompt if needed

## Try more

### Different resolution / duration
```bash
open-video "a neon koi swimming through rain" --duration 10 --aspect 9:16
```

### With a LoRA
```bash
open-video "a product shot of a luxury watch" --lora cinematic-v2 --lora-weight 0.7
```

### Multi-shot film (beyond 15s)
```bash
open-video "a 60-second short film about a lighthouse keeper" --duration 60
```

### Inspect a video's recipe (the recipe-in-render feature)
```bash
open-video inspect output/film.mp4
```

### Remix a video (recreate from embedded recipe)
```bash
open-video remix output/film.mp4
```

## Troubleshooting
| Issue | Fix |
|---|---|
| `CUDA out of memory` | Use NF4 quant (8GB VRAM) — edit `backends/h3/backend.py` settings |
| Download slow | Use aria2c with 16 connections: `aria2c -x16 -s16 <url>` |
| ComfyUI not running | `cd ComfyUI && python main.py --listen --lowvram --use-sage-attention` |
| NVFP4 OOM on 5090 | Avoid NVFP4 — use INT8 ConvRot (default) |

## Next steps
- Browse prompts: `open-video list-presets`
- Browse models: `open-video list-models`
- Read the tutorial: `docs/TUTORIAL.md`
- Contribute: `CONTRIBUTING.md`
