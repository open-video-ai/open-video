# nexu-io/open-design — Deep-Dive Analysis for OpenVideo

> **Purpose.** A dedicated, evidence-based deep-dive into the largest repo in the OpenVideo
> competitive landscape (`nexu-io/open-design`, 84,180★ as of 2026-08-06). This complements —
> and goes deeper than — the open-design section of `docs/COMPETITOR_DEEP_DIVE.md`. The goal is
> concrete borrow/adapt recommendations, not summary.
>
> All facts verified 2026-08-06 via `gh api repos/nexu-io/open-design`, the `main` README,
> `AGENTS.md`, `docs/architecture.md`, `plugins/spec/SPEC.md`, `design-systems/default/DESIGN.md`,
> and the HeyGen `hyperframes` README. Numbers tagged `(verify)` drift; positioning does not.

---

## 0. Snapshot (verified 2026-08-06)

| Field | Value | Source |
|---|---|---|
| Stars | **84,180** | `gh api` |
| Forks | 9,803 | `gh api` |
| Watchers | 261 | `gh api` |
| Open issues | 799 | `gh api` |
| License | **Apache-2.0** | `gh api` |
| Language | TypeScript (dominant) | `gh api` |
| Created | **2026-04-28** (100 days / ~3.3 months old) | `gh api` |
| Last push | 2026-08-06 (active daily) | `gh api` |
| Homepage | https://open-design.ai (HTTP 200) | `curl` |
| Discord | https://discord.gg/mHAjSMV6gz (HTTP 301 → valid) | `curl` |
| X | @OpenDesignHQ (HTTP 200) | `curl` |
| Latest release | **v0.18.0** (2026-08-05) — "115 PRs · 22 contributors · 2 days" | `gh api releases` |
| Maintainers | @Nagendhra-web, @Sid-Qin, @YOMXXX | README |

**Growth velocity (honest proxy):** 84,180 stars ÷ 100 days = **~842★/day (~25K/month)**. GitHub
REST has no star-history endpoint, so created→now is the only honest linear rate; the trajectory
is nonlinear and almost certainly front-loaded (launch spike), so the *daily average* understates
peak and overstates recent pace. Even halved, this is the fastest-growing repo in the OpenVideo
competitive set.

**Release cadence:** roughly weekly-to-twice-weekly, 2-week patches, each release taglined as a
*product* moment ("Design Team Workspace", "Reliable Delivery", "Sharper Vision, Longer Flow").
18 minor releases in ~14 weeks. This is the single most striking operational signal in the repo.

---

## 1. What Open Design actually is (one-paragraph read)

Open Design (OD) is a **local-first Electron desktop app** — positioned as "the open-source Claude
Design alternative" and "the Figma alternative for the agent era" — whose core trick is to treat
**the coding-agent CLI already on your laptop** (Claude Code, Codex, Cursor, OpenCode, Gemini,
Qwen — **25 distinct executables, 26 runtime defs**) as the rendering engine for a *broad design
studio*: prototypes, decks, dashboards, live artifacts, images, **and video**. Outputs are real
files exported as HTML / PDF / PPTX / MP4 / ZIP / Markdown. The headline positioning quote
(README):

> "Your CLI becomes the design engine, your laptop becomes the studio, and your team's `DESIGN.md`
> becomes the brand contract."

This is a **broad artifact studio, not a video product**. Video is one of seven output surfaces
(`prototype / deck / live-artifact / image / video / hyperframes / audio / design-system` — see
plugin modes, §3). That breadth is the central fact about OD that determines everything below: it
is a complement to OpenVideo, not a peer.

---

## 2. Architecture — how they orchestrate generation

### 2.1 Stack (verified)

| Layer | Technology | Source |
|---|---|---|
| Frontend | Next.js 16 App Router + React 18 + TypeScript | README |
| Daemon | Node 24 · Express · SSE streaming · `better-sqlite3` | README |
| Storage | SQLite (projects / conversations / messages / tabs / templates) | README + AGENTS.md |
| Preview | Sandboxed `srcDoc` iframe, dual-iframe CSS-visibility swap | AGENTS.md |
| Desktop | Electron shell + sandboxed renderer + sidecar IPC | README + AGENTS.md |
| Package mgr | pnpm 10.33 (primary); Bun lockfile secondary | repo |
| Lifecycle | Single entrypoint `pnpm tools-dev` | README |

### 2.2 The orchestration pattern — daemon spawns CLI subprocesses

This is OD's defining architectural choice and the part most worth studying.

```
Browser (Next.js 16 / Electron)
   │  HTTP (/api/*)
   ▼
Local daemon  ───────────────────┐   privileged process, owns:
 (Express + SQLite, 127.0.0.1)   │   • agent spawning & stdin bookkeeping
   │  spawns child process       │   • skills / design-systems / templates
   ▼                             │   • artifacts, projects, files
Coding-agent CLI on PATH         │   • BYOK proxy with SSRF guards
 (Claude / Codex / Cursor …)     │   • MCP stdio server
   │  composes prompt + DESIGN.md│   • plugin state, memory
   ▼                             │
real files (HTML/MP4/PPTX)  ←────┘   sandboxed iframe preview
```

**Key mechanics (verified from `AGENTS.md`):**

- **Agent stdin has two protocols.** Default `promptInputFormat: 'text'` writes the composed
  prompt and closes stdin. **Claude is the only runtime using `'stream-json'`** — the daemon
  wraps the prompt as one JSONL `user` message and *keeps stdin open* so it can stream further
  user messages back in mid-turn. `applyClaudeStreamJsonRunBookkeeping` closes stdin only when a
  `turn_end` (or `usage`) event arrives with a non-`tool_use` `stop_reason`. **Read: OD's entire
  interactivity model is built around Claude Code's stream-JSON semantics.** This is a load-bearing
  coupling that matters for anyone copying the pattern.

- **CLI ↔ Web dual-track.** Every capability is reachable through both the web UI and the `od`
  CLI; both call the *same* `/api/*` endpoints. Subcommands register through `SUBCOMMAND_MAP`.
  The daemon HTTP layer is the single source of truth.

- **Sidecar IPC.** Three packages divide concerns: `packages/sidecar-proto` (constants, schema,
  error shapes), `packages/sidecar` (bootstrap + transport + path resolution), `packages/platform`
  (OS process stamp serialization, command parsing). **Process stamps are exactly five fields:**
  `app, mode, namespace, ipc, source`. POSIX IPC sockets are fixed at
  `/tmp/open-design/ipc/<namespace>/<app>.sock`. Orchestration must call package primitives; no
  hand-built `--od-stamp-*` args.

- **MCP stdio server.** OD ships a stdio MCP server with per-agent install snippets
  (`od mcp install <agent>`). Exposed queries: `od project list --json`, `od files list`,
  `od files read`, `od plugin list --json`, `od skills list --json`. **Read-only by default.**

- **Data directory contract.** `OD_DATA_DIR` resolves once at startup to `RUNTIME_DATA_DIR`.
  Every daemon-owned datum (SQLite DB, MCP config/tokens, plugin state, artifacts, sandbox logs)
  must derive from this root. AGENTS.md explicitly calls out anti-patterns: module-level defaults
  pointing at cwd-relative legacy dirs, `openDatabase(projectRoot)` fallbacks,
  `defaultRegistryRoots()` recomputing from env.

### 2.3 Security boundaries (verified)

- **BYOK proxy with per-target SSRF protection** at `POST /api/proxy/{anthropic,openai,azure,
  google,ollama,senseaudio}/stream`. Blocks internal IPs / link-local / CGNAT at the daemon edge.
  Presets: OpenAI, Atlas Cloud, Anthropic, Azure OpenAI, Gemini, Ollama, LM Studio, vLLM.
- **`OD_ALLOWED_INTERNAL_HOSTS`** — strict opt-in, exact-host matching (no subdomain/substring/
  CIDR) for VPN-only endpoints like LiteLLM or Ollama on `10.x` / `192.168.x`.
- **`OD_BIND_HOST` + `OD_ALLOWED_ORIGINS`** — daemon binds `127.0.0.1` by default; LAN exposure
  requires explicit opt-in.
- **Iframe sandbox.** Artifact & plugin previews run in sandboxed iframes without host same-origin
  access. `UrlLoadDecision` chooses URL-load vs `srcDoc`; bridges (deck nav, palette, edits,
  tweaks) inject *only* via `srcDoc`. `isOurIframe(ev.source)` filters messages; signals that must
  come from the active iframe additionally re-check `ev.source === iframeRef.current?.contentWindow`.

This is the **correct security shape for any platform that forwards user API keys** — directly
applicable to OpenVideo's hosted tier.

### 2.4 Model support

Two distinct model surfaces, both important:

1. **Coding-agent CLIs (25 distinct executables)** — the *orchestration* brain. The agent CLI is
   where reasoning happens; OD is the file system + UI + preview around it.
2. **BYOK generation models** — for raw generation when no CLI is wanted. Paste `baseUrl + apiKey
   + model`; presets cover all major OpenAI-compatible endpoints. **Open Design Cloud** (v0.9.0)
   adds a first-party metered service: "one recharge to use GPT, Claude, Gemini, and DeepSeek,
   20+ flagship models, zero config, billed by real token usage."

**Read:** OD's "model support" is structurally *which coding agent you bring*. The actual
generative model is whatever the agent calls. This is opposite to OpenVideo, where the open video
model (H3) *is* the product and the agent layer is OpenVideo's own planner/judge.

---

## 3. UX pattern — chat + workspace + sandboxed preview

### 3.1 Primary surface

**Chat-based**, not canvas, not form. The loop (README):

```
brief  →  plugin  →  direction  →  design system  →  artifact  →  handoff  →  memory
```

Concrete steps:
1. **Pick a skill + a design system, type the brief** (Home entry point).
2. Agent locks direction (5 curated directions, or import your brand).
3. Agent emits an artifact (plugin + skill + `DESIGN.md` bound).
4. **Hand off to engineering as real HTML/CSS** (no proprietary format).
5. System learns — "screenshots, fonts, palettes, and confirmed artifacts accumulate as defaults."

### 3.2 The five UX moves worth stealing

- **Question-form artifact.** When the agent needs clarification, it emits a `<question-form>`
  markdown artifact; `AssistantMessage.tsx` renders it inline in the originating assistant
  message; answers flow back as the next user message via `formatFormAnswers` → `POST /api/chat`.
  Detection scans streamed text for the `<question-form` marker, reassembled across `text_delta`
  chunks. **Cheap, structured clarification without a modal.** OpenVideo's planner currently runs
  unattended; if we ever expose the plan step interactively, this is the pattern.

- **Studio per-project workspace** producing multiple artifact types. A project is a long-lived
  container with files, conversations, tabs — not a one-shot prompt. **OpenVideo's "film project"
  (bible + shots + receipts) is the same shape; OD is the proof that users want it.**

- **5-direction picker** at the lock-direction step. Curates divergence before convergence. Cheap
  to add to our planner's "review the bible before we generate" step.

- **Todo progress display** during long generation. OD surfaces plan items as a checklist the
  agent ticks. **OpenVideo's planner → crafter → generate → judge → stitch is a natural todo
  list we should expose in the App.**

- **Hand off as real files.** Every artifact is a real file on disk. OpenVideo already does this
  (per-shot receipts, output MP4); OD validates the design choice.

### 3.3 Modes (the breadth)

Plugin `od.mode` enumerates 8 output surfaces: `prototype / deck / live-artifact / image / video /
hyperframes / audio / design-system`. Workflow lanes (7): `import / create / export / share /
deploy / refine / extend`. **This breadth is the strategic tell:** OD is going after every
"agent-made artifact" surface simultaneously, riding the vibe-coding wave. OpenVideo's
video-only focus (`POSITIONING §4`) is the opposite bet.

---

## 4. Video path — two routes, both relevant

### 4.1 Route A — HyperFrames (HTML → MP4, deterministic)

This is OD's **first-class** video story and the part most directly borrowable. HyperFrames is a
**separate Apache-2.0 project maintained by HeyGen** (`heygen-com/hyperframes`); OD integrates it.

How it works (verified from the HyperFrames README):
- Author video as a plain HTML file with `data-*` timing attributes. A composition is a `<div>`
  with dimensions/start/composition-id; elements carry `class="clip"`, `data-start`,
  `data-duration`, `data-track-index`.
- Wire animation via GSAP / CSS keyframes / Lottie / Three.js / Anime.js / WAAPI. The timeline
  is created **paused** and registered on `window.__timelines` so the renderer can **seek it
  frame-by-frame**.
- **The renderer seeks each frame in headless Chrome and encodes with FFmpeg** — so the same
  input produces the same video. Frame-deterministic, not wall-clock.
- 19 skills ship (`/hyperframes`, `/product-launch-video`, `/faceless-explainer`, `/pr-to-video`,
  `/embedded-captions`, `/motion-graphics`, `/music-to-video`, `/remotion-to-hyperframes`, plus
  domain skills for core / animation / keyframes / media / cli).
- Package split: `hyperframes` (CLI), `@hyperframes/core`, `@hyperframes/engine` (Puppeteer +
  FFmpeg), `@hyperframes/producer`, `@hyperframes/studio`, `@hyperframes/player`,
  `@hyperframes/shader-transitions`, `@hyperframes/aws-lambda` (distributed render).
- **License:** Apache-2.0, explicitly contrasted with Remotion's source-available license ("no
  per-render fees or commercial-use thresholds").

**The contrast with diffusion video (the relevant part for OpenVideo):**
> "HyperFrames does not generate pixels from noise — it is a deterministic code-to-video
> pipeline. Every visual element is authored in HTML/CSS/media and rendered through exact frame
> capture. Full creative control, reproducibility, no hallucination, editability, CI-friendly."

OD ships **11 HyperFrames templates**: SaaS promo 16:9, TikTok karaoke 9:16 (TTS + word-synced
captions), brand sizzle reel with audio-reactive kinetic type, bar-chart race, flight map, logo
outro, money counter, website-to-video. Plus a "composition cache, sandbox-exec workaround,
MP4-as-chip" abstraction layer in `design-templates/hyperframes/`.

**Why this matters for OpenVideo:** every title card, lower-third, kinetic-type transition,
chart overlay, or logo sting in a long film is currently a wasted diffusion generation. A
deterministic HTML→MP4 path for those shots would **sharpen long-film economics and credits
story** — see §7 borrow #2.

### 4.2 Route B — routed closed-API generative

For *photorealistic* video, OD routes to **closed APIs**: **Seedance 2.0** (cinematic t2v/i2v,
the named default), **Veo 3 / Sora 2 / Kling 2** as routed variants, **Suno v5 / Lyria 2** for
audio. **39 Seedance prompts ship** in `prompt-templates/`.

**This is the structural DNA difference:** OD's generative video stack is a *polish layer over
paid closed APIs*. OpenVideo runs **H3** — the #1 open model, at Arena parity with closed — on
your own GPU, with an open judge→refine loop. OD has neither a planner→multi-shot stitcher, nor a
per-shot judge, nor FL2VA handoff. Its generative route is single-shot routing; its programmatic
route (HyperFrames) is motion-graphics only. **Neither produces a coherent multi-minute film.**

---

## 5. Community features — the real growth engine

### 5.1 Planes of contribution (the four-plane composition)

| Plane | Count | What it is |
|---|---:|---|
| **Plugins** | 277 official + 183 examples | Marketplace-distributable, `open-design.json` manifest |
| **Skills** | 100+ | `SKILL.md` convention (Claude Code format, adopted "verbatim") |
| **Design templates** | 20+ rendering templates | Prototype / deck / video scenarios |
| **Design systems** | **151 brand-grade `DESIGN.md` packages** | Apple, Stripe, Notion, Figma, Vercel, Linear, Spotify, Tesla, Nvidia, SpaceX, … |
| Prompt templates | 93 image prompts + 39 Seedance video + 11 HyperFrames | Ready-to-replicate |
| Atoms | 13 reusable UI fragments | Buttons, heroes, KPI cards |

### 5.2 The plugin SPEC (open-design.json v1.0.0)

The plugin manifest is the most spec'd contributor surface in the repo. Verified from
`plugins/spec/SPEC.md`:

```json
{
  "$schema": "https://open-design.ai/schemas/plugin.v1.json",
  "specVersion": "1.0.0",
  "name": "my-plugin",
  "version": "0.1.0",
  "od": {
    "kind": "skill",
    "taskKind": "new-generation",
    "mode": "video",
    "scenario": "marketing",
    "pipeline": {
      "stages": [
        { "id": "discovery", "atoms": ["discovery-question-form"] },
        { "id": "plan", "atoms": ["direction-picker", "todo-write"] },
        { "id": "generate", "atoms": ["file-write", "live-artifact"] },
        { "id": "critique", "atoms": ["critique-theater"], "repeat": true,
          "until": "critique.score>=4 || iterations>=3" }
      ]
    },
    "inputs": [{ "name": "audience", "type": "string", "required": true }],
    "capabilities": ["prompt:inject", "fs:write"]
  },
  "compat": { "agentSkills": [{ "path": "./SKILL.md" }] }
}
```

Key spec elements:
- **`od.mode`** — 8 output surfaces (see §3.3).
- **`od.taskKind`** — `new-generation / figma-migration / code-migration / tune-collab`.
- **`od.pipeline.stages[]`** — declarative pipeline with `repeat` + `until` (e.g.
  `critique.score>=4 || iterations>=3`). This is a **declarative refinement loop** baked into the
  manifest format.
- **`od.capabilities`** — declared permissions: `prompt:inject` (default), `fs:read`, `fs:write`,
  `mcp`, `subprocess`, `bash`, `network`, `connector`, `connector:<id>`. Restricted installs get
  `prompt:inject` only by default.
- **`od.genui.surfaces[]`** — controlled human-in-the-loop: `form / choice / confirmation /
  oauth-prompt`. Persistence scopes: `run / conversation / project`.
- **`evals/evals.json`** — required for repeatable quality checks; `evals/trigger-queries.json`
  for activation testing.
- **Minimum publishable plugin = just a `SKILL.md`.** The enriched form adds
  `open-design.json`, `README.md`, `preview/`, `examples/`, `assets/`, `references/`, `evals/`.
- **Toolchain:** `pnpm guard`, `pnpm --filter @open-design/plugin-runtime typecheck`,
  `od plugin validate ./path/to/plugin`. Folder name must match `name`. `specVersion` tracks the
  spec; `version` tracks the plugin (semver); behavior change ⇒ bump `version` in the same PR.

### 5.3 Marketplace & community

- **The Bazaar (v0.11.0)** — "a community marketplace of plugins and design systems anyone can
  pick from and contribute to." Distribution is GitHub / Open Design PR; listings also push to
  `skills.sh`, `ClawHub`, and other registries (`PUBLISHING-REGISTRIES.md`).
- **Fellow Program** — "shape the product alongside the core team, represent Open Design
  officially in their region." Funded: $1,000 / MR, free LLM credits, direct review track.
- **i18n** — README translated into 14 languages (EN, ES, PT, DE, FR, zh-CN, zh-TW, KO, JA, AR,
  RU, UK, TR, TH).
- **Channels** — Discord (daily chat, plugin sharing), X (@OpenDesignHQ, release notes +
  behind-the-scenes), GitHub Discussions (RFCs, show-your-work), GitHub Issues.
- **Sponsor** — Sealos (one-click deploy button), Open Design Cloud (the metered model service).

### 5.4 The DESIGN.md format (the highest-leverage borrow)

Verified from `design-systems/default/DESIGN.md` ("Neutral Modern" starter). **Nine sections,
machine-consumable:**

1. **Header metadata** — name, category ("Starter"), usage guidance.
2. **Visual Theme & Atmosphere** — qualitative mood ("Calm, functional, quietly confident") for
   tone decisions tokens can't express.
3. **Color Palette & Roles** — semantic role → hex ("Accent: #2F6FEB", "Background: #FAFAFA",
   Success / Warn / Danger roles). Hard constraints inline ("Never pure black; never pure white
   for backgrounds").
4. **Typography Rules** — font stack with exact fallbacks (`'Inter', -apple-system, system-ui,
   sans-serif`), weight per use case (400 body, 600 headings), **fixed type scale** (12 · 14 ·
   16 · 20 · 24 · 32 · 48 · 64), line-height, conditional letter-spacing.
5. **Component Stylings** — per-component recipes ("Buttons: 8px radius, 10px padding-block,
   16px padding-inline"; "Cards: 12px radius, 20px padding, no shadow by default"), with variants.
6. **Layout Principles** — 12-col grid, 1200px max-width, 24px gutters, hero 40–60vh, responsive
   spacing (80px / 48px / 32px).
7. **Depth & Elevation** — named tiers ("Flat (0)", "Raised (1)"), shadow params; anti-patterns
   named ("No neumorphism, no glassmorphism").
8. **Do's and Don'ts** — ✅/❌ constraint checklist.
9. **Agent Prompt Guide** — meta-instructions ("When in doubt, subtract"; "Do not invent hex
   values outside this palette"; fallback rule: "surface a warning comment in the artifact and
   use the closest existing token").

**Why it matters:** every artifact (prototype, deck, image, *video*) reads the same Markdown
contract. This is the **brand-contract pattern** — a single file that the crafter, the judge, and
the renderer all obey. 151 example systems ship. It is the single highest-leverage idea in the
repo for OpenVideo (§7 borrow #1).

---

## 6. Growth — what made them reach 84K★ in ~3 months

**No single viral mechanic — a stack of timing, positioning, and operational cadence.** Honest
read of the evidence:

1. **Piggybacked on Anthropic's Claude Design launch (April 2026).** README opens by dating the
   trigger: *"In April 2026, Anthropic released Claude Design"*, described as viral but
   "closed-source, paid-only, cloud-only." OD's tagline is *"the open-source Claude Design
   alternative."* This is **superlative timing** — surfacing a closed viral product's open
   alternative in the same news cycle is the highest-leverage growth move in open source. **Lesson
   for OpenVideo: launch inside the news cycle of every closed competitor's release** (Seedance /
   Sora / Veo / Runway announcements are our trigger events).

2. **Agent-native wave, not video wave.** OD rides the *coding-agent* hype (Claude Code, Codex,
   Cursor), which is the dominant 2026 open-source growth vector. The 84K★ is largely the
   coding-agent audience, *not* a video audience. **This is why their star count is not the
   ceiling for an open video project — different audience.**

3. **"Your CLI becomes the design engine" is a memeable, low-friction hook.** It repurposes a tool
   the target user already has and loves. There's no install a new model step. The friction story
   is "I already have Claude Code, this just makes it draw." OpenVideo's friction story ("install
   ComfyUI + pull H3 + run") is currently heavier — a real lesson.

4. **Operational cadence is extreme.** 18 minor releases in 14 weeks, each release taglined as a
   *product moment*. v0.18.0 = "115 PRs · 22 contributors · 2 days." A 22-contributor, 115-PR
   sprint in 2 days is not a side project — this is a funded team operating at startup velocity.
   The README's Fellow Program (funded) and Open Design Cloud (metered) signal a real commercial
   backbone, not a hobby repo. **The star count tracks the cadence, not just the launch.**

5. **Breadth recruits breadth.** Seven output surfaces mean seven distinct audiences each find
   something to star for. A Figma migrator, a Notion-user, a TikTok creator, a PM making a deck —
   each is a star. OpenVideo's video-only focus is the right *product* call (POSITIONING §4) but
   it is a narrower recruiting funnel by design.

6. **14-language i18n at launch.** Non-English open-source audiences are large and underserved;
   shipping 14 README translations on day one is a measurable star multiplier, especially in
   zh / ja / ko / es / pt markets where the closed incumbents are weak.

7. **151 design systems as stars bait.** Apple / Stripe / Notion / Figma / Tesla / Nvidia /
   SpaceX brand systems are individually searchable; each one is a Google entry point and a
   Hacker-News-showable artifact. **A library of recognizable brands is itself a growth hack.**

**What is *not* the cause:** there is no evidence of paid promotion, no viral video demo, no
celebrity endorsement in the verified material. The growth is *timing × positioning × cadence ×
breadth × i18n × brand-bait*, executed by a funded team.

---

## 7. TOP 5 things OpenVideo should BORROW (concrete, with how-to-adapt)

> Order = leverage for OpenVideo, highest first. Each item states the borrow, *why*, and a
> concrete adaptation path against our current `ARCHITECTURE.md` shape.

### Borrow #1 — The `DESIGN.md` brand-contract pattern (as `STYLE.md` for film)

**What.** A single Markdown file holds the visual contract — tokens, palettes, fonts, component
recipes, do/don'ts, agent prompt guide — that *every* artifact reads and obeys. 151 shipped
examples prove it scales.

**Why for OpenVideo.** Our `library/style_profiles/` is currently a list of LoRAs and presets,
not a *contract*. Films have stronger brand needs than dashboards: color science (LUTs),
shot-composition rules, dialogue voice, pacing, lower-third typography, music genre. A
`STYLE.md` per project (or per series) that the **crafter and the judge both read** would close
the loop on "does shot 14 obey the film's contract?" — currently our judge scores vs intent and a
quality bar, but not vs a written style contract. This is the **single highest-leverage borrow**
because it makes style consistency *machine-checkable* across a multi-minute film.

**How to adapt (concrete).**
- Add `library/style_profiles/<name>/STYLE.md` mirroring OD's 9-section format, *inverted for
  video*: (1) Header & usage, (2) Mood & tone references, (3) Color science (LUT name + role
  palette + "never pure black" rules), (4) Typography (lower-third, title card fonts + scales),
  (5) Shot composition (lens, framing, do/don'ts per scene type), (6) Pacing & rhythm (target cut
  frequency, act-level tempo), (7) Audio (music genre, dialogue treatment, BGM rules), (8) Do's
  & Don'ts, (9) Crafter & Judge prompt guide.
- Wire `core/crafter.py` to inject the active `STYLE.md` into the per-shot prompt, and
  `core/judge.py` to score each shot against it as an additional axis. The judge already extracts
  frames and uses a vision model; adding "does this shot obey the STYLE.md color/pacing/composition
  rules" is a prompt-level change, not new infra.
- Ship 5–10 example `STYLE.md` profiles at launch (noir, documentary, product-spot, anime,
  handheld-indie) as stars bait — OD's brand-bait pattern (§6 item 7), adapted to film genres.

**Cost.** ~1 week. Mostly prompt-engineering + doc authoring; no core rewrite.

---

### Borrow #2 — HyperFrames as a deterministic "programmatic shot" adapter

**What.** HTML + CSS + GSAP → headless Chrome → FFmpeg = deterministic MP4. Apache-2.0, HeyGen-
maintained, frame-seekable, 19 skills, AWS-Lambda distributed render. OD uses it for 11 motion-
graphics templates.

**Why for OpenVideo.** Every title card, lower-third, kinetic transition, chart overlay, logo
sting, end-credit sequence in a long film is currently a **wasted diffusion generation** —
expensive, non-deterministic, and wrong-tool-for-the-job. A programmatic shot path (a) slashes
GPU cost on title/transition shots, (b) gives frame-accurate reproducibility (no judge needed —
the shot *is* the spec), (c) makes the credits/pricing story sharper ("we only spend a generation
on shots that need pixels"). Pixelle's `static_*` template taxonomy (COMPETITOR_DEEP_DIVE §2a)
points the same way.

**How to adapt (concrete).**
- Add `engines/hyperframes/` as a new `EngineAdapter` alongside `engines/comfyui/`. The adapter's
  `generate(shot)` writes the HTML+CSS+GSAP and shells to the HyperFrames CLI
  (`npx hyperframes render`). Return the MP4 path as the shot result — same `ShotResult` shape as
  a ComfyUI shot, so `pipeline.py` doesn't change.
- Extend `core/planner.py` to tag each shot with a `mode`: `diffusion` (a real generation via
  ComfyUI+H3) or `programmatic` (a HyperFrames render). Heuristics: title cards, charts, lower
  thirds, logo stings, end credits → `programmatic`; photorealistic narrative shots → `diffusion`.
- The `core/validator.py` hard-gate already exists; add a `programmatic`-mode gate that checks
  the shot's HTML is valid and the timeline is seekable (HyperFrames ships a linter).
- Ship 3–5 starter templates (animated title, end credits, lower-third, chart-overlay, beat-synced
  cut) under `library/hyperframes_templates/`.

**Cost.** ~2 weeks. Adapter is a thin shell-around-CLI; the value is in planner tagging + a few
good templates. **Highest ROI of any infra borrow** — directly improves long-film economics.

---

### Borrow #3 — The plugin manifest SPEC (validated, CI-checkable `library/`)

**What.** OD's `open-design.json` v1.0.0: a validated manifest with `specVersion`, declared
`capabilities`, declarative `pipeline.stages` with `repeat`/`until`, required `evals/evals.json`,
`od plugin validate` toolchain, scaffold/validate PR checklist.

**Why for OpenVideo.** Our `library/` is one plane (prompts / reference_packs /
coherence_recipes / style_profiles) with no manifest, no capabilities, no evals, no validator.
The first contributor-submitted LoRA or recipe that silently breaks a film will be a real pain.
A validated manifest makes contributor artifacts **safe, CI-checkable, and marketplace-ready**
(positioning §6 advantage 2 — the compounding community library — depends on this).

**How to adapt (concrete).**
- Define `open-video.json` v1.0.0 per library artifact. Fields:
  `specVersion`, `name`, `version`, `kind` (`prompt` / `reference_pack` / `coherence_recipe` /
  `style_profile` / `lora`), `compat` (which backends / engines it works with — e.g.
  `"backends": ["h3"], "engines": ["comfyui"]`), `inputs[]`, `capabilities[]` (e.g.
  `"fs:read"`, `"comfyui:workflow"`, `"lora:load"`), and an optional declarative pipeline mirror
  of our planner→crafter→judge→stitch flow.
- **Mandatory `evals/evals.json`** for any artifact that alters generation: each entry has `id`,
  `prompt`, `expected` (e.g. "shot passes judge with score ≥ 4"), `assertions[]`. This makes the
  library **regression-testable** — a contributor's LoRA must demonstrably not regress quality.
- Add `open-video validate <path>` and a `library/AGENTS.md` PR checklist mirroring OD's
  (`pnpm guard` → `open-video validate`).
- Mirror the "minimum publishable = just a `SKILL.md`" rule: the minimum OpenVideo library
  artifact is a single prompt file; the manifest is required only for marketplace presence.

**Cost.** ~1.5 weeks. Mostly schema + validator + docs; no core changes. Pays off the day the
second contributor lands.

---

### Borrow #4 — MCP server exposing the active film project to agents

**What.** OD ships a stdio MCP server (`od mcp install <agent>`) exposing `project list / files
list / files read / plugin list / skills list` read-only. Any MCP-compatible agent becomes a
first-class participant in the project.

**Why for OpenVideo.** Our `interfaces/skill/` (`SKILL.md`) lets an agent *invoke* OpenVideo, but
it's one-shot — the agent can't *inspect* the active film project mid-flight (read the coherence
bible, list shots, read a receipt, see why shot 7 was refined). An MCP server makes OpenVideo a
**first-class tool inside Claude Code / Cursor / Codex**, not just a skill they call. This matters
because OD's entire 84K★ wave is the coding-agent audience; being a first-class MCP participant
puts OpenVideo inside that audience's existing workflow instead of asking them to leave it.

**How to adapt (concrete).**
- Add `interfaces/mcp/server.py` exposing read-only tools over the active project:
  `open_video.film.list`, `open_video.bible.read`, `open_video.shots.list`, `open_video.shot.read`
  (prompt + settings + judge verdict + fix log), `open_video.receipts.read`, `open_video.library.search`.
- Add write tools with explicit capability gates: `open_video.shot.refine` (trigger a re-judge of
  a specific shot), `open_video.film.regenerate_from_scene` (re-plan from a given scene).
- Ship `open-video mcp install <agent>` mirroring OD's per-agent install snippets.
- Keep the existing `SKILL.md` for fully-autonomous one-shot use; the MCP server is for the
  *collaborative* case where a creator drives from inside their coding agent.

**Cost.** ~1 week for read-only; ~2 weeks with write tools. Stdio MCP server is small; the value
is being inside the agent loop instead of beside it.

---

### Borrow #5 — The BYOK proxy + SSRF guard for the hosted tier

**What.** OD's `/api/proxy/{provider}/stream` with per-target SSRF protection (blocks internal
IPs / link-local / CGNAT), strict opt-in `OD_ALLOWED_INTERNAL_HOSTS` (exact-host matching, no
subdomain/CIDR), `OD_BIND_HOST` + `OD_ALLOWED_ORIGINS` for LAN exposure.

**Why for OpenVideo.** Our Phase-2 hosted tier (POSITIONING §3 business DNA) and any SaaS/API
path will forward user API keys to model endpoints. This is the **correct security shape**, ready
to lift. We should not reinvent it.

**How to adapt (concrete).**
- Implement `OPEN_VIDEO_ALLOWED_INTERNAL_HOSTS` (exact-host opt-in for VPN-hosted ComfyUI / SGLang
  on `10.x` / `192.168.x`), `OPEN_VIDEO_BIND_HOST` (default `127.0.0.1`), and per-target SSRF
  filtering at the proxy edge, mirroring OD's three-knob pattern.
- Reuse OD's *exact* allowlist rules: no subdomain/substring/CIDR — explicit host only. This is a
  deliberately tight shape; do not loosen it.
- Pair with the per-shot receipt (which we already ship) so every proxied generation is auditable.

**Cost.** ~3 days. The pattern is well-documented; port the rules verbatim.

---

## 8. TOP 3 things OpenVideo does BETTER (structural, evidence-based)

> Framing matters: OD is at 84K★ and OpenVideo is pre-launch. "Better" here means **structural
> advantages in the long-form coherent video lane that OD does not have the IP for**, not market
> position. Each is a consequence of focus, not of execution — OD executes excellently *on a
> different problem*.

### Better #1 — Long-form coherence (planner → FL2VA → judge → stitch)

**The evidence.** OD's video routes are (a) HyperFrames = motion-graphics only (HTML→MP4, no
photorealistic generation, §4.1), and (b) routed closed-API single-shot Seedance/Veo/Sora/Kling
(§4.2). **Neither has a planner, neither has a per-shot judge, neither has multi-shot stitching,
neither has FL2VA handoff across a 15-second ceiling.** OD's plugin manifest even encodes a
refinement loop (`pipeline.stages[].repeat until critique.score>=4`) — but that loop is for
*artifacts in general*, not for shot-level video coherence.

OpenVideo's `core/pipeline.py` — plan → craft → validate → generate (w/ FL2VA chaining) → judge
→ refine → stitch — is the **director layer OD does not have and cannot add without becoming a
different product** (it would have to abandon the "your CLI is the engine" abstraction and build
a film-specific brain). The honest gap we acknowledge (stitched < native coherence, see
`POSITIONING §2`) is still a gap OD doesn't even attempt to close. **This is the flagship IP.**

### Better #2 — Open-model baseline on your own GPU vs. closed-API routing

**The evidence.** OD's generative video stack routes to **Seedance / Veo / Sora / Kling** — paid
closed APIs (§4.2). The `od.mode: "video"` surface is a prompt that gets sent to a closed
endpoint; the user pays per second to those vendors. The deterministic HyperFrames path is free
but motion-graphics-only.

OpenVideo runs **MiniMax H3** — the #1 open video model, T2V #2 / I2V #3 on Artificial Analysis
Arena, within benchmark noise of the closed #1 (`POSITIONING §2`) — **on your own GPU**, with
**no per-second billing, no region lock, no server-side content filter, no model churn**
(`POSITIONING §6` Advantage 1). The DNA difference is structural: OD is a polish layer over paid
APIs; OpenVideo is the open alternative to those APIs. When Seedance/Veo/Sora change price,
terms, or geography, OD's users are affected; OpenVideo's are not.

### Better #3 — Per-shot judge → refine loop, in the open

**The evidence.** OD has a *general* critique atom (`critique-theater`, `pipeline.stages` with
`repeat until critique.score>=4 || iterations>=3`) — but it is artifact-level, prompt-in/text-out,
and not coupled to a vision model scoring actual video frames. There is no
extract-frames-and-judge-against-intent step anywhere in the OD stack, because the OD stack does
not generate video frames from noise.

OpenVideo's `core/judge.py` is the **productized VISTA / VideoWeaver pattern**: extract frames →
vision-assess vs prompt intent + a quality bar (and, after borrow #1, vs the `STYLE.md` contract)
→ diagnose → targeted fix → regenerate (best-of-N optional). This loop is the **thing no open
video project has** (`COMPETITOR_DEEP_DIVE` confirms: OpenMontage 45K★ lacks it; ViMax 11.7K★ is
closed-API-only). It is also the loop that turns a single-shot ≤15s open model into a coherent
multi-minute film. OD cannot add it without rebuilding the entire video path.

> **One-line summary of the three:** OpenVideo is the open long-form director; Open Design is the
> open broad artifact studio. Same license, opposite focus.

---

## 9. Partner or compete?

**Partner — aggressively and visibly — on the surfaces where we are complementary; compete on
none.** The evidence is unambiguous:

### Why complementarity is structural, not tactical

1. **Different lanes.** OD = broad artifact studio (7 surfaces, video is one). OpenVideo =
   video-only long-form director (`POSITIONING §4`). OD's video routes are motion-graphics
   (HyperFrames) + closed-API single-shot routing (Seedance/Veo/Sora/Kling). Neither is a
   long-form coherent open film. **OD does not make films; we do not make decks.** No positional
   overlap.

2. **Different model DNA.** OD's generative stack is closed-API routing; ours is open-model-on-
   your-GPU. Even if OD wanted to add H3, its architecture (daemon spawns CLI, CLI calls whatever
   it wants) is not built around a *specific open video model's* workflow grammar (H3's 3-field
   prompts, FL2VA/T2V/R2V, int8_convrot settings — `ARCHITECTURE.md` `backends/h3/`). We own that
   depth; they don't want it.

3. **Different audiences converging on the same skill format.** OD adopted Claude Code's
   `SKILL.md` "verbatim." OpenVideo's `interfaces/skill/` is the same format. **The skill format
   is the natural integration point** — both projects already speak it.

### Concrete partnership surface (the win-win)

- **OpenVideo as an OD plugin.** Wrap OpenVideo's `open-video "..." --duration 300` CLI (or the
  MCP server from borrow #4) as an OD plugin with `od.mode: "video"`, `od.taskKind:
  "new-generation"`, `od.capabilities: ["subprocess", "fs:write"]`, pipeline stages
  `[plan, craft, validate, generate, judge{repeat until score>=4}, stitch]`. OD users gain an
  open long-form director; OpenVideo gains access to OD's 84K★ audience the day the plugin ships
  in OD's marketplace. **This is the single highest-leverage distribution move available to
  OpenVideo at launch.**

- **HyperFrames reciprocation.** We adopt HyperFrames as a programmatic-shot engine (borrow #2);
  in return, we can contribute long-form coherence templates (multi-shot FL2VA chains) upstream
  to HyperFrames, since their current templates are short motion-graphics. The relationship is
  with the HeyGen HyperFrames team, not with OD directly — two separate partnerships.

- **Shared library format.** If we adopt a `STYLE.md` / `open-video.json` pattern inspired by OD's
  DESIGN.md / open-design.json (borrows #1 and #3), we can propose a cross-project library
  interchange so a OD design system can be referenced as the visual contract for an OpenVideo
   film. This is a long-term play; the immediate win is just "we both speak SKILL.md."

### Where to *not* partner

- **Do not depend on OD for distribution.** The plugin is a *channel*, not a strategy. OpenVideo's
  primary surface stays `open-video.ai` + the App + the CLI + our own Discord. If OD pivots or
  slows (it's a funded team operating at extreme cadence — that can change), OpenVideo must stand
  alone.
- **Do not adopt OD's breadth.** Resisting the all-modalities trap (`POSITIONING §4`) is what
  protects the focus that makes Better #1–#3 true. Partnership is at the *integration surface*
  (plugin / MCP / skill), not at the product scope.

### Recommended public posture

> **"Open Design is the studio for everything else; OpenVideo is the director for film. Same open
> ethos, same skill format, different problems. We ship OpenVideo as an OD plugin on day one."**

This costs nothing, earns goodwill from a 84K★ community, and routes their audience into our
funnel. It also pre-empts the "are you competing with open-design?" question with a structural
answer.

---

## 10. Action register (sequenced)

| # | Action | Source borrow | Owner lane | Est. cost | Precedence |
|---|---|---|---|---|---|
| 1 | Author `library/style_profiles/STYLE.md` spec + 5 launch profiles | Borrow #1 | `core/` + docs | 1 wk | **Pre-launch** |
| 2 | Wire `STYLE.md` into `crafter.py` + `judge.py` (style-axis score) | Borrow #1 | `core/` | 3 days | **Pre-launch** |
| 3 | Add `engines/hyperframes/` adapter + planner `mode` tagging | Borrow #2 | `engines/` + `core/planner.py` | 2 wk | **Phase 1** |
| 4 | Define `open-video.json` v1.0.0 + `open-video validate` | Borrow #3 | `library/` + `cli/` | 1.5 wk | **Pre-launch** |
| 5 | Ship `interfaces/mcp/server.py` (read-only first) | Borrow #4 | `interfaces/` | 1 wk | **Phase 1** |
| 6 | Implement BYOK proxy + SSRF guards for hosted tier | Borrow #5 | (hosted) | 3 days | **Phase 2** |
| 7 | Wrap OpenVideo as an OD plugin (`od.mode: video`) | §9 partnership | `interfaces/` | 3 days | **At OD Bazaar listing window** |
| 8 | i18n README into 8 languages at launch (zh / ja / ko / es / pt / fr / de / ar) | §6 item 6 | docs | 1 wk | **Pre-launch** |
| 9 | Launch inside the next closed-competitor news cycle | §6 item 1 | growth | 0 | **Trigger-based** |

---

## 11. Sources (all verified 2026-08-06)

- `gh api repos/nexu-io/open-design` — stars/forks/created/license/topics/homepage.
- `gh api repos/nexu-io/open-design/releases` — release cadence, v0.14.0→v0.18.0 bodies.
- `gh api repos/nexu-io/open-design/topics` — 20 topics (figma-alternative, claude-design, byok,
  agent-skills, vibe-coding, ui-generator, design-systems, …).
- `https://raw.githubusercontent.com/nexu-io/open-design/main/README.md` — features, stack,
  agent list, BYOK, design systems, plugins, architecture summary, roadmap, lineage.
- `https://raw.githubusercontent.com/nexu-io/open-design/main/AGENTS.md` — daemon/CLI spawning,
  stdin protocols, sidecar IPC, MCP, data-dir contract, iframe security.
- `https://raw.githubusercontent.com/nexu-io/open-design/main/docs/architecture.md` — content
  registry, daemon ownership, sandbox boundary, persistence model.
- `https://raw.githubusercontent.com/nexu-io/open-design/main/plugins/spec/SPEC.md` —
  `open-design.json` v1.0.0 schema, modes, lanes, capabilities, evals, validate toolchain.
- `https://raw.githubusercontent.com/nexu-io/open-design/main/design-systems/default/DESIGN.md`
  — 9-section brand-contract format (the highest-leverage borrow).
- `https://raw.githubusercontent.com/heygen-com/hyperframes/main/README.md` — HTML→MP4 pipeline,
  determinism, skills, package split, Apache-2.0, HeyGen-maintained.
- `curl -sI` on `open-design.ai` (HTTP 200), `discord.gg/mHAjSMV6gz` (301 → valid),
  `x.com/OpenDesignHQ` (HTTP 200) — community presence.
- Internal: `/mnt/data/workspace/open-video/README.md`, `ARCHITECTURE.md`, `docs/POSITIONING.md`,
  `docs/COMPETITOR_DEEP_DIVE.md` — OpenVideo's own positioning, architecture, and prior
  competitor research this deep-dive extends.

> **Verify-before-publish tag:** star count, release cadence, and HyperFrames template counts
> drift weekly. Re-pull `gh api` and the HyperFrames README before any external publication. The
> architectural mechanics (daemon-spawns-CLI, DESIGN.md format, plugin SPEC, HyperFrames pipeline)
> and the borrow/adapt recommendations are durable.
