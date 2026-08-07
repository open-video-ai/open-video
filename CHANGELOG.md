# Changelog

Site: [`open-video-web`](https://github.com/open-video-ai/open-video-web).

## [0.0.1] — 2026-08-07

### Scope (locked)

> **Ollama for MiniMax H3 + skill harness — so any agent can generate high-quality local video.**

Not in 0.0.1: multi-model platform, cloud Studio, 100+ gallery productization.

### What ships

| Layer | Delivers |
|---|---|
| **Ollama-shaped CLI** | `pull h3` · `status`/`ps` · `run` · `recommend-quant` · dry-run |
| **Installer** | `curl …/install \| bash` → ComfyUI + resumable H3 weights (~51 GB) |
| **Agent skill harness** | `skill/h3-video` — craft official 3-field prompts, validate, generate, review |
| **H3 backend** | T2V / I2V / FL2VA via ComfyUI adapter |
| **Quality path** | Prompt grammar + hard validator (agent must follow skill; judge loop early) |
| **Packaging** | Apache-2.0 · tests · CI · HF software card packaging |

### Agent contract (v0.0.1)

1. Load [`skill/h3-video/SKILL.md`](skill/h3-video/SKILL.md)
2. Ensure engine + weights (`install` / `pull` / `status`)
3. Craft H3 3-field prompt (`backends/h3/PROMPT_GRAMMAR.md`)
4. `open-video run "…"` or Python `H3Backend.generate`
5. Deliver `mp4` + receipts

### Hub

- HF org: https://huggingface.co/open-video-ai  
- Publish helpers: `packaging/huggingface/publish.sh`

### Known limitations

- Long-film director / judge→refine still early (`skill/open-video`)
- Weights not in git (upstream pull only)
- v0.0.1 is local CLI + skill — not hosted free GPU generate

## Unreleased

- Multi-backend · cloud generate · gallery 100+ · full director polish
