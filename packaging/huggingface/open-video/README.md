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
  - ollama
  - local-first
  - skill
pipeline_tag: text-to-video
---

# OpenVideo · v0.0.1

## Scope (this release)

> **Ollama for MiniMax H3 + agent skill harness.**  
> Any coding agent (Claude Code, Cursor, Codex, OpenCode, …) can install, pull, and generate **high-quality local video**.

| | |
|---|---|
| **Website** | https://open-video.ai |
| **GitHub** | https://github.com/open-video-ai/open-video |
| **HF org** | https://huggingface.co/open-video-ai |
| **License (code)** | Apache-2.0 |
| **Version** | **0.0.1** |

```text
Agent or human → skill/h3-video or CLI → pull h3 → run → mp4
                      ↓
              ComfyUI + MiniMax H3 (your GPU)
```

This Hub page is a **software card**. It does **not** re-host H3 weights (~54 GB). The installer pulls upstream quants (Comfy-Org / ModelScope).

## Install (Ollama-style)

```bash
curl -fsSL https://open-video.ai/install | bash

open-video pull h3
open-video status
open-video run "a red panda in mist" --duration 5
```

## Agent harness

Copy or load from the repo:

- **[`skill/h3-video/SKILL.md`](https://github.com/open-video-ai/open-video/blob/master/skill/h3-video/SKILL.md)** — default for v0.0.1 (high-quality H3 clips)
- Official 3-field grammar: `backends/h3/PROMPT_GRAMMAR.md`

The skill tells the agent to: check `status` → craft prompt correctly → `run` → review output.

## What v0.0.1 is / is not

| Is | Is not |
|---|---|
| Ollama-like local H3 loop | Multi-model platform (later) |
| Skill for **any** agent host | Hosted cloud GPU (roadmap) |
| High-quality prompt path for H3 | Re-upload of MiniMax weights |

## Citation

```bibtex
@software{openvideo_0_0_1,
  title  = {OpenVideo},
  year   = {2026},
  url    = {https://github.com/open-video-ai/open-video},
  note   = {v0.0.1 — Ollama for H3 + agent skill harness}
}
```
