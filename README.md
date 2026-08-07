<p align="center">
  <img src="website/logo.svg" width="110" height="110" alt="OpenVideo" />
</p>

<h1 align="center">OpenVideo</h1>

<p align="center">
  <strong>The open-source video generation platform — Ollama for video.</strong><br/>
  From concept to finished film, for everyone.
</p>

<p align="center">
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-blue.svg"/></a>
  <a href="https://github.com/robotlearning123/open-video/stargazers"><img alt="GitHub Stars" src="https://img.shields.io/github/stars/open-video-ai/open-video?style=social"/></a>
  <a href="https://discord.gg/open-video"><img alt="Discord" src="https://img.shields.io/discord/0?style=social&logo=discord&label=Discord&color=5865F2"/></a>
  <a href="https://open-video.ai"><img alt="Website" src="https://img.shields.io/website?url=https%3A%2F%2Fopen-video.ai&label=open-video.ai"/></a>
  <a href="https://huggingface.co/spaces/ArtificialAnalysis/Video-Generation-Arena"><img alt="H3 Arena" src="https://img.shields.io/badge/H3-Arena%20%231%20open-FBBF24.svg"/></a>
</p>

<p align="center">
  <sub><b>OpenCode&nbsp;→&nbsp;Cursor.&nbsp;&nbsp;Open&nbsp;Design&nbsp;→&nbsp;Claude&nbsp;Design.&nbsp;&nbsp;OpenVideo&nbsp;→&nbsp;Runway.</b></sub><br/>
  <sub>One open director brain that turns open video models into a finished film — local, free, and yours.</sub>
</p>

---

<p align="center">
  <video controls width="100%" src="website/demo.mp4" poster="website/logo.svg">
    Demo film — open this file on GitHub, or view it locally at <code>website/demo.mp4</code>.
  </video>
</p>
<p align="center"><sub>A concept → a coherent, multi-shot film. Live demo: <a href="https://open-video.ai">open-video.ai</a>.</sub></p>

---

## References (OpenCode · Open Design · OpenArt)

We deliberately mirror sibling open products:

| Project | Domain | Closed peer |
|---|---|---|
| [OpenCode](https://opencode.ai/) | Code agent | Cursor |
| [Open Design](https://open-design.ai/) | Design workspace | Claude Design |
| [OpenArt](https://openart.ai/) | Creator studio DNA | (product polish) |
| **OpenVideo** | **Video director** | **Runway / Seedance** |

Details: [`docs/REFERENCES.md`](docs/REFERENCES.md) · positioning: [`docs/POSITIONING.md`](docs/POSITIONING.md).

## Why OpenVideo

Closed video tools sell you a black box: per-second fees, region locks, watermarks, and a model
that changes when the vendor says so. **Open models already closed the quality gap** —
[**MiniMax H3**](https://huggingface.co/MiniMaxAI) sits at **Artificial Analysis Arena ([artificialanalysis.ai/video](https://artificialanalysis.ai/video/leaderboard/text-to-video)) T2V #2 /
I2V #3 overall, and #1 open** (Elo 1238 / 1189), within noise of closed #1 (Gemini Omni Flash
1244 / Seedance 1197). The raw quality is there. **What's missing is the director.**

OpenVideo is that director — the **autonomous agent layer** no open engine ships natively. It
plans, crafts prompts, validates, judges, refines, stitches, and delivers. You get **Runway-grade
results on hardware you own, with models you control.**

## One-command quickstart

```bash
# Linux / macOS (Ollama-style one-liner)
curl -fsSL https://open-video.ai/install | bash

# Windows (PowerShell) — prefers WSL2 for full H3 GPU path
irm https://open-video.ai/install.ps1 | iex

# Then generate (one prompt → video). Dry-run validates without GPU:
open-video "A lone astronaut planting a flag on a red dune at dusk" --duration 8
open-video "sunset waves" --dry-run
open-video recommend-quant          # resource-aware H3 quant (nf4/w4/int8)
```

| OS | Install | Generate |
|---|---|---|
| **Linux** | `curl …/install \| bash` | NVIDIA GPU · full H3 |
| **macOS** | same curl (setup + dry-run) | H3 gen community/MLX; not default |
| **Windows** | `irm …/install.ps1 \| iex` | **WSL2** for H3 GPU; native dry-run OK |


That's it. OpenVideo plans the film, generates each shot, judges every frame, refines the weak
ones, stitches the cuts, and hands you `output/film.mp4`. **Local-first by default; bring your
own GPU or run on our managed cloud.**

<details>
<summary><b>Prefer manual?</b></summary>

```bash
git clone https://github.com/robotlearning123/open-video && cd open-video
python cli/open_video.py "waves at sunset, golden hour" --duration 10 --model h3 --output out.mp4
# requires a running ComfyUI at http://127.0.0.1:8188 (OPEN_VIDEO_COMFYUI=...)
```

</details>

## Three ways to use it

| Interface | For | Experience |
|---|---|---|
| 🖥️ **App** *(primary)* | Everyone — creators, PMs, non-technical users | Natural language → video. Storyboard preview, presets, one-click render. Like ChatGPT for film. |
| ⌨️ **CLI / API** | Developers | `open-video "concept" --duration 300` or REST. Automate, integrate, build on top. |
| 🤖 **Skill** | Agent hosts (Claude Code, Cursor, MCP) | Drop-in `SKILL.md` — let any agent direct video end-to-end, fully autonomous. |

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

<p>
  <a href="https://discord.gg/open-video"><img alt="Discord" src="https://img.shields.io/discord/0?style=for-the-badge&logo=discord&label=Join%20Discord&color=5865F2"/></a>
  &nbsp;
  <a href="CONTRIBUTING.md"><img alt="Contributing" src="https://img.shields.io/badge/PRs-welcome-FBBF24.svg"/></a>
</p>

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

<p align="center"><sub>★ Star this repo to follow the build. ⭐ 100K★ north star — the #1 open video community.</sub></p>
