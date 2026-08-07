# open-video — Product Feature Roadmap

> The 10 must-have features to be the #1 open video generation community + platform, plus the
> **Quality Loop** (judge → refine → best-of-N) as our unique IP.
>
> Status: v0 / planning. Aligned with `PLAN.md` phases. Each feature lists **what it is**, **which
> competitor validates demand**, **our open implementation plan**, and **MVP vs later** priority.

## Priority legend
- **MVP / Phase 0–1** — ship with the open-source core launch. Without these, open-video is not usable as a product.
- **Phase 2** — hosted SaaS / API era. Needed for revenue and non-technical scale.
- **Phase 3** — marketplace / community era. The flywheel that compounds past closed vendors.

---

## The Unique IP — the Quality Loop (judge → refine → best-of-N)

**What it is.** Every generated shot is scored by a vision judge against the prompt intent + a
quality bar. Below bar → **diagnose** (dropped element? bad motion? inconsistency?) → **targeted
refine** (prompt tweak / mode swap / more steps / add reference-pack) → regenerate. Optionally run
**best-of-N** and let the judge pick the winner (VISTA tournament / triple-eval). Productized as
`core/judge.py` + `core/pipeline.py`.

**Why it is the moat (competitor validation):**
- **Google VISTA** (2025) proved judge + best-of-N tournament + triple-eval delivers **+46.3% win
  rate** over single-shot generation — the largest single quality lever in open video research.
- **VideoWeaver** proved an evidence-grounded agent-as-judge closes the open/closed adherence gap.
- **No open video project ships this.** ComfyUI = manual node-graph (no judge); OpenMontage (45K★)
  lacks it; ViMax (11.7K★) is closed-API-only; MiniMax H3 ships as a single-shot engine. Closed
  products (Seedance 2.x, Sora, Veo) have internal judge loops — invisible, unfixable, unauditable.
- **open-video owns this for open models**, and ships it **auditable** (every verdict + receipt
  is in the open `library/`).

**Implementation plan:**
1. **Refine-primary loop (MVP, Phase 0).** Extract frames → judge via vision model
   (`analyze_image` + cross-model `cx` GPT-5.6 / Opus 4.8 per `cross-model-review.md`) → if REFINE,
   structured diagnosis → targeted fix → regenerate. Cheapest path; H3 quality is already at Arena
   parity so the loop fixes adherence/length/consistency, not raw fidelity.
2. **Best-of-N tournament (Phase 1, optional flag).** `--best-of N` — generate K candidates, judge
   ranks them, keep winner. Cost = GPU × K; reserved for high-stakes shots (shot 1 of a film,
   hero shots) where one bad generation breaks continuity.
3. **Judge-LoRA / open judge (Phase 2).** Replace paid vision API with a fine-tuned open judge
   (VideoScore / Qwen2.5-VL) so the loop is free at hosted scale. Unit economics of the hosted tier
  hinge on this.
4. **Receipts as community IP.** Every judge verdict + refine trajectory is logged to
   `library/judge_logs/` → the community studies *what fixes what* → compounding know-how closed
   vendors cannot match.

**Decision (locked, from `PLAN.md`):** **refine-primary, best-of-N optional.** H3 is already at
parity; the loop fixes the agent-layer gap (adherence, length, consistency), which is what differs
between a single shot and a delivered film.

---

## The Top 10 features

### 1. Conversational Agent UX ("describe it, get a film")

**What it is.** Natural language in → finished video out. The user describes a concept in plain
English/Chinese; the agent plans, crafts, validates, generates, judges, refines, stitches, and
delivers — no node graphs, no prompt engineering, no mode selection. Chat-style refinement ("make
shot 3 slower", "change the lighting to golden hour") works on the project, not just one clip.

**Competitor validation:**
- **Seedance 2.x** — closed agentic long-video pipeline; the bar open-video matches open.
- **Sora (ChatGPT)** — conversational generation inside ChatGPT;证明了 NL UX beats node-graph for non-technical users.
- **Runway Gen-3** — polished NL prompt box; but single-shot, no plan/judge/stitch.

**open-video implementation:**
- `core/pipeline.py` is the director; the UX layer is a thin chat front-end that calls it.
- Three surfaces share one brain: **App** (chat GUI), **CLI** (`open-video "..."`), **Skill**
  (SKILL.md for Claude Code / Cursor). All three already enumerated in `README.md`.
- Refinement is **project-scoped**, not clip-scoped: the agent edits the coherence bible and
  re-runs only affected shots (state-vector handoff keeps the rest stable).

**MVP vs later:**
- **MVP (Phase 0–1):** CLI + Skill. Free, ships with the open-source core, targets developers first.
- **Phase 2:** App (web GUI) — the ChatGPT-for-video surface for PMs/creators. This is the
  `open-video.ai/try` page from `PLAN.md`.

---

### 2. Multi-model routing (model-agnostic core)

**What it is.** `core/selector.py` picks the best backend per shot based on declared capabilities.
H3 for audio + prompt adherence; Wan 2.2 for physics; LTX-2.3 for real-time drafts; FLUX3-Dev when
open-weighted. The director survives model churn — the community never has to throw away recipes.

**Competitor validation:**
- **ComfyUI** — multi-model but manual (user wires the node-graph). Validates demand, not the UX.
- **Pika / Runway** — single-model wrappers; brittle when their model ages.
- **MiniMax / Kling / Hailuo** — each a single closed model behind a paywall.

**open-video implementation:**
- `backends/<model>/` plugin contract (`backend.py` ABC + Capabilities + ShotRequest/Result).
- H3 = plugin #1 (ported, proven from early lab).
- Add a model = write a backend plugin (capabilities, prompt_grammar, modes→workflow, constraints).
  Core never changes — this is the architectural seam from `ARCHITECTURE.md`.
- Routing signals: shot needs audio? → H3. Needs long continuous motion? → Wan 2.2. Draft
  iteration? → LTX. Hero shot? → H3 + best-of-N.

**MVP vs later:**
- **MVP (Phase 0):** H3 only (single backend) — but the contract is in place from day 1.
- **Phase 1:** 2nd backend (Wan 2.2 or FLUX3-Dev) to prove model-agnostic. **This is a flagship
  proof-point**: open-video is the only project where the *director* is model-agnostic.
- **Phase 2:** selector.py auto-routing from declared `Capabilities.strengths`.

---

### 3. Infinite canvas (storyboard / timeline workspace)

**What it is.** A spatial workspace where each shot is a node on an infinite canvas, connected by
the coherence bible's act/scene structure. Users drag, reorder, branch (variants), and the canvas
**reflects the director's plan** — not a blank node-graph like ComfyUI, but a populated storyboard
the agent built and the user can edit. Branches = best-of-N variants side by side.

**Competitor validation:**
- **Krea** — real-time canvas, proved the spatial-editing UX beats timeline-only for generative work.
- **Runway (Frames / Gen-3 canvas)** — spatial timeline for sequences.
- **ComfyUI** — infinite canvas but for *wires*, not *story*; this is the gap.

**open-video implementation:**
- Render `planner.py`'s coherence bible as a canvas of shot cards (thumbnail + prompt + verdict).
- Each card is editable: change prompt → re-craft → re-validate → re-judge just that card.
- Branching: right-click a card → "variants" → best-of-N candidates spawn as children; pick one to
  promote. This is the VISTA tournament, visualized.
- FL2VA chain visualized as edges (last-frame → first-frame handoff), making the long-film
  pipeline legible to non-technical users.

**MVP vs later:**
- **MVP (Phase 0–1):** linear storyboard preview (PNG thumbnails per shot, sequential). No canvas.
- **Phase 2:** infinite canvas in the App. The differentiator vs ComfyUI's wire-canvas: **story-canvas**.

---

### 4. Full generation matrix (T2V + I2V + V2V + extend + multi-shot)

**What it is.** Every mode the user might need, behind one coherent director:
- **T2V** — text to video (concept → first shot).
- **I2V** — image to video (keyframe or uploaded image → motion).
- **V2V** — video to video (style/subject transform of existing clip).
- **Extend** — continue a clip beyond the model's native ceiling (15s for H3).
- **Multi-shot** — chain shots into a multi-minute film (the flagship).

**Competitor validation:**
- **Runway Gen-3 / Pika** — ship all five modes; this is the table-stakes matrix.
- **MiniMax H3** — ships T2V/I2V/R2V natively but **single-shot only**; the agent layer is what
  turns these modes into a film.

**open-video implementation:**
- Each mode = a `ShotRequest` mode flag dispatched to the backend's `modes→workflow` map.
- **Extend = FL2VA with first_frame = clip's last frame** (the same primitive as multi-shot).
- **Multi-shot = the flagship `core/pipeline.py`** — FL2VA chain + coherence-bible state-vector
  handoff + per-shot judge. This is the 5-min film engine from `PLAN.md`.
- Validator (`core/validator.py`) is **mode-aware** — duration/ref-counts/timeline/dialogue rules
  differ per mode, hard-gated before generation.

**MVP vs later:**
- **MVP (Phase 0):** T2V + I2V + multi-shot (the long-film pipeline). These three prove the thesis.
- **Phase 1:** extend (cheap once FL2VA chain exists — it's the same primitive).
- **Phase 2:** V2V (style transfer — needs a second model class or control-net adapter).

---

### 5. Frame-level edit propagation

**What it is.** User edits a single frame ("remove the hat from frame 47", "warm the color from
frame 12 onward") and the edit propagates coherently across the shot — and, where the coherence
bible says it should, across downstream shots. This is the successor to inpainting: edit at
frame granularity, get temporal consistency for free.

**Competitor validation:**
- **Runway Gen-3 (Director Mode)** — frame-level inpainting + region editing; the category leader.
- **Descript (for video)** — text-based edit propagation proved the demand for "edit one place, fix everywhere".
- **Pika (Pikaffects / modify region)** — region-targeted edits.

**open-video implementation:**
- Per-frame edit → mask + edit prompt → **regenerate the affected shot** with the edited frame as
  a keyframe (I2V-from-edited-frame) → judge re-checks temporal coherence.
- Cross-shot propagation: if the edit touches a state-vector field (identity / wardrobe / geography
  / story-knowledge / audio), the planner rewrites the bible and flags downstream shots for re-judge.
- Receipts: every propagated edit is logged so the user can audit *why* shot 7 regenerated.

**MVP vs later:**
- **Phase 2:** shot-scoped frame edits (regenerate shot from edited keyframe).
- **Phase 3:** cross-shot state-vector propagation (full "edit once, fix everywhere"). Requires the
  judge loop to re-certify downstream shots — non-trivial GPU cost.

---

### 6. Reference consistency (identity / style / prop lock)

**What it is.** A character, style, or prop stays the same across every shot of a multi-minute
film — the single hardest problem in long-video and the one that most visibly separates amateur
from professional output. Implemented via **reference-packs** (turnaround sheets, lighting boards,
style frames) that the backend consumes as R2V / FL2VA inputs.

**Competitor validation:**
- **Seedance 2.x** — strong character consistency in closed long-video; the bar.
- **Runway (References / Characters)** — explicit "character" inputs for identity lock.
- **MiniMax H3** — ships R2V (reference-to-video) natively; the primitive is there.

**open-video implementation:**
- `library/reference_packs/` — curated turnaround sheets + lighting boards (official seed +
  community contributions). The compounding-moat artifact.
- Planner attaches the relevant reference-pack to each shot's `ShotRequest`; backend maps it to
  H3's R2V mode or FL2VA-with-reference.
- Validator enforces backend ref-count limits (H3: hard cap) before generation.
- Judge includes a **consistency dimension** — does the character in shot N match the reference-pack?

**MVP vs later:**
- **MVP (Phase 0):** reference-pack input → R2V on H3. Proves the primitive.
- **Phase 1:** curated `library/reference_packs/` ships with the open-source core (the flywheel seed).
- **Phase 2:** auto-build reference-packs from the first generated shot of a character (closed-loop
  consistency without user-supplied turnarounds).

---

### 7. One-click effects (camera moves, transitions, styles)

**What it is.** A palette of one-click effects — dolly zoom, rack focus, match cut, film grain,
VHS, anime-style, etc. — that compose into the prompt as *camera prose* and *style modifiers*
rather than post-processing filters. The effect changes generation, not the output.

**Competitor validation:**
- **Pika (Pikaffects)** — one-click visual effects as the brand hook; proved virality of effects.
- **Runway (Gen-3 effects + LUTs)** — cinematic presets.
- **CapCut / Canva** — one-click templates for non-technical creators (the UX bar).

**open-video implementation:**
- `library/style_profiles/` + an `effects/` catalog — each entry is a *prompt fragment* + *mode
  hint* + *validator-aware constraint delta* (e.g. "anime-style" flips style field, "long-take"
  relaxes cut count).
- The crafter (`core/crafter.py`) merges the user's concept + selected effects into the final
  model-specific 3-field prompt — effects are first-class in the prompt, not post-hoc.
- Judge checks effect adherence ("did we actually get a dolly zoom?") — closes the loop.

**MVP vs later:**
- **Phase 1:** ~20 curated effects (camera moves + transitions + 5 style profiles) ship in `library/`.
- **Phase 2:** effect marketplace (community-contributed, curated, with judge-verified thumbnails).
- **Phase 3:** premium effect packs (style LoRAs) — the marketplace revenue line.

---

### 8. Template catalog (start from a finished thing)

**What it is.** A browsable catalog of starting points — "30-second product ad", "60-second
vertical TikTok", "2-minute documentary cold open", "movie trailer" — each a pre-built
**coherence bible** + shot list + style profile + reference-pack. One click → the user's concept
fills the slots → film generates. Templates lower the floor from "describe a film" to "pick a film".

**Competitor validation:**
- **Canva** — template catalog is the entire product; proved templates are how non-technical users
  adopt a creative tool.
- **CapCut** — video templates drove its billions of users.
- **Runway (Templates)** — genre-based starting points for ads/trailers.

**open-video implementation:**
- `library/coherence_recipes/` — pre-built coherence bibles for common film types (the
  `PLAN.md` flywheel seed).
- Each template = a parameterized bible: slots for {subject, brand, mood, duration}. User fills
  slots via chat or form; planner instantiates the full shot list.
- Templates are **community-contributable** under Apache 2.0 — the catalog grows with the community.

**MVP vs later:**
- **Phase 1:** ~10 official templates (ad / trailer / explainer / vertical social / documentary).
- **Phase 3:** template marketplace (premium coherence-recipes = first take-rate revenue line,
  per `PLAN.md` Phase 3).

---

### 9. Community gallery (verified prompt → video)

**What it is.** `open-video.ai/gallery` — every prompt in `library/prompts/` is **tested on H3
and the output is shown alongside the prompt** (prompt → video → quality verdict + judge receipt).
Browsability + one-click remix. This is both the flywheel seed and the **public proof that
open-video works**.

**Competitor validation:**
- **Civitai** — gallery + prompts + LoRAs = the community flywheel that made Stable Diffusion
  win. The single most-copied playbook in open generative.
- **OpenArt** — prompt gallery as product surface (the "OpenArt" half of our positioning).
- **Hugging Face Spaces** — community-runnable demos.

**open-video implementation:**
- Auto-render every merged `library/prompts/` entry on the official GPU; publish video + judge
  verdict + receipts to the gallery.
- One-click "remix" → opens the prompt in `open-video.ai/try` pre-filled.
- Provenance labels (per `data-integrity.md`): each gallery item shows model + settings + GPU +
  judge verdict — honest, reproducible, not a cherry-picked highlight reel.

**MVP vs later:**
- **Phase 1:** static gallery (prompts + rendered videos) — the proof-point that ships with the
  open-source launch.
- **Phase 2:** interactive remix-in-place.
- **Phase 3:** creator profiles + tipping / paid packs (the community-as-platform layer).

---

### 10. Platform export presets (right format, every platform)

**What it is.** One-click export to every platform's exact spec — vertical 9:16 for TikTok /
Reels / Shorts, 1:1 for feed, 16:9 for YouTube, with correct duration caps, codec, bitrate, safe
zones, and caption burn-in. The director plans for the target platform from the start (shot count
and duration budget per platform), not just resizes at the end.

**Competitor validation:**
- **CapCut** — platform export presets are table stakes for any creator tool.
- **Runway / Pika** — export dialogs with aspect + duration presets.
- **Adobe Premiere (Social Media presets)** — the professional bar.

**open-video implementation:**
- Platform presets as a `library/platforms/` data table (aspect, max duration, codec, bitrate,
  safe-zone, caption style).
- The **planner consumes the target platform up front** — a 30s TikTok gets a different coherence
  bible (3 × 8s shots, vertical framing, hook in first 1s) than a 2-min YouTube short.
- `stitcher.py` applies the final encode + caption burn-in via ffmpeg (already a dependency).

**MVP vs later:**
- **Phase 1:** 5 presets (TikTok / Reels / Shorts / YouTube 16:9 / Square) — covers ~95% of demand.
- **Phase 2:** platform-aware planning (planner reads preset before writing the bible).
- **Phase 3:** auto-caption + auto-chapter + multi-language export.

---

## Phase summary (features → phases)

| Feature | Phase 0 (MVP) | Phase 1 (open core) | Phase 2 (hosted) | Phase 3 (marketplace) |
|---|---|---|---|---|
| **Quality Loop** | refine-primary | + best-of-N flag | + open judge (free at scale) | + receipt library |
| **1. Agent UX** | CLI + Skill | CLI + Skill | + App (web GUI) | — |
| **2. Multi-model routing** | H3 only (contract ready) | + 2nd backend | auto-routing | — |
| **3. Infinite canvas** | storyboard preview | storyboard preview | full canvas | — |
| **4. Generation matrix** | T2V + I2V + multi-shot | + extend | + V2V | — |
| **5. Frame-level edit** | — | — | shot-scoped | cross-shot propagation |
| **6. Reference consistency** | R2V primitive | + curated ref-packs | auto ref-packs | premium packs |
| **7. One-click effects** | — | ~20 curated effects | effect marketplace | premium LoRAs |
| **8. Template catalog** | — | ~10 official templates | — | template marketplace |
| **9. Community gallery** | — | static gallery | interactive remix | creator profiles |
| **10. Export presets** | — | 5 platform presets | platform-aware planning | auto-caption/multi-lang |

## What we explicitly do NOT build (focus guardrails)

- **Not an all-modalities platform.** Video generation ONLY — no image-only, no audio-only, no code.
  Closed competitors spread thin; open-video goes deep on the agent layer for video.
- **Not a video editor.** No multi-track NLE, no color grading UI — that's Resolve/Premiere/CapCut.
  We export to them. The canvas is for *story*, not for *cutting*.
- **Not a model trainer.** No training infra — we consume open models (H3, Wan, LTX, FLUX). Style
  LoRAs come from the community via the marketplace, not from us.
- **Not a closed SaaS.** Everything ships Apache 2.0; the hosted tier is convenience, not lock-in.

## Success metric (unchanged from PLAN.md)

**An open-video-generated open film, vision-judged (cx GPT-5.6 + Opus 4.8) as coherent and at least
on-par with a Seedance-generated short on the same concept.** Every feature above exists to make
that true at scale — and to make the next 10,000 such films community-generated.
