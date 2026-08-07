<p align="center">
  <img src="https://open-video.ai/logo.svg" width="110" height="110" alt="OpenVideo" />
</p>

<h1 align="center">OpenVideo</h1>

<p align="center">
  <strong>OpenVideo</strong> — open-source video generation.<br/>
  <sub>v0.0.1: local MiniMax H3 (Ollama-style) + agent skill harness — any agent, high-quality video on your GPU.</sub>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-blue.svg"/></a>
  <img alt="Version" src="https://img.shields.io/badge/version-0.0.1-informational.svg"/>
  <a href="https://open-video.ai"><img alt="Website" src="https://img.shields.io/website?url=https%3A%2F%2Fopen-video.ai&label=open-video.ai"/></a>
  <a href="https://huggingface.co/open-video-ai"><img alt="Hugging Face" src="https://img.shields.io/badge/HuggingFace-open--video--ai-yellow.svg"/></a>
  <a href="https://huggingface.co/spaces/ArtificialAnalysis/Video-Generation-Arena"><img alt="H3 Arena" src="https://img.shields.io/badge/H3-Arena%20%231%20open-FBBF24.svg"/></a>
</p>

<p align="center">
  <sub><b>OpenCode&nbsp;→&nbsp;Cursor.&nbsp;&nbsp;Open&nbsp;Design&nbsp;→&nbsp;Claude&nbsp;Design.&nbsp;&nbsp;OpenVideo&nbsp;→&nbsp;Runway.</b></sub><br/>
  <sub><b>OpenVideo</b> v0.0.1: <code>pull</code> · <code>run</code> · <b>skill harness</b> for MiniMax H3 — not the full multi-model platform yet.</sub>
</p>

---

Brand: [`BRAND.md`](BRAND.md) · Design: [`DESIGN.md`](DESIGN.md) · Copy: [`docs/PUBLIC_COPY.md`](docs/PUBLIC_COPY.md).

**Primary CTA is Install** (site + CLI). Source lives at
[`open-video-ai/open-video`](https://github.com/open-video-ai/open-video) — use the install
path below; clone when the org opens the tree for contributors.

## What v0.0.1 is

| | |
|---|---|
| **Product** | **OpenVideo** — open-source video generation |
| **Agent path** | Drop-in **skill harness** (`skill/h3-video`) so Claude Code / Cursor / Codex / any agent host can craft official 3-field prompts and generate **high-quality** H3 clips |
| **Model** | MiniMax H3 via ComfyUI (local GPU) |
| **Not yet (later releases)** | Multi-model backends, cloud Studio, 100+ gallery, long-film director polish |

```text
  Human or Agent
        │
        ▼
  skill/h3-video  ──or──  open-video CLI
        │
        ▼
  pull h3 → status → craft prompt → run → mp4
        │
        ▼
  ComfyUI + MiniMax H3 (local)
```

Site: [open-video.ai](https://open-video.ai) · demo: [demo.mp4](https://open-video.ai/demo.mp4)

## Why this release

Closed tools charge per second and lock models. Open **H3** already has Arena-tier quality —
what's missing for agents and builders is a **simple local loop**: install → pull → run, plus a
**skill** that encodes best-practice prompting so quality is not left to chance.

v0.0.1 is that loop. Full multi-shot director / multi-model platform is the road ahead.

## Install + generate (OpenVideo CLI)

```bash
# Linux / macOS — install engine + pull H3 weights (resumable ~54 GB)
curl -fsSL https://open-video.ai/install | bash

# Windows (PowerShell) — prefers WSL2 for full H3 GPU path
irm https://open-video.ai/install.ps1 | iex

# Same mental model as Ollama: pull → status → run
open-video pull h3                  # verify / resume H3 weights
open-video status                   # ComfyUI health + weight inventory (alias: ps)
open-video recommend-quant          # resource-aware quant (nf4 / w4 / int8)

open-video run "A lone astronaut planting a flag on a red dune at dusk" --duration 8
open-video "sunset waves" --dry-run # plan + validate without GPU
```

| OS | Install | Generate |
|---|---|---|
| **Linux** | `curl …/install \| bash` | NVIDIA GPU · full H3 |
| **macOS** | same curl (setup + dry-run) | H3 gen community/MLX; not default |
| **Windows** | `irm …/install.ps1 \| iex` | **WSL2** for H3 GPU; native dry-run OK |

**Local-first.** Bring your own NVIDIA GPU. Weights ~54 GB (resumable pull).

### Agent harness (any agent host)

Point your agent at the skill — it will install/pull if needed, craft the **official H3 3-field
prompt**, validate, generate, and review:

| Skill | Use when |
|---|---|
| **[`skill/h3-video/SKILL.md`](skill/h3-video/SKILL.md)** | **v0.0.1 default** — high-quality single/short H3 clips (T2V / I2V / FL2VA) |
| [`skill/open-video/SKILL.md`](skill/open-video/SKILL.md) | Longer director path (plan → judge → stitch) — evolving |

Works with Claude Code, Cursor, Codex, OpenCode, and any host that loads `SKILL.md`.

<details>
<summary><b>Prefer manual clone?</b></summary>

```bash
git clone https://github.com/open-video-ai/open-video && cd open-video
pip install -e .
open-video pull h3
open-video run "waves at sunset, golden hour" --duration 10 --model h3 --output out.mp4
# ComfyUI at http://127.0.0.1:8188 (env OPEN_VIDEO_COMFYUI)
```

</details>

## Three ways to use it (v0.0.1)

| Interface | For | Experience |
|---|---|---|
| 🤖 **Skill harness** | **Any agent** | Load `skill/h3-video` → agent generates high-quality H3 video end-to-end |
| ⌨️ **CLI** | Developers / scripts | `open-video pull` · `status` · `run` (Ollama-shaped) |
| 🖥️ **Site** | Discovery | [open-video.ai](https://open-video.ai) — install + docs UI (product site repo) |

## The quality loop (the part no open project has)

```
   generate ──→ judge ──→ refine ──→ best-of-N ──↻ repeat until it clears the bar
                  │
                  └─ a vision model scores every shot vs. your intent + a quality bar.
                     Below bar → diagnose → targeted fix → regenerate. Only the best take ships.
```

This loop — proven by Google VISTA (+46.3% win rate) and VideoWeaver — is what turns a
single-shot open model (≤15s) into a **coherent multi-minute film**. Closed products
(Seedance, Sora) ship this layer internally. **OpenVideo ships it open.**

## Why open beats closed

| | Open | Closed (Runway / Seedance / Sora) |
|---|---|---|
| **Quality** | H3 = Arena parity with #1 closed | Reference ceiling |
| **Cost** | Free locally; cheap SaaS optional | $0.50–$2+/second |
| **Ownership** | Your models, your prompts, your data | Vendor lock-in, region bans |
| **Longevity** | Model-agnostic core survives churn | Model changes when they say |
| **Community** | Shared prompts, LoRAs, reference-packs (a moat they can't match) | Internal know-how |

## How it compares

| | What | Open? | Long-film agent | Quality loop | Notes |
|---|---|:--:|:--:|:--:|---|
| **OpenVideo** | Director agent on ComfyUI + open models | ✅ Apache-2.0 | ✅ | ✅ judge→refine→best-of-N | **this project** |
| **Runway** | Closed SaaS, Gen-4 | ❌ | ✅ | internal | the brand to beat |
| **Seedance 2.x** | Closed, native 180s agent | ❌ | ✅ native | internal | the closed target we match |
| **OpenMontage** | Open editor, 45K★ | ✅ | ❌ | ❌ | great editor, no director brain |
| **ComfyUI** | Node-graph engine, 124K★ | ✅ GPL | ❌ | ❌ | **our partner** — we drive it, not replace it |

> OpenVideo isn't a model (H3/Wan/LTX are backends) and isn't an engine (ComfyUI is). It's the
> **agent brain** those layers lack.

## Community

PRs welcome once the source tree is open for contributors — see [`CONTRIBUTING.md`](CONTRIBUTING.md).
Chat/Discord may land later; until then use GitHub Issues on this repo.

**OpenVideo is a plugin platform — contribute what you're good at:**

| You have | Contribute → | Effort |
|---|---|---|
| A great prompt | `library/prompts/` — a verified recipe | 5 min |
| A turnaround / lighting board | `library/reference_packs/` — identity consistency | 15 min |
| A new model (Wan 2.2, Hunyuan, LTX) | `backends/<model>/` — a backend plugin | an afternoon |
| A scoring method / vision judge | `judges/` — a judge plugin | an afternoon |
| A new engine (diffusers, SGLang) | `engines/<engine>/` — an adapter | an afternoon |
| A style LoRA | `library/style_profiles/` — share it | 10 min |

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for templates and [`GOVERNANCE.md`](GOVERNANCE.md) for
how decisions get made. **We integrate, we don't reinvent** — if a working project already does
it, we wrap it as a plugin.

## Architecture

```
concept ──→ [core: planner]   ── coherence bible (acts → scenes → ≤15s shots)
           [core: crafter]    ── model-specific 3-field prompts
           [core: validator]  ── hard-gate (duration / refs / dialogue / timeline)
           [backends/<model>] ── generate shot (via engines/<engine>)  ── FL2VA chain
           [core: judge]      ── vision-assess vs intent + quality bar  ── refine ↻
           [core: stitcher]   ── concat + audio continuity + 2K upscale (opt)
                              ── delivered multi-minute film + per-shot receipts
```

- **`core/`** — model-agnostic brain: planner, crafter, validator, judge-loop, stitcher, selector.
- **`backends/<model>/`** — one plugin per open model. H3 today; Wan 2.2 / Hunyuan / LTX next.
- **`engines/<engine>/`** — adapters. ComfyUI today (via its HTTP API); diffusers/SGLang later.
- **`interfaces/`** — `skill/` (SKILL.md), `cli/` (`open-video`), web app (planned).

Add a model = write a backend. Add an engine = write an adapter. **The core never changes.**
Full design in [`ARCHITECTURE.md`](ARCHITECTURE.md); roadmap + open decisions in
[`PLAN.md`](PLAN.md).

## Status & roadmap

**v0 / planning** — H3 backend + ComfyUI adapter + core loop, proving the thesis: an open,
vision-judged, multi-minute film that holds up next to a Seedance short.

- **Phase 0 — thesis proof:** a real 1–5 min open film, judge-verified coherent.
- **Phase 1 — open + community:** `library/` flywheel, Discord, a 2nd backend (Wan 2.2) to prove
  model-agnostic, prompt gallery at `open-video.ai/gallery`.
- **Phase 2 — hosted:** managed SaaS/API (bring-your-key or our GPUs) + enterprise license.
- **Phase 3 — marketplace:** premium coherence-recipes, style LoRAs, reference-packs.

## Acknowledgments

Standing on the shoulders of open giants: **[ComfyUI](https://github.com/comfyanonymous/ComfyUI)**
(engine, 124K★), **[MiniMax H3](https://huggingface.co/MiniMaxAI)** (baseline model), the
**[woodfantasy](https://github.com/woodfantasy)** prompt methodology (MIT-0), and
**[VideoScore](https://github.com/TIGER-AI-Lab/VideoScore)** (judge). We integrate, not reinvent.

## License

[Apache-2.0](LICENSE) © OpenVideo contributors. Built in the open at **[open-video.ai](https://open-video.ai)**.

---

<p align="center"><sub>OpenVideo · open-video.ai · 100K★ north star — the #1 open video community.</sub></p>

## Security

Please see [SECURITY.md](SECURITY.md) for private vulnerability reporting.

## Repos

Core · site · ops map: [REPOS.md](REPOS.md). Public release checklist: [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md).
