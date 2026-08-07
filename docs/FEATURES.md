# open-video — Product Feature Roadmap

> **This document is a roadmap, not a shipped feature list.**  
> OpenVideo v0.0.1 delivers local MiniMax H3 + agent skill harness. Items below describe intent,
> scaffolds, and phases. Aligned with `PLAN.md`. Prefer short technical plans over competitive
> essays.
>
> Status: v0 / planning. Each feature lists **what it is**, **why demand exists**, **open
> implementation plan**, and **MVP vs later**.

## Priority legend
- **MVP / Phase 0–1** — needed for a usable open core (local H3 + honest agent path).
- **Phase 2** — optional hosted / App convenience (not current product).
- **Phase 3** — marketplace / community packaging (future; not a current business claim).

---

## Design target — the Quality Loop (judge → refine → best-of-N)

**What it is.** Every generated shot is scored by a vision judge against the prompt intent + a
quality bar. Below bar → **diagnose** → **targeted refine** → regenerate. Optionally **best-of-N**
and keep the winner. Target surface: `core/judge.py` + `core/pipeline.py`.

**Why build it (research / product context):**
- Judge + best-of-N / refine patterns (e.g. Google VISTA research) improve win rate vs single-shot.
- Most open tools stop at “generate once” (ComfyUI node-graph, raw model engines). Closed products
  often hide internal QC. An **open, auditable** loop is a reasonable open-source goal.
- **v0.0.1 honesty:** the judge is a **scaffold**. Without a wired `vision_fn`, verdicts may PASS
  by default. Do not claim a live quality loop “ships today.”

**Implementation plan:**
1. **Refine-primary loop (MVP).** Extract frames → real vision judge → if REFINE, structured
   diagnosis → targeted fix → regenerate. H3 raw fidelity is already strong; the loop targets
   adherence / length / consistency.
2. **Best-of-N (Phase 1, optional flag).** `--best-of N` for hero shots; cost = GPU × K.
3. **Open judge (Phase 2).** Prefer local/open vision (e.g. VideoScore / Qwen-VL) over paid APIs
   when possible.
4. **Receipts.** Log verdicts + refine trajectories for debugging and later community study.

**Decision (from `PLAN.md`):** refine-primary, best-of-N optional.

---

## The Top 10 features

### 1. Conversational Agent UX ("describe it, get a film")

**What it is.** Natural language in → finished video out. The user describes a concept in plain
English/Chinese; the agent plans, crafts, validates, generates, judges, refines, stitches, and
delivers — no node graphs, no prompt engineering, no mode selection. Chat-style refinement ("make
shot 3 slower", "change the lighting to golden hour") works on the project, not just one clip.

**Demand signal:** closed tools (Seedance, Sora chat, Runway) prove natural-language → video UX
beats node-graphs for non-technical users.

**open-video implementation:**
- `core/pipeline.py` is the long-film orchestrator **scaffold**; single-shot path is reliable today.
- Surfaces today: **CLI** + **Skill** (`h3-video` / `open-video`). **App** and hosted try-as-GPU
  are not shipped (`/try` is a browser mockup).
- Future: project-scoped refine (edit bible, re-run affected shots only).

**MVP vs later:**
- **MVP (Phase 0–1):** CLI + Skill.
- **Phase 2:** App / hosted convenience — not a current claim.

---

### 2. Multi-model routing (model-agnostic core)

**What it is.** `core/selector.py` picks the best backend per shot based on declared capabilities.
H3 for audio + prompt adherence; Wan 2.2 for physics; LTX-2.3 for real-time drafts; FLUX3-Dev when
open-weighted. The director survives model churn — the community never has to throw away recipes.

**Demand signal:** multi-model tools (e.g. ComfyUI) show users want choice; single-model wrappers
age poorly.

**open-video implementation:**
- `backends/<model>/` plugin contract (`backend.py` ABC + Capabilities + ShotRequest/Result).
- H3 = plugin #1 (working).
- Add a model = one backend plugin; core stays stable (`ARCHITECTURE.md`).

**MVP vs later:**
- **MVP (Phase 0):** H3 only — contract in place.
- **Phase 1:** 2nd backend to prove the seam.
- **Phase 2:** selector auto-routing from `Capabilities.strengths`.

---

### 3. Infinite canvas (storyboard / timeline workspace)

**What it is.** A spatial workspace where each shot is a node on an infinite canvas, connected by
the coherence bible's act/scene structure. Users drag, reorder, branch (variants), and the canvas
**reflects the director's plan** — not a blank node-graph like ComfyUI, but a populated storyboard
the agent built and the user can edit. Branches = best-of-N variants side by side.

**Demand signal:** spatial storyboards (Krea, Runway canvas) beat wire-only graphs for creators.

**open-video implementation:**
- Render planner output as shot cards (thumbnail + prompt + verdict).
- Card edit → re-craft / re-validate / re-judge that shot only.
- Optional branching for best-of-N variants.
- FL2VA handoff as edges between cards.

**MVP vs later:**
- **MVP (Phase 0–1):** linear storyboard preview (thumbnails). No canvas.
- **Phase 2:** infinite story-canvas in an App (App itself is Phase 2).

---

### 4. Full generation matrix (T2V + I2V + V2V + extend + multi-shot)

**What it is.** Every mode the user might need, behind one coherent director:
- **T2V** — text to video (concept → first shot).
- **I2V** — image to video (keyframe or uploaded image → motion).
- **V2V** — video to video (style/subject transform of existing clip).
- **Extend** — continue a clip beyond the model's native ceiling (15s for H3).
- **Multi-shot** — chain shots toward longer films (**design flagship**; partial scaffold today).

**Demand signal:** commercial tools expose T2V/I2V/extend matrices; H3 natively covers short
T2V/I2V/R2V shots.

**open-video implementation:**
- Each mode = a `ShotRequest` mode flag → backend workflow map.
- **Extend / multi-shot** share FL2VA last-frame → first-frame chaining in `core/pipeline.py`
  (partial).
- Validator is mode-aware (duration / refs / timeline).

**MVP vs later:**
- **MVP (Phase 0):** reliable T2V + I2V single-shot; multi-shot as best-effort scaffold.
- **Phase 1:** extend + solid multi-shot.
- **Phase 2:** V2V.

---

### 5. Frame-level edit propagation

**What it is.** User edits a single frame ("remove the hat from frame 47", "warm the color from
frame 12 onward") and the edit propagates coherently across the shot — and, where the coherence
bible says it should, across downstream shots. This is the successor to inpainting: edit at
frame granularity, get temporal consistency for free.

**Demand signal:** frame/region edit tools (Runway, Pika, Descript-style) show users want
edit-once consistency.

**open-video implementation (roadmap):**
- Edit frame → regenerate shot from keyframe → re-check coherence when judge is live.
- Cross-shot propagation via state-vector fields later.
- Receipts for audit.

**MVP vs later:**
- **Phase 2:** shot-scoped frame edits.
- **Phase 3:** cross-shot propagation (expensive; needs live judge).

---

### 6. Reference consistency (identity / style / prop lock)

**What it is.** A character, style, or prop stays consistent across shots — hard problem in long
video. Implemented via **reference-packs** (turnaround sheets, lighting boards, style frames) that
the backend consumes as R2V / FL2VA inputs.

**Demand signal:** closed tools expose character/reference locks; H3 already has R2V primitives.

**open-video implementation:**
- `library/reference_packs/` — curated packs + community contributions (as they land).
- Planner attaches packs to `ShotRequest`; backend maps to R2V / FL2VA-with-reference.
- Validator enforces ref-count limits.
- Future judge: consistency dimension vs reference pack.

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

**Demand signal:** one-click effects/presets are table stakes in creator tools.

**open-video implementation:**
- `library/style_profiles/` + effects as prompt fragments + mode hints (generation-time, not only
  post filters).
- Crafter merges concept + effects into the model-specific prompt.

**MVP vs later:**
- **Phase 1:** curated effects in `library/`.
- **Phase 2+:** community effects / style packs (not a revenue claim).

---

### 8. Template catalog (start from a finished thing)

**What it is.** A browsable catalog of starting points — "30-second product ad", "60-second
vertical TikTok", "2-minute documentary cold open", "movie trailer" — each a pre-built
**coherence bible** + shot list + style profile + reference-pack. One click → the user's concept
fills the slots → film generates. Templates lower the floor from "describe a film" to "pick a film".

**Demand signal:** template catalogs lower the floor for non-technical creators.

**open-video implementation:**
- `library/coherence_recipes/` — YAML templates for common film types.
- Parameterized slots ({subject, brand, mood, duration}) when planner UX exists.
- Community-contributable under Apache 2.0.

**MVP vs later:**
- **Phase 1:** ~10 official templates (ad / trailer / explainer / vertical social / documentary).
- **Phase 3:** optional template marketplace (future idea only — not a product claim today).

---

### 9. Community gallery (verified prompt → video)

**What it is.** A public gallery of prompts + rendered results (when the site is ready). Not live
as a full product surface in v0.0.1.

**Demand signal:** Civitai / OpenArt-style galleries help discovery and remix.

**open-video implementation (roadmap):**
- Publish tested `library/prompts/` with media + settings + provenance.
- Remix into local CLI / future App — `/try` stays a mockup until real cloud gen exists.

**MVP vs later:**
- **Phase 1:** static gallery when prompts + assets are ready.
- **Phase 2:** interactive remix.
- **Phase 3:** creator profiles (optional; not a marketplace claim).

---

### 10. Platform export presets (right format, every platform)

**What it is.** One-click export to every platform's exact spec — vertical 9:16 for TikTok /
Reels / Shorts, 1:1 for feed, 16:9 for YouTube, with correct duration caps, codec, bitrate, safe
zones, and caption burn-in. The director plans for the target platform from the start (shot count
and duration budget per platform), not just resizes at the end.

**Demand signal:** platform export presets are table stakes in creator tools.

**open-video implementation:**
- Platform presets as a `library/platforms/` data table (aspect, max duration, codec, bitrate,
  safe-zone, caption style).
- Planner *can* consume target platform up front when multi-shot planning is solid — a 30s TikTok
  gets a different shot budget than a 2-min YouTube cut.
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

- **Not an all-modalities platform.** Video generation focus — not a general image/music studio.
- **Not a video editor.** No multi-track NLE; export to Resolve/Premiere/CapCut.
- **Not a model trainer.** Consume open models; community may train LoRAs elsewhere.
- **Not a closed SaaS.** Apache 2.0 core; any hosted tier is convenience, not lock-in.

## Success metric (from PLAN.md)

A coherent multi-shot open demo with a **real** vision review (not the PASS stub), documented with
receipts — not vanity star-count goals on public docs.
