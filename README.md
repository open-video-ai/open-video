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

## What works today vs what is designed next

| | v0.0.1 (shipped) | Designed (not default yet) |
|---|---|---|
| **Generate** | Local MiniMax H3 via ComfyUI — `pull` / `status` / `run` | Multi-model backends (Wan, etc.) |
| **Agent path** | `skill/h3-video` crafts official prompts + drives CLI | Full multi-shot director agent |
| **Judge loop** | Scaffold in `core/judge.py` (PASS stub without a vision fn) | Vision score → refine → best-of-N |
| **Long film** | Single clips (H3 shot length) | Planner → stitch multi-minute film |
| **Hosted try** | Site is install + docs; `/try` is a **browser mockup** | Real free/paid GPU generate |

The **generate → judge → refine** loop is the long-term design (same class of idea as
VISTA / VideoWeaver-style refine). It is **not** a live vision judge in v0.0.1 — do not treat
README architecture diagrams as “already ships multi-minute judged film.”

## Local vs closed SaaS (facts only)

| | OpenVideo (local) | Typical closed SaaS |
|---|---|---|
| **Model** | MiniMax H3 (open weights; Arena #1 open — see model card / Arena) | Vendor-hosted only |
| **Cost** | Your GPU + electricity | Per-second API / subscription |
| **Data** | Stays on your machine | Vendor pipeline |
| **License** | Apache-2.0 software | ToS / region limits |

## How it compares (honest)

| | What | Open software? | Local open model? | Notes |
|---|---|:--:|:--:|---|
| **OpenVideo** | CLI + skill + H3 on ComfyUI (v0.0.1) | ✅ Apache-2.0 | ✅ H3 | **this project** — director/judge loop is scaffolding |
| **Runway** | Closed SaaS | ❌ | ❌ | Hosted product |
| **Seedance** | Closed agentic long video | ❌ | ❌ | Hosted product |
| **OpenMontage** | Open editor | ✅ | n/a | Editor, not a local H3 pull/run path |
| **ComfyUI** | Node-graph engine | ✅ GPL | via custom nodes | **Runtime we drive** — not a competitor to replace |

> OpenVideo is not a foundation model and not a replacement for ComfyUI. v0.0.1 is the
> **install → pull → run** layer plus an agent skill on top of H3.

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

## Architecture (v0.0.1 + design target)

**Shipped path:**

```
prompt / skill ──→ open-video CLI ──→ backends/h3 ──→ engines/comfyui ──→ mp4
```

**Design target** (modules exist or are sketched; not all wired end-to-end):

```
concept ──→ planner → crafter → validator → backend → judge → stitcher → film
```

- **`backends/h3/`** — MiniMax H3 (baseline).
- **`engines/comfyui/`** — ComfyUI HTTP adapter.
- **`skill/h3-video`** — agent harness for prompts + generate.
- **`core/`** — shared types + judge/planner scaffolding for later phases.

Full design notes: [`ARCHITECTURE.md`](ARCHITECTURE.md). Short public roadmap: below.
Internal planning detail lives in the private ops repo, not in star-count vanity on this README.

## Status & roadmap

**v0.0.1 — shipped:** local H3 pull/run, skill harness, install path, product site.

- **Next:** real vision judge wiring, multi-shot continuity, 2nd backend, contributor gallery when ready.
- **Later (maybe):** hosted generate, desktop packaging, marketplace-style sharing — only when real.

## Acknowledgments

Standing on the shoulders of open giants: **[ComfyUI](https://github.com/comfyanonymous/ComfyUI)**
(engine, 124K★), **[MiniMax H3](https://huggingface.co/MiniMaxAI)** (baseline model), the
**[woodfantasy](https://github.com/woodfantasy)** prompt methodology (MIT-0), and
**[VideoScore](https://github.com/TIGER-AI-Lab/VideoScore)** (judge). We integrate, not reinvent.

## License

[Apache-2.0](LICENSE) © OpenVideo contributors. Built in the open at **[open-video.ai](https://open-video.ai)**.

---

<p align="center"><sub>OpenVideo · open-video.ai · Apache-2.0</sub></p>

## Security

Please see [SECURITY.md](SECURITY.md) for private vulnerability reporting.

## Repos

Core · site · ops map: [REPOS.md](REPOS.md). Public release checklist: [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md).
