# Local GPU runtime (lab)

Official product: this repo (`open-video-ai/open-video`).  
ComfyUI + MiniMax H3 weights are **not** in git. Keep them in a sibling **lab** directory (or any path you set via env).

## Recommended layout

```text
some-parent/
├── open-video/     ← THIS git repo (code)
└── lab/            ← runtime only (not published in git)
    ├── ComfyUI/
    ├── h3_models/  (~51 GB INT8 package)
    ├── venv/       # optional Comfy Python
    └── inputs/
```

Site and private maintainer ops, if you clone them, are separate repos — not required to generate video.

## Environment

| Variable | Default | Meaning |
|---|---|---|
| `OPEN_VIDEO_ROOT` | this repo | Product checkout |
| `OPEN_VIDEO_LAB` | `../lab` | Runtime root |
| `OPEN_VIDEO_MODELS` | `$OPEN_VIDEO_LAB/h3_models` | Weight files |
| `OPEN_VIDEO_COMFYUI` | `http://127.0.0.1:8188` | HTTP API |
| `OPEN_VIDEO_COMFY_PYTHON` | (optional) | Python that runs ComfyUI |

## Prefer product surfaces

| Surface | Role |
|---|---|
| `open-video pull \| status \| run` | Users and scripts |
| `skill/h3-video` | Agents (prompt craft + generate) |
| `docs/h3/*` | Prompt / bench / practices in **this** repo |
| `scripts/h3_agent.py` | Optional advanced harness |

## Notes

- Never commit weights, ComfyUI clones, or `.env` files.
- Do not hardcode machine-absolute paths; use env vars or paths relative to the checkout.
- Weight license (MiniMax H3 Community) is separate from this software’s Apache-2.0.
