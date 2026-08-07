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
  - open-video
pipeline_tag: text-to-video
---

# OpenVideo · v0.0.1

**OpenVideo** is open-source video generation.

v0.0.1 focuses on **local MiniMax H3**: Ollama-style install/CLI (`pull` · `run` · `status`) and a **skill harness** so any agent can generate high-quality video on your GPU.

| | |
|---|---|
| **Product** | OpenVideo |
| **Code** | open-video |
| **Website** | https://open-video.ai |
| **GitHub** | https://github.com/open-video-ai/open-video |
| **License (code)** | Apache-2.0 |

```bash
curl -fsSL https://open-video.ai/install | bash
open-video pull h3
open-video run "a red panda in mist" --duration 5
```

Agent: load `skill/h3-video/SKILL.md` from the repo.

This Hub card is software documentation — it does not re-host H3 weights (~54 GB; pulled upstream by the installer).
