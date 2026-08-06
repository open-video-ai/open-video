# Reference products — what OpenVideo steals (and what it doesn't)

> Living map of the projects we deliberately **refer to** when designing the product, site, and go-to-market.
> Update numbers before press; Elo and star counts drift.

## Canonical references

| Project | URL | Repo | Role for OpenVideo |
|---|---|---|---|
| **OpenCode** | [opencode.ai](https://opencode.ai/) | [anomalyco/opencode](https://github.com/anomalyco/opencode) (aka sst lineage) | **Business DNA + install UX.** Open AI coding agent; multi-surface (TUI / desktop / IDE); `curl …/install \| bash`; model-agnostic open brain. |
| **Open Design** | [open-design.ai](https://open-design.ai/) | [nexu-io/open-design](https://github.com/nexu-io/open-design) | **Local-first agent product pattern.** Open-source Claude Design alternative; desktop + skills + MCP; Apache-2.0; “one system, many surfaces”; official brand page. |
| **OpenArt** | [openart.ai](https://openart.ai/) | [OpenArt-AI](https://github.com/OpenArt-AI) (partial) | **Product DNA.** Polished creator studio; gallery / models / free start; “for everyone,” not just node-graph engineers. |
| **Cursor** | cursor.com | closed | Closed **code** incumbent in the analogy. |
| **Runway / Seedance** | runwayml.com / seedance | closed | Closed **video** incumbents. Runway = category shorthand; Seedance = technical peer for long-film agent. |

## The family analogy (site + pitch)

| Domain | Closed product | Open alternative | What the open layer is |
|---|---|---|---|
| **Code** | Cursor | **OpenCode** | Open coding *agent* on any model |
| **Design** | Claude Design / closed design agents | **Open Design** | Open design *workspace* driven by local agents |
| **Video** | Runway / Seedance | **OpenVideo** | Open video *director* on ComfyUI + open models (H3) |

One-liner (from `POSITIONING.md`):

> **OpenCode → Cursor. Open Design → Claude Design. OpenVideo → Runway.**

## Patterns we copy

### From OpenCode
- Ultra-clear H1: *what it is in one breath* (“The open source AI coding agent”).
- **One install command** on the site + docs: `curl -fsSL https://opencode.ai/install | bash`.
- Multi-surface: terminal · desktop · IDE (for us: App · CLI · Skill).
- Model-agnostic framing (we swap video backends, not only LLMs).
- Social proof block when numbers are real (stars / contributors / users).

### From Open Design
- **“Open-source X alternative”** SEO + hero clarity ([open-design.ai](https://open-design.ai/)).
- Local-first desktop + agent hosts (Claude Code, Codex, Cursor, OpenCode, …).
- Apache-2.0, free local use, optional cloud/pricing later.
- Dedicated **Download / Install / Docs / Official naming** surfaces.
- Skills / MCP packaging so agents consume the product natively.

### From OpenArt
- Ship a **product**, not a node-graph manual.
- Gallery + models library + “start free” as the first click.
- Creator language (story, brand, character) over researcher jargon.
- Presets and one-shot success paths for non-developers.

## Patterns we deliberately do **not** copy

| Source | Pattern | Why not |
|---|---|---|
| OpenArt | All-modality studio (image + video + audio + music as equals) | OpenVideo is **video-only** (native audio with the clip is in-scope; standalone image/music is out). See `POSITIONING.md` §4. |
| OpenArt | Hosted-only / credit economy as the default | We are **local-first**; hosted is phase-2 open-core, not the core identity. |
| Closed Runway | Black-box API, per-second metering as the only path | We lead with ownership, no region lock, no watermark. |
| Generic “AI studio” | Feature soup | Focus: director loop (plan → craft → generate → judge → refine → stitch). |

## Install UX parity (must match OpenCode / Open Design)

| Surface | OpenCode | Open Design | OpenVideo |
|---|---|---|---|
| One-liner | `curl -fsSL https://opencode.ai/install \| bash` | `curl -fsSL https://open-design.ai/install.sh \| sh` | `curl -fsSL https://open-video.ai/install \| bash` |
| Docs | opencode.ai/docs | open-design.ai (docs in product) | open-video.ai/docs |
| Desktop | Download page | open-design.ai/download | App *planned* (CLI + Try mockup first) |
| Agent skill | — | Skills + MCP for coding agents | `skill/open-video/SKILL.md` for Claude/Cursor/MCP |

## Repo / brand hygiene (from Open Design “official”)

- **Canonical site:** `https://open-video.ai`
- **Canonical code:** prefer one public GitHub path (today: `robotlearning123/open-video`; target org: `open-video` / `open-video-ai` when secured).
- Names that all mean this project: **OpenVideo**, **open-video**, **open-video.ai**.
- Avoid linking to dead orgs (`open-video-ai/...` before the org exists) or foreign Pages projects (`open-video.pages.dev` name collision).

## How to use this doc

1. **Website copy** — hero, analogy strip, install, three interfaces: follow OpenCode + Open Design clarity.
2. **README** — OpenCode-style badges + one-liner install + analogy subhead.
3. **Pitch / HN / Reddit** — OpenArt product story + OpenCode open-core story; never “we’re a ComfyUI wrapper.”
4. **Roadmap** — desktop download page (Open Design), gallery (OpenArt), hosted tier (OpenCode).

## Sources checked (2026-08-06)

- https://open-design.ai/ · https://open-design.ai/download/ · https://github.com/nexu-io/open-design  
- https://opencode.ai/ · https://opencode.ai/docs/ · https://github.com/sst/opencode / anomalyco  
- https://openart.ai/ · https://github.com/OpenArt-AI  
- Local: `docs/POSITIONING.md`, `README.md`, `website/`
