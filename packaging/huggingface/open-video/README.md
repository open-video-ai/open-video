---
license: apache-2.0
library_name: open-video
tags:
  - video-generation
  - text-to-video
  - image-to-video
  - comfyui
  - minimax-h3
  - open-source
  - agent
  - local-first
pipeline_tag: text-to-video
---

# OpenVideo · v0.0.1

**Ollama for video** — open-source director layer on [ComfyUI](https://github.com/comfyanonymous/ComfyUI) + open models (baseline: **MiniMax H3**).

| | |
|---|---|
| **Website** | https://open-video.ai |
| **GitHub** | https://github.com/open-video-ai/open-video |
| **Org (HF)** | https://huggingface.co/open-video-ai |
| **License (code)** | Apache-2.0 |
| **Version** | **0.0.1** (first release line) |

> OpenCode → Cursor · Open Design → Claude Design · **OpenVideo → Runway**

This Hub page is the **software / integration card**. It does **not** re-host MiniMax H3 weights (~54 GB). Weights are pulled by the installer from upstream (e.g. Comfy-Org / ModelScope) — see install docs.

## Install (Ollama-style)

```bash
curl -fsSL https://open-video.ai/install | bash

open-video pull h3
open-video status
open-video run "a red panda in mist" --duration 5
open-video "sunset waves" --dry-run   # no GPU
```

Windows: `irm https://open-video.ai/install.ps1 | iex` (WSL2 for full H3 GPU).

## What v0.0.1 includes

- CLI: `pull` / `run` / `status` / `recommend-quant` / dry-run generate
- H3 backend + ComfyUI engine adapter
- Skill harnesses for agents (`skill/h3-video`, `skill/open-video`)
- Prompt library + coherence recipe YAML presets
- Unit tests (no GPU required in CI)

## What it is not

- Not a re-upload of MiniMax / Comfy-Org weight files
- Not a hosted cloud GPU product (cloud Studio is roadmap)
- Judge / long-film planner still early (honest alpha)

## Upstream models (weights)

Use OpenVideo to **drive** these — do not confuse with this software card:

- MiniMax / Comfy-Org H3 quants (INT8 ConvRot default in installer)
- Future: Wan, LTX, etc. as pluggable backends

## Citation / links

```bibtex
@software{openvideo_0_0_1,
  title  = {OpenVideo},
  year   = {2026},
  url    = {https://github.com/open-video-ai/open-video},
  note   = {Version 0.0.1}
}
```

- Docs: https://open-video.ai/docs  
- Demo film: https://open-video.ai/demo.mp4  
- Security: see `SECURITY.md` on GitHub  

**GitHub may be private during preview** — install one-liner on open-video.ai still works when scripts are hosted on Pages.
