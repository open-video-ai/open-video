# Competitor Deep Dive — Three Newly-Discovered Open-Source Video Projects

> Status: **research / v1** · All facts verified 2026-08-06 against `gh api` and each repo's `main` README.
> Scope: three Apache-2.0 projects that overlap with OpenVideo's mission. For each: what they do
> well (and what we should borrow), where OpenVideo is stronger, features we're missing, and a
> one-line competitive read.
> Companion to `docs/POSITIONING.md` (our locked positioning) and `docs/OPEN_VS_CLOSED.md`.

---

## 0. Snapshot (verified 2026-08-06)

| Project | Stars | Forks | Language | Created | Last push | Stack signal |
|---|---:|---:|---|---|---|---|
| **nexu-io/open-design** | 84,180 | 9,803 | TypeScript | 2026-04-28 | 2026-08-06 | Next.js 16 + Electron + Express daemon; BYOK 25+ agent CLIs; MCP server |
| **ATH-MaaS/Pixelle-Video** | 26,537 | 3,832 | Python | 2025-11-07 | 2026-06-14 | ComfyUI workflows + direct API models; LLM script → image → TTS → video |
| **FireRedTeam/FireRed-OpenStoryline** | 3,194 | 374 | Python | 2026-02-07 | 2026-07-31 | LangChain agent + MCP server + MoviePy/FFmpeg; conversational editing |

All three are Apache-2.0. All three are younger than ~10 months old — the category is fresh and
none of these are entrenched. The star velocities are real (open-design at 84k in ~3 months is a
breakout) and tell us where mindshare is moving.

The category split is sharp and is itself the headline finding:

- **open-design** = *broad artifact studio* (HTML/PDF/PPTX/MP4) where video is one of seven
  outputs and the agent is a user-supplied CLI. Closest to the "vibe coding" wave, not to Runway.
- **Pixelle-Video** = *short-video automator* (topic → vertical short). Closest to a content-marketing
  pipeline, not a film director.
- **FireRed-OpenStoryline** = *editing agent* (cuts/sequences existing footage). Closest to an
  AI Premiere/CapCut, not a generator.

**None of the three occupies OpenVideo's lane** (open autonomous *director* that *generates*
long-form coherent video on top of open models). That is the headline. OpenVideo's positioning
(`docs/POSITIONING.md` §2) — model-agnostic planner→crafter→judge→stitch on H3/ComfyUI — is
uncontested by these three. The borrowable value is in *product patterns* and *single features*,
not in conceding any positional ground.

---

## 1. nexu-io/open-design — the broad artifact studio (84k★)

**One-line read:** A local-first Electron desktop app that turns any coding-agent CLI on your
`PATH` (Claude Code, Codex, Cursor, Gemini, OpenCode, Qwen — 25 distinct executables backed by 26
runtime defs) into a *design engine* that emits real files: prototypes, decks, dashboards, images,
and **video** (HTML/PDF/PPTX/MP4/ZIP/Markdown). It is the "open-source Claude Design alternative"
and the fastest-growing of the three.

**Architecture (verified from README):**
- Frontend: Next.js 16 App Router + React 18 + TypeScript
- Daemon: Node 24 + Express + SSE + `better-sqlite3` (the privileged process)
- Desktop: Electron shell, sandboxed renderer, sidecar IPC (`STATUS · EVAL · SCREENSHOT · CONSOLE · CLICK · SHUTDOWN`)
- Storage: SQLite for projects/conversations/messages/tabs/templates
- MCP stdio server exposes project files to external agents
- BYOK proxy: `POST /api/proxy/{anthropic,openai,azure,google,ollama,senseaudio}/stream` with per-target SSRF protection and an opt-in internal-host allowlist (`OD_ALLOWED_INTERNAL_HOSTS`)
- Plugin/Skill/Template/DesignSystem four-plane composition with `od plugin scaffold`/`validate` toolchain and a published plugin SPEC

**How they do video (two distinct pathways):**
1. **HyperFrames (HTML→MP4, programmatic).** The agent writes HTML + CSS + GSAP; HyperFrames
   (HeyGen's open-source Apache-2.0 framework at `heygen-com/hyperframes`) renders it to a
   deterministic MP4 via headless Chrome + FFmpeg. OD layers on a composition cache, sandbox-exec
   workaround, and "MP4-as-chip" abstraction. 11 templates ship in-repo (SaaS promos 16:9,
   TikTok karaoke 9:16 with TTS + word-synced captions, brand sizzle reels with audio-reactive
   kinetic type, bar-chart races, flight maps, logo outros, money counters, website-to-video).
2. **Routed model variants (generative).** Seedance 2.0 for cinematic t2v/i2v; Veo 3 / Sora 2 /
   Kling 2 as routed variants; Suno v5 / Lyria 2 for audio. 39 Seedance prompts ship.

**The UX that's working (84k in 3 months says so):** "Your CLI becomes the design engine, your
laptop becomes the studio, and your team's `DESIGN.md` becomes the brand contract." Every render
reads a Markdown design system as the source of truth; 151 example design systems ship.

### (a) What they do WELL that OpenVideo should borrow

1. **The `DESIGN.md` brand-contract pattern.** A single Markdown file holds the design tokens,
   palettes, fonts, component conventions — every artifact reads from it. We have `library/`
   (LoRAs, reference-packs, recipes) but no on-disk *brand contract* a render must obey. **Borrow:
   adopt a `STYLE.md` (or extend our recipe format) as the brand source-of-truth that the crafter
   and judge both read.** This is the single highest-leverage idea here.

2. **HyperFrames as a *deterministic* video pathway.** HTML+CSS+GSAP → headless Chrome → FFmpeg
   is controllable, debuggable, frame-accurate, and zero-model-cost for motion-graphics shots
   (titles, lower-thirds, kinetic type, bar-chart races, logo stings). OpenVideo currently treats
   every shot as a diffusion generation. **Borrow: add a "programmatic shot" adapter so the
   planner can route title/transition/overlay shots to a HyperFrames-style renderer instead of
   spending a generation.** It sharpens the long-film economics and the credits story.

3. **The BYOK proxy with SSRF guards.** Per-target SSRF protection blocking internal IPs /
   link-local / CGNAT at the daemon edge, with strict exact-host opt-in allowlist for internally
   hosted gateways. This is the correct security shape for any platform that forwards user API
   keys to model endpoints. **Borrow wholesale for the hosted tier / OpenVideo Cloud.**

4. **The MCP "expose-the-project" pattern.** `od mcp install <agent>` injects per-agent config so
   any MCP-compatible agent can query project files without manual config. Our POSITIONING lists
   a `SKILL.md` interface; **we should ship an MCP server that exposes the active film project
   (bible, shots, receipts) the same way**, so OpenVideo becomes a first-class tool inside Claude
   Code / Cursor / Codex, not just a skill they invoke.

5. **Plugin/Skill/Template/DesignSystem four-plane composition with a published SPEC and
   scaffold/validate toolchain.** Our `library/` is one plane. Borrowing the *validated manifest*
   pattern (`open-design.json` / `SKILL.md` + `od plugin validate`) would make our
   LoRAs/recipes/packs contributor-safe and CI-checkable.

6. **Artifact-first agent output.** They expect the agent to produce structured files (HTML, MP4,
   PPTX), not prose. Our per-shot receipts already lean this way; making "an artifact, not a
   paragraph" the explicit agent contract would harden the judge→refine loop.

### (b) What OpenVideo does BETTER (our advantages)

- **Focus.** Open-design is genuinely *seven artifacts* (prototypes, decks, dashboards, slides,
  images, video, live artifacts). Video is one pillar, not the product. OpenVideo's video-only
  focus (POSITIONING §4) is a structural advantage in depth: coherence bibles, FL2VA handoff,
  per-shot judges, multi-shot stitching — none of which open-design has.
- **Long-form coherence.** Open-design's *generative* video route is single-shot Seedance/Veo/Sora
  routing; its *programmatic* route is motion-graphics only. There is **no planner → multi-shot
  stitcher**. OpenVideo's director layer is the thing they don't have.
- **Open-model baseline, not closed-API routing.** Open-design's generative stack *routes to
  closed APIs* (Seedance/Veo/Sora/Kling). OpenVideo runs H3 (the #1 open model, Arena parity with
  closed) on your own GPU. Different DNA: they're a polish layer over paid APIs; we're the open
  alternative to those APIs.
- **Local-first with no censorship / no per-second billing.** Same POSITIONING §6 advantage.
- **Verified Prompt Gallery + per-shot receipts as the public proof.** Their flywheel is "your CLI
  makes nice files"; ours is "prompt → video → quality verdict, in the open."

### (c) Features we're MISSING (gaps to consider)

- **MP4 as one export among many** (HTML/PDF/PPTX/MP4/ZIP/Markdown). OpenVideo exports MP4 + per-shot
  receipts. The *export the storyboard as a deck* feature (storyboard → PDF/PPTX for review) is a
  genuinely useful pre-production surface we don't have. Consider for the App.
- **A desktop (Electron) app.** They have a polished local-first desktop shell. Our App is
  web-first; an Electron wrapper (or a Tauri one) is on the table if local-first creators want it.
- **A daemon-spawns-CLI orchestration pattern.** We have a Skill interface but we haven't framed
  OpenVideo *itself* as something a daemon orchestrates from inside other tools.

### (d) One-line competitive assessment

> **Not a competitor — a complement.** Open-design is a broad artifact studio whose video is
> either motion-graphics (HTML→MP4) or closed-API routing; OpenVideo is the open long-form
> director it doesn't have. The borrowable IP (`STYLE.md` brand contract, HyperFrames-style
> programmatic shots, BYOK SSRF proxy, MCP project server, plugin SPEC) is significant.

---

## 2. ATH-MaaS/Pixelle-Video — the short-video automator (26.5k★)

**One-line read:** A Python pipeline that turns a single topic keyword into a finished vertical
short video, fully automatically, by chaining LLM → image-gen → TTS → BGM → composition on top of
ComfyUI workflows and direct API models. Tagline: "零门槛，零剪辑经验" (zero barrier, zero editing
experience).

**Pipeline (verified from README):** four stages —
`文案生成 → 配图规划 → 逐帧处理 → 视频合成` (script → illustration planning → frame-by-frame →
composition). From one topic: LLM writes the script → per-segment images/clips → TTS narration →
BGM → composite. Progress is shown per shot ("分镜 3/5 - 生成插图").

**Model support (the breadth is real):**
- LLM: GPT, Qwen, DeepSeek, Ollama (local/free)
- Image: ComfyUI workflows (default `image_flux.json`), DashScope (Wanxiang), OpenAI GPT-Image, ByteDance Seedream, Nano Banana, RunningHub cloud
- Video: **WAN 2.1**, DashScope Wan/HappyHorse, Kling AI, ByteDance Seedance, RunningHub cloud (48 GB VRAM boxes), image-to-video + motion-transfer pipelines
- TTS: Edge-TTS (pinned version), Index-TTS (voice cloning from reference), multi-language, custom ComfyUI TTS workflows
- Built on **Pixelle-MCP** — a "ComfyUI MCP server that lets AI assistants directly call ComfyUI"

**ComfyUI integration:** auto-scans `workflows/` for TTS workflows; supports local ComfyUI
(`127.0.0.1:8188`) and cloud RunningHub with configurable concurrency; custom workflows drop into
`workflows/`; template custom parameters on API interfaces; content-moderation retry (neutralize
prompt + retry on moderation failure) and network download retries.

**Templates are typed by media need:** `static_*.html` (no AI media, pure text styling),
`image_*.html` (AI images as backgrounds), `video_*.html` (AI video as backgrounds).

### (a) What they do WELL that OpenVideo should borrow

1. **Atomic-capability composition with swappable backends.** "Image, video, TTS, VLM each
   replaceable; ComfyUI workflows *or* direct API models." Our model-agnostic adapter (ComfyUI
   today, diffusers/sglang tomorrow) is the same idea; **the borrowable piece is the *uniform
   capability interface* — image, video, TTS, vision-as-judge all behind one swappable spec** so a
   contributor can drop in a new provider without touching the planner. We have this for the video
   model; we should explicitly extend it to TTS and to the *judge* (vision model is swappable).

2. **Template taxonomy by media need (static / image / video).** This is a smart, cheap
   optimization: not every segment needs a generation. **Borrow: a segment-typing layer so the
   planner can mark some segments "stock/programmatic" and only spend generations where they
   matter.** Pairs naturally with the HyperFrames programmatic-shot idea from open-design.

3. **Content-moderation retry.** For the *hosted* tier (where the upstream API may refuse), a
   "neutralize prompt and retry on moderation failure" loop is a polite, useful fallback. The
   local tier (POSITIONING §6) needs no such thing. **Borrow for the hosted/API path only; never
   for local.**

4. **One-click Windows package bundling ffmpeg.** "No need to install Python, uv, or ffmpeg —
   one-click, out of the box." OpenVideo's install story for non-technical creators (the App
   audience) is currently the weakest link. **Borrow aggressively: a batteries-included installer
   that bundles ComfyUI deps + ffmpeg + a default quantized H3 is the difference between "for
   everyone" and "for developers."**

5. **Custom-material reverse pipeline.** "Upload your photos/videos, AI analyzes and generates
   scripts." This is the inverse of our generate-from-concept flow, and it's a real onboarding
   pattern (creators bring footage). **Borrow as a "footage-to-film" entry mode** in the App.

6. **Flexible script segmentation** (paragraph / line / sentence). Tiny detail, real value: the
   unit-of-segmentation choice changes per genre. Borrow into the planner.

### (b) What OpenVideo does BETTER (our advantages)

- **It's an automator, not a director.** Pixelle produces *one short per topic* with **no
  judge→refine loop, no coherence bible, no multi-shot handoff, no per-shot receipts.** The README
  is explicit: when results are unsatisfactory, the FAQ tells users to *manually* switch LLM,
  adjust prompt prefixes, change TTS workflow, try a different template. **OpenVideo's judge and
  refine loop is the entire IP Pixelle lacks.**
- **No quality loop of any kind.** Verified from README: "No explicit automated quality evaluation
  loop exists." OpenVideo's judge scoring each shot vs intent + quality bar (the
  VISTA/VideoWeaver pattern productized) is a structural moat.
- **Short-video-only.** Vertical shorts, single-segment topic. No long-form film, no acts →
  sequences → shots planning. POSITIONING §4 focus (long coherent films) is uncontested.
- **Closed-API-heavy, not open-model-first.** Default stack leans on DashScope, Kling, Seedance,
  RunningHub — paid services. H3 (our baseline, #1 open, Arena parity) isn't in their default
  path. Openness advantage holds.
- **Last push 2026-06-14** — the repo is ~7 weeks stale at time of writing. Maintenance signal.

### (c) Features we're MISSING (gaps to consider)

- **TTS as a first-class pipeline stage with multiple backends (Edge, Index with voice cloning,
  ComfyUI).** POSITIONING says "audio that is *part of the video* is in scope" and we handle
  cross-shot audio continuity in the stitcher — but we currently rely on the model's native audio
  (H3 ships stereo). **A swappable TTS layer (with voice cloning) for dialogue voiceover is a real
  gap** for films where the model's audio isn't enough.
- **Digital-human lip-sync (multi-language) and motion transfer** (reference video + image →
  animation). Niche but increasingly expected. Mark as plugin territory per POSITIONING §4 —
  partner with the ecosystem rather than build.
- **BGM recommendation + beat-sync** (also a FireRed feature — see §3). The stitcher handles
  audio continuity; an explicit BGM-recommendation step would round out the audio story.

### (d) One-line competitive assessment

> **Adjacent, not a peer.** Pixelle automates *one* short from *one* topic with no quality loop;
> OpenVideo is the judge-driven long-form director it doesn't pretend to be. Borrow the
> installer, the swappable-capability interface, segment typing, and the TTS layer; do not copy
> the "no judge, manual retry" philosophy.

---

## 3. FireRedTeam/FireRed-OpenStoryline — the editing agent (3.2k★)

**One-line read:** A LangChain + MCP conversational *editing* agent that turns natural-language
intent into cut/swap/resequence/style operations on media — the closest of the three to OpenVideo's
"director" language, but built for *editing existing footage*, not generating new video.

**"Intent-driven director" mechanism:** user intent in natural language → agent plans and calls
video-processing *nodes* (`src/open_storyline/nodes/`) → MCP server (`src/open_storyline/mcp/`)
exposes capabilities → stateful conversation memory (`storage/` = "Agent Memory") → prompts in
`prompts/`. The README **does not specify the planning-chain type** (no ReAct vs plan-and-execute
detail, no tool-selection logic, no error-recovery story) — the agent internals are opaque from
this document. Build entry points: `agent.py`, `cli.py`, `agent_fastapi.py` (FastAPI + Uvicorn,
port 8005).

**Tech stack (verified):** LangChain · MCP server · MoviePy + FFmpeg · Python ≥3.11 · FastAPI web
UI · CLI · local ASR via torchaudio (`storyline.local_asr`) · Docker images · TOML config. Agent
Skills format is **open and compatible with OpenClaw, Claude Code, and Codex** — the repo ships
`openstoryline-install` and `openstoryline-use` skills.

**Human-in-the-loop:** "Conversational Refinement" — AI generates → user critiques in plain
language → AI re-edits → repeat. "All edits are performed exclusively via natural language prompts
with immediate results." Tone-described voiceover matching ("Restrained", "Emotional",
"Documentary-style").

**Style Skills:** "Save your complete editing workflow as a custom Skill. Simply swap the media
and apply the corresponding Skill to instantly replicate the style." Functions as a macro/template
system capturing the full decision chain — script style, BGM logic, fonts, pacing, transitions —
into a reproducible artifact enabling batch creation. Pre-built demo styles: Zhongcao, Humorous,
Product Picks, Artistic, Unboxing, Talking Pet, Travel Vlog, Year-in-Review.

### (a) What they do WELL that OpenVideo should borrow

1. **Style Skills as reusable, media-swappable workflows.** This is the **single most relevant
   idea across all three competitors** for OpenVideo. It's a near-perfect productization of our
   `library/` "coherence recipes" strand: serialize the *whole* director workflow (bible template,
   crafter settings, judge thresholds, style LoRA choices, pacing rules) into a portable Skill
   that any user applies to their own concept. **Borrow: make our coherence-recipes into
   first-class Style Skills with an open spec, compatible with Claude Code / Codex / Cursor via
   the same open format.** This directly strengthens POSITIONING §6 Advantage 2 (the compounding
   community library).

2. **MCP server as the editing-capability surface.** `mcp/server.py` → `nodes/` → `storage/` is a
   clean separation: editing primitives (cut, swap, restyle, transition) exposed as MCP tools any
   agent can orchestrate. **Borrow: expose OpenVideo's *director primitives* (plan-shot,
   craft-prompt, judge-shot, refine-shot, stitch) as MCP tools**, not just as a Skill — so a
   creator can drive OpenVideo from inside Claude Code / Cursor with full agent autonomy. This is
   a stronger interface than our current Skill-only story.

3. **Conversational refinement UX.** "All edits via natural language, with immediate results."
   OpenVideo's App is currently concept→film; **a post-generation conversational-edit surface**
   ("make shot 4 warmer", "swap the third beat for a close-up", "tighten the pacing in act 2") is
   a real App feature we're missing. The judge→refine loop is internal; exposing a piece of it as
   a user-facing conversational editor is high-leverage.

4. **ASR-driven rough cut.** "Automatic removal of filler words, disfluencies, and repeated
   sentences, with timestamp-aligned segmentation" via local ASR. For the *footage-to-film* entry
   mode (borrowed from Pixelle §2) this is essential: a creator brings talking-head footage and
   OpenVideo auto-cuts the umms. Standard torchaudio ASR + heuristics; implementable.

5. **Beat-synced BGM recommendation.** Detect content mood, match music, align to beats. Pairs
   with Pixelle's BGM rec to round out the audio story; the stitcher already handles continuity.

6. **Few-shot style transfer for scripts** via reference text. "Define specific copy styles
   (product reviews, casual vlogs) via reference text." This is a smart, cheap way to condition
   the planner's script generation without a fine-tune. Borrow into the crafter.

7. **Tone-described voice matching.** "Restrained / Emotional / Documentary-style" as voice
   descriptors. A cleaner UX than picking a voice model from a dropdown.

### (b) What OpenVideo does BETTER (our advantages)

- **We *generate* video; FireRed *edits* it.** FireRed has **no generative video model**. It
  sources footage by "automatically searching online and downloading images and video clips" —
  it's a re-editor of stock. OpenVideo's whole point (POSITIONING §2) is generating coherent
  video from a concept with H3. Different category.
- **Long-form coherence bible + multi-shot planning.** FireRed's "storyline construction" is for
  sequencing existing clips; it has no acts → sequences → shots planner, no FL2VA continuous
  handoff, no per-shot judges scoring against a quality bar.
- **Open-model baseline.** FireRed routes to LLM + stock. OpenVideo runs H3 locally.
- **Per-shot receipts and reproducible workflows** (POSITIONING §6 Advantage 3). FireRed is
  conversational and stateful but ships no comparable audit/repro artifact.
- **Bigger community trajectory.** 3.2k stars vs our 100k north-star; same age cohort. We are
  behind today on stars, ahead on IP — the question is execution, not category overlap.

### (c) Features we're MISSING (gaps to consider)

- **A conversational post-generation editor in the App.** Currently we generate; we don't
  conversationally *edit* the result. This is the biggest product gap FireRed exposes.
- **Stock-footage sourcing as an input mode.** POSITIONING §4 says we generate video; it doesn't
  forbid *importing* footage as an input (we already accept reference imagery). A "stock + AI"
  hybrid mode (some shots sourced, some generated, judge treats them uniformly) is worth at least
  scoping — it's the realistic shape of most real films.
- **Agent Skills packaged as installable artifacts with a published open format.** Our `SKILL.md`
  is one file; FireRed ships installable skill bundles compatible with multiple agent platforms.
  Borrow the bundle/spec.

### (d) One-line competitive assessment

> **Closest in language, not in lane.** FireRed is an editing agent over sourced footage; OpenVideo
> is a generating director over open models. The borrowable IP is huge and on-theme — Style Skills,
> MCP director primitives, conversational refinement, ASR rough cut — and we should take all of it.

---

## 4. Synthesis — what to borrow, what to ignore, where we win

### 4.1 The five borrowable patterns, ranked

| # | Pattern | From | Impact on OpenVideo |
|---|---|---|---|
| 1 | **Style Skills as open, installable, media-swappable workflows** | FireRed | Highest. Turns our `library/` into a compounding product surface compatible with Claude Code/Codex/Cursor. Reinforces POSITIONING §6 Advantage 2. |
| 2 | **`STYLE.md` brand contract read by crafter + judge** | open-design | Highest. Makes "on-brand" a deterministic property of the render, not a hope. Pairs with our recipes. |
| 3 | **MCP server exposing director primitives** (plan/craft/judge/refine/stitch) | FireRed + open-design | High. Stronger than Skill-only; makes OpenVideo a first-class tool inside other agents. |
| 4 | **Programmatic-shot adapter** (HyperFrames: HTML+CSS+GSAP → headless Chrome → FFmpeg) | open-design | High for long-form economics. Title/transition/overlay shots become free and frame-accurate. |
| 5 | **Batteries-included installer** (bundles ffmpeg + ComfyUI deps + quantized H3) | Pixelle | High for "for everyone". Closes our weakest link (non-technical install). |

### 4.2 Single-feature gaps (consider per POSITIONing §4 test)

- **Conversational post-generation editor in the App** (FireRed) — passes the test: makes OpenVideo
  generate *better* films by letting users steer the judge→refine loop in plain language.
- **Swappable TTS layer with voice cloning** (Pixelle Index-TTS) — passes: improves audio where
  native model audio isn't enough. Within scope (POSITIONING §4: audio that's part of the video).
- **ASR-driven rough cut** (FireRed) — passes *only* if we add a footage-input mode. Otherwise out
  of scope (we generate, not ingest talking-head). Decide on the entry mode first.
- **Beat-synced BGM recommendation** (Pixelle + FireRed) — passes: audio-continuity story.
- **Footage-to-film / stock-source input mode** (Pixelle + FireRed) — passes the test if framed as
  *input*, not as a pivot away from generation. Hybrid stock+AI films are the realistic shape.
- **Storyboard → PDF/PPTX export** (open-design) — passes: a pre-production review surface.
- **Electron/Tauri desktop shell** (open-design) — neutral; defer until creators ask.

### 4.3 What we should explicitly NOT copy

- **The "broad artifact studio" framing.** Open-design does HTML + PDF + PPTX + MP4 + dashboards +
  prototypes + decks. We do video. POSITIONING §4 is correct: depth over breadth.
- **Closed-API routing as the default stack.** Pixelle and open-design both default to closed paid
  APIs (Seedance/Veo/Sora/Kling/DashScope). Our open-model baseline (H3) is the differentiator.
- **"No judge, manual retry" philosophy.** Pixelle's FAQ literally tells users to manually switch
  LLMs and tweak prompt prefixes when quality is bad. That's the gap we exist to close.
- **Editing-only positioning.** FireRed edits sourced footage and has no generative model. Our IP
  is the generative director; don't drift into being a re-editor.

### 4.4 Where OpenVideo is uncontested

None of the three projects has, as a combined product:

1. A **planner → crafter → validator → judge → stitcher** director loop over an **open video model
   at Arena parity with closed** (H3). Closest is FireRed's agent loop, which edits sourced
   footage instead of generating.
2. **Long-form coherent multi-shot generation** with FL2VA continuous handoff across shots. None
   of the three attempt this.
3. **Local-first, no-censorship, no-API-billing** operation as a *product* (not a developer tool).
   Pixelle is local-capable but defaults to paid APIs; open-design is local-first but routes
   generative video to closed APIs; FireRed routes LLM + stock.
4. **Per-shot receipts as a public, reproducible artifact.** None of the three ships anything like
   our open audit trail.
5. A **compounding community library** (LoRAs, reference-packs, coherence recipes / Style Skills)
   as the structural moat. FireRed's Style Skills are the closest analogue and we should adopt and
   extend them.

**Net:** POSITIONING.md is intact. These three projects validate the category and contribute
specific patterns (especially Style Skills, MCP director primitives, programmatic shots, and a
batteries-included installer) that strengthen OpenVideo without forcing a re-positioning.

---

## Appendix — verification receipts

All facts in this document were verified 2026-08-06:

- Star/fork/language/license/created/pushed/topics via `gh api repos/{owner}/{repo>` (output saved
  in research session, JSON inspection confirmed).
- Architecture, pipeline, model lists, and feature quotes via `WebFetch` of each repo's
  `raw.githubusercontent.com/.../main/README.md`.
- OpenVideo positioning referenced from `/mnt/data/workspace/open-video/docs/POSITIONING.md`.

Caveats / gaps in source material:
- **FireRed-OpenStoryline's README is opaque on agent internals.** No ReAct-vs-plan-and-execute
  detail, no tool-selection logic, no error-recovery story. The borrowable value is in *product
  patterns*, not AI internals — labelled as such in §3.
- **Pixelle-Video's last push was 2026-06-14** (~7 weeks stale at time of writing). Maintenance
  signal noted; doesn't change the analysis.
- **Star counts drift.** Re-verify before publishing externally; the qualitative analysis does not
  depend on exact counts.
