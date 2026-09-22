# OpenVideo Quickstart (v0.1.0)

> **v0.1.0 = Ollama for MiniMax H3 + `skill/h3-video` harness** — any agent can generate high-quality local video.
> Canonical commands for README / site / tutorial.

## Prerequisites
- **NVIDIA GPU** (32GB-class VRAM for the default INT8 ConvRot path; smaller cards need manual, experimental W4/NF4 tiers)
- **Linux or macOS** (Windows via WSL2)
- **~60GB disk** (for ComfyUI + H3 weights)

## 3 Steps (human / CLI)

### 1. Install
```bash
git clone --depth 1 --branch v0.1.0 https://github.com/open-video-ai/open-video
cd open-video
bash scripts/install.sh
```
First run downloads ~54GB of H3 weights (resumable, integrity-verified).
The `curl https://open-video.ai/install` site installer still serves the
previous release until an authorized site cutover — use the tag clone above.

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

## What happens (v0.1.0)
1. Weights + ComfyUI ready (`pull` / `status`)
2. Skill or human crafts H3 3-field prompt (quality lever)
3. H3 generates clip (local GPU; typical 5–10s, 1344×768-class)
4. Output under `output/` — review and refine prompt if needed

## Try more

### Different resolution / duration
```bash
open-video "a neon koi swimming through rain" --duration 10 --aspect 9:16
```

### Image-to-video / first-last-frame
```bash
open-video run "…" --mode i2v --first-frame inputs/start.png
open-video run "…" --mode flf2v --first-frame inputs/start.png --last-frame inputs/end.png
```
Frames are staged into the ComfyUI server's own input dir — set
`OPEN_VIDEO_COMFYUI_INPUT` to a directory that belongs to that server.

### Multi-shot film (beyond 15s — experimental director path)
```bash
open-video "a 60-second short film about a lighthouse keeper" --duration 60
```

### Read a video's embedded recipe
Every render embeds its generation recipe in the mp4 metadata. Read it back
with the Python API (there is no `inspect`/`remix` CLI):

```bash
python - <<'PY'
from open_video.core.recipe import read_recipe
print(read_recipe("output/film.mp4"))
PY
```

## Troubleshooting
| Issue | Fix |
|---|---|
| `CUDA out of memory` | Re-run with INT8 + `--lowvram`; W4/NF4 tiers are manual, experimental — not installed by `pull` |
| Download slow | Use aria2c with 16 connections: `aria2c -x16 -s16 <url>` |
| ComfyUI not running | `cd ComfyUI && python main.py --listen --lowvram --use-sage-attention` |
| I2V/FL2V frame not found | Set `OPEN_VIDEO_COMFYUI_INPUT` to the server's own `input/` dir |
| NVFP4 OOM on 5090 | Avoid NVFP4 — use INT8 ConvRot (default) |

## Next steps
- Browse prompts: `open-video list-presets`
- Browse models: `open-video list-models`
- Read the tutorial: `docs/TUTORIAL.md`
- Contribute: `CONTRIBUTING.md`
