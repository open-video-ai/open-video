# OpenVideo lab runtime

Official product: this repo (`open-video-ai/open-video`).  
Local GPU runtime (ComfyUI + weights) lives **next to** the product under the monorepo-style project folder:

```text
open-video-project/
├── open-video/     ← THIS git repo (code)
├── open-video-web/
├── open-video-ops/
└── lab/            ← runtime only (not published in git)
    ├── ComfyUI/
    ├── h3_models/  (~54 GB)
    └── inputs/
```

## Environment

| Variable | Default | Meaning |
|---|---|---|
| `OPEN_VIDEO_ROOT` | this repo | Product checkout |
| `OPEN_VIDEO_LAB` | `../lab` | Runtime root |
| `OPEN_VIDEO_MODELS` | `$OPEN_VIDEO_LAB/h3_models` | Weight files |
| `OPEN_VIDEO_COMFYUI` | `http://127.0.0.1:8188` | HTTP API |

## Agent / harness scripts (ported from lab)

| Script | Role |
|---|---|
| `scripts/h3_agent.py` | High-quality single-shot agent path |
| `scripts/validate_prompt.py` | 3-field hard gate |
| `scripts/h3_generate_benchmark.py` | Comfy HTTP generate helper |
| `scripts/h3_multishot.py` | Multi-shot plan runner |
| `docs/h3/*` | BEST_PRACTICES, PROMPT_GUIDE, … |

Prefer **OpenVideo CLI** for users: `open-video pull|status|run`.  
Prefer **`scripts/h3_agent.py`** when agents need the battle-tested receipt loop.

## Legacy path

`/mnt/data/workspace/open-video-project/lab` is **deprecated** as a product root; it may keep symlinks into `lab/` for old scripts.
