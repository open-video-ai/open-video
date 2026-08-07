# OpenVideo Quickstart

> **v0.0.1:** Ollama for MiniMax H3 + `skill/h3-video` harness — any agent can generate high-quality local video.


> This is the ONE official quickstart. All docs (README, website, tutorial) should use these exact commands.

## Prerequisites
- **NVIDIA GPU** (8GB+ VRAM for NF4, 32GB+ for INT8 ConvRot)
- **Linux or macOS** (Windows via WSL2)
- **~60GB disk** (for ComfyUI + H3 weights)

## 3 Steps

### 1. Clone
```bash
git clone https://github.com/open-video-ai/open-video.git
cd open-video
```

### 2. Install (one-click: sets up venv + ComfyUI + downloads H3 weights)
```bash
bash scripts/install.sh
```
> First run downloads ~54GB of model weights (~30 min on fast connection). Subsequent runs skip completed steps.

### 3. Generate
```bash
open-video "a cinematic lighthouse on a cliff at dusk, golden light, stormy sea, camera pushing in"
```

## What happens
1. OpenVideo plans the shot (coherence bible + prompt crafting)
2. H3 generates the video (1344×768, 24fps, native stereo audio)
3. The quality judge extracts frames + assesses vs prompt intent
4. If below bar → diagnose + refine + regenerate
5. Output: `output/film.mp4` with embedded recipe metadata

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
