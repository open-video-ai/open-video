# Changelog

Site: [`open-video-web`](https://github.com/open-video-ai/open-video-web). Ops: private `open-video-ops`.

## [0.0.1] — 2026-08-07

**First release line** — Ollama for MiniMax H3.

### Added
- CLI: `pull` / `run` / `status`/`ps` / `list` / `recommend-quant` / dry-run generate
- H3 backend + ComfyUI adapter + skill harnesses (`skill/h3-video`, `skill/open-video`)
- Installer (`scripts/install.sh`) + Pages host on open-video.ai
- Library prompts + coherence recipes
- Tests + GitHub CI / SECURITY / release templates
- Hugging Face software card + prompts dataset packaging (`packaging/huggingface/`)

### Hub
- HF org: https://huggingface.co/open-video-ai  
- Software card (bootstrap): https://huggingface.co/fei567/open-video → transfer to `open-video-ai/open-video` when org write is enabled  
- Publish script: `packaging/huggingface/publish.sh`

### Known limitations
- Judge / planner early; no cloud Studio in this tag
- Weights not shipped (pull upstream ~54 GB)
- GitHub may remain private until owner opens

## Unreleased
- Gallery / cloud generation (site product)
