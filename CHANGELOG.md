# Changelog

All notable changes to **open-video** (core) are documented here.  
Site changes: see [`open-video-web`](https://github.com/open-video-ai/open-video-web).  
Internal strategy: private `open-video-ops` only.

Format inspired by [Keep a Changelog](https://keepachangelog.com/). Versioning aims at [SemVer](https://semver.org/) with pre-release tags (`a`/`b`/`rc`).

## [0.1.0a1] — 2026-08-07

First release-candidate line for public open source (**Ollama for MiniMax H3**).

### Added
- CLI surface aligned with Ollama: `pull`, `run`, `status`/`ps`, `list`, `recommend-quant`, default generate
- `core/h3_weights.py` — verified INT8 package inventory (resumable pull via installer)
- `core/resources.py` — VRAM-aware quant recommendation (nf4 / w4 / int8)
- Skill harnesses: `skill/h3-video` (H3/Ollama) + `skill/open-video` (director)
- One-click installer `scripts/install.sh` (+ PowerShell) hosted on open-video.ai
- Plugin architecture: `ModelBackend`, ComfyUI engine adapter, H3 backend + workflows
- Library: prompt recipes + coherence recipe YAML presets
- Tests: backend, pipeline, validator, resources, h3_weights, install policy
- GitHub: CI, release-on-tag, Dependabot, issue/PR templates, SECURITY.md

### Changed
- Product website moved to private repo `open-video-web` (three-repo layout)
- Canonical GitHub org: `open-video-ai`

### Known limitations (honest)
- Quality judge is v0 (stub / partial) — vision wiring is ongoing
- Planner prompts are template-level without full LLM crafter by default
- Cloud Studio / 100+ gallery are site/product roadmap, not this core tag
- End-to-end GPU generation tests are lab-only (not in CI)
- Model weights are third-party (~54 GB); not shipped in git

### Verified in lab
- Unit tests: `pytest tests/` green
- Dry-run CLI path without GPU
- Weight inventory against known H3 INT8 tree

## [0.0.1] — 2026-08-06

Initial private scaffold: core modules, H3 backend, installer prototype, docs skeleton.
