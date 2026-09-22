# Changelog

Site: [open-video.ai](https://open-video.ai).

## [0.1.0] — 2026-09-22

Reliability improvements for local MiniMax H3 generation and the agent skill.

### Reliability fixes

- **Recipe-in-render round-trip** — `embed_recipe` / `read_recipe` now round-trip
  with atomic replacement for in-place updates, and stale OpenVideo metadata
  tags are cleared before re-embed, so a re-rendered file never carries the
  previous run's recipe.
- **Integrity-verified weights** — `open-video pull h3` verifies the packaged
  manifest (sizes + checksums) instead of trusting file presence; the manifest
  ships with the package.
- **Engine adapter hardening** — ComfyUI adapter: correct URL encoding and real
  error propagation (engine failures surface as errors, not silent timeouts).
- **I2V / FLF2V staging** — first/last frames are staged under unique names via
  `OPEN_VIDEO_COMFYUI_INPUT`, which must point at a directory that belongs to
  the target ComfyUI server. Concurrent runs no longer clobber each other's
  `firstframe.png` / `lastframe.png`.
- **Honest judge** — without `OPEN_VIDEO_VLM_URL` + `OPEN_VIDEO_VLM_MODEL` (or an
  explicit `vision_fn`), shot verdicts are now reported as `SKIPPED` (score 0)
  instead of a silent PASS stub. Real VLM callbacks stay strictly opt-in.
- **Judge retries and receipts** — `OPEN_VIDEO_JUDGE_RETRIES` sets the number of
  extra takes (default 1); the best take's seed and per-take history are kept in
  the JSON receipt. A failed requested shot stops the run without reporting a
  partial film as complete.
- **Portrait generation** — `--aspect 9:16` now reaches the backend's generation
  settings; JSON output includes the actual dimensions and take receipts.

### Docs / honesty

- CLI has no `inspect` / `remix` / `--lora` flags — removed from docs. Recipe
  read-back is the Python API: `open_video.core.recipe.read_recipe(path)`.
- Default weights path is **INT8 only**. W4 / NF4 tiers are manual, experimental
  suggestions — never auto-installed.
- Install this version from the GitHub tag (`git clone --branch v0.1.0`).
  The website installer is updated separately and may serve an older version.

### Still not shipped

- Long-film director stays **experimental** (`skill/open-video`); generation
  requires an NVIDIA GPU runtime.
- Native Windows execution and an independent visual review of a multi-shot
  demo remain unverified. See the release notes for the recorded acceptance checks.

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
