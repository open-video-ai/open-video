# open-video — SaaS / API Plan

> The hosted layer on the open core: **OpenArt (product) + OpenCode (business model)**, for video.
> Apache-2.0 core you can self-host free; a managed convenience layer we run at roughly compute cost.
> Domain: **open-video.ai**. Baseline model: **MiniMax H3** (#1 open, Arena parity with closed).

This document covers (1) the hosted architecture, (2) pricing tiers, (3) why an open model lets us
underprice closed vendors by an order of magnitude, (4) the `/try` page UX, (5) queue management,
(6) the developer API (REST + MCP), and (7) unit economics. Status throughout: **v0 / planning**.
Numbers drawn from repo code are cited to file:line; market/competitor numbers are labelled with
their source or `(verify at launch)`.

---

## 0. The thesis (one paragraph)

Closed video products (Runway, Seedance, Sora, Veo, Kling) charge for three things bundled together:
**the model** (their R&D/licensing), **the compute** to run it, and **the director/UX layer**. We
un-bundle them. The model (**MiniMax H3**) is open and free. The director layer (**open-video core**)
is open and free (Apache 2.0). So the only thing left to charge for, if a user doesn't want to
self-host, is **raw GPU compute** — and we pass that through at thin margins. That is the OpenCode
move (free open core + managed hosted convenience) applied to video generation. The result: a
fair-use **PRO tier at $5/mo** against closed competitors' credit-capped $15/mo plans, and a
genuinely free self-host path closed vendors structurally cannot offer.

---

## 1. Architecture

### Request flow

```
                                  open-video.ai
                                       │
   ┌─────────────────── browser / app / CLI / agent ───────────────────┐
   │                                                                    │
   ▼                                                                    ▼
┌─────────────────────────────┐                            ┌──────────────────────────┐
│  Static front-end           │                            │  Developer clients       │
│  index.html  /try  /gallery │                            │  (REST SDK, MCP hosts)   │
└──────────────┬──────────────┘                            └────────────┬─────────────┘
               │  HTTPS (prompt, preset, model, aspect, dur)            │ REST/MCP
               ▼                                                         ▼
       ┌─────────────────────────────────────────────────────────────────────┐
       │  API GATEWAY  — FastAPI  (server/app.py — the `cli serve` target)    │
       │  • auth (anon/API-key/OAuth)  • rate-limit + quota  • /jobs polling  │
       │  • REST + MCP-over-HTTP        • request validation                  │
       └────────────────────────────┬────────────────────────────────────────┘
                                      │ enqueues Job{plan}
                                      ▼
       ┌─────────────────────────────────────────────────────────────────────┐
       │  QUEUE + ORCHESTRATOR  (Redis + a worker pool / RQ or Celery)        │
       │  • priority lanes (paid > free)  • fairness + back-pressure          │
       │  • capacity scaler (GPU pool size)                                   │
       └────────────────────────────┬────────────────────────────────────────┘
                                      │ dispatches Job to a worker
                                      ▼
       ┌─────────────────────────────────────────────────────────────────────┐
       │  GPU WORKER POD  (one ComfyUI + H3 per GPU)                          │
       │                                                                       │
       │   open-video core/  ──►  backends/h3/  ──►  engines/comfyui/adapter   │
       │   (plan→craft→      (H3 prompt grammar,   (POST /prompt, poll         │
       │    validate→          constraints,          /history/{id}, fetch)      │
       │    generate→          workflows/*.json)                                 │
       │    judge→refine→                                                      │
       │    stitch)                                                            │
       │              │                                                        │
       │              ▼  HTTP :8188                                            │
       │   ┌──────────────────────┐    ┌────────────────────────────────┐     │
       │   │  ComfyUI (engine)    │───►│  MiniMax H3 (model on GPU)     │     │
       │   │  runs the workflow   │    │  INT8 ConvRot (10/20-step)     │     │
       │   └──────────────────────┘    └────────────────────────────────┘     │
       │              │                                                        │
       │              ▼  frames → vision judge (core/judge.py)                 │
       │              ↓  refine loop (0–N times)                               │
       │              ▼  stitcher (ffmpeg + audio continuity)                  │
       └──────────────┬──────────────────────────────────────────────────────┘
                      ▼
       ┌─────────────────────────────────────────────────────────────────────┐
       │  OBJECT STORE  (S3/R2)  →  signed URL  →  front-end / API consumer    │
       │  + per-shot receipt JSON (prompt, settings, judge verdict, timings)   │
       └─────────────────────────────────────────────────────────────────────┘
```

### Components and how they map to the repo today

| Component | Status | Repo seam |
|---|---|---|
| **Static front-end** (`/try`, `/`, `/gallery`) | exists (mockup) | `website/index.html`, `website/try.html` (UI only; "generate" is simulated client-side) |
| **FastAPI gateway** | not yet built | `cli/open_video.py` `cmd_serve()` already probes for `server.app` / `api.app` — that is where the gateway lives |
| **open-video director core** | exists | `core/` (`planner`, `crafter`, `validator`, `judge`, `pipeline`, `stitcher`, `selector`) — see `ARCHITECTURE.md` |
| **H3 backend** | exists | `backends/h3/backend.py` — caps: `max_duration_s=15.0`, `max_short_edge_px=768`, native audio, T2V/I2V/FL2VA/R2V; default `steps=20`, INT8 ConvRot quant |
| **ComfyUI engine adapter** | exists | `engines/comfyui/adapter.py` — `submit()` (POST `/prompt`), `wait()` (poll `/history/{id}`, 1800s timeout, 3s poll), `fetch_outputs()` |
| **Queue + orchestrator** | not yet built | greenfield (Redis + RQ/Celery); the `ComfyUIAdapter.wait()` blocking poll is single-job today and must be lifted into an async worker for concurrency |
| **GPU worker** | exists as a process | today one ComfyUI + H3 per host; the SaaS wraps it as a scalable pool |

### Design rules

1. **The gateway is thin.** Auth, quota, rate-limit, enqueue, poll. All generation logic stays in
   `core/` so self-hosted and hosted run the **same** director. No closed fork.
2. **One ComfyUI + H3 per GPU.** A 32 GB RTX 5090 holds one INT8-ConvRot H3 generation at a time —
   measured peak **~28 GB** at 864×480 (ai-muninn receipt via `research_h3`; the older "~21 GB"
   figure in `docs/h3_ecosystem.md` is unverified and does not match the measured peak). The
   one-job-per-GPU conclusion holds either way; concurrency = number of GPUs, not threads.
6. **⚠️ Hosting jurisdiction is a material constraint.** H3 weights are **license-blocked in the US,
   EU, UK, and South Korea** (H3 `LICENSE §I.3/§I.5`, verified by `research_h3`). Hosted inference
   cannot lawfully run on US/EU/UK/KR servers. See §9 "Material constraint" for mitigations; resolve
   before any paid hosted launch.
3. **Engines are adapters.** Today ComfyUI; a direct diffusers adapter can replace it without
   touching the gateway or the core (`engines/<engine>/` plug-in).
4. **Models are backends.** Today H3; Wan 2.2 / LTX land as `backends/<name>/` and the SaaS inherits
   them unchanged (`core/selector.py` can route per request).
5. **Stateless workers, durable queue.** Workers can be killed/rescheduled mid-job; the queue
   re-dispatches. A job is idempotent via its plan + seed.

---

## 2. Pricing tiers

| | **FREE** | **PRO** | **API / Enterprise** |
|---|---|---|---|
| **Price** | $0 | **$5 / month** | pay-as-you-go per GPU-second (+ volume commit) |
| **Audience** | everyone trying it; the top of the flywheel | creators who use it daily | developers, agencies, integrations |
| **Quota** | **3 generations / day** | **unlimited (fair-use)** | metered, no daily cap |
| **Quality tier** | Draft (fast path, lower res) | Draft + standard-quality on spare capacity | full-quality (20-step), best-of-N, 2K upscale |
| **Queue priority** | lowest (best-effort) | high | highest |
| **Concurrent jobs** | 1 | 2 | per contract |
| **Commercial use** | personal/eval | yes | yes |
| **Self-host alternative** | always free (Apache 2.0) | always free | always free |

**"Draft" tier definition.** Draft = the fastest available path: **10-step INT8 ConvRot today**. The
community "Turbo" 4-step path is adopted **only if `bench/` verifies it from a primary source** (§7);
until then Draft is 10-step, not Turbo. Keeping the tier name mechanism-agnostic means the product
surface does not change if Turbo is confirmed, refuted, or replaced by a faster license-clean
backend.

**Fair-use definition for PRO "unlimited".** "Unlimited" means **no fixed daily cap**, bounded by a
rolling monthly soft-limit tuned so the median PRO user's cost-to-serve stays below revenue (see
§7). Concretely (target, to be confirmed by unit-econ receipts): the expectation is on the order of
**a few hundred short generations per month**; sustained automated/abuse traffic is throttled to the
queue's free lane. The honest framing: PRO is "use it like a human creator, not a scraping farm."

**No model licensing line item.** Because H3 is open, there is no per-seat or per-output royalty to
pass through. The only marginal cost is GPU-seconds (§7).

> The competitor reference ($15/mo entry plan) is the figure named in the positioning brief; it must
> be **re-verified at launch** against the then-current Runway/Seedance pricing pages, since closed
> vendors change credit allotments frequently. `(verify at launch)`

---

## 3. Why we can be ~10× cheaper

Two structural reasons, not a marketing rounding-down:

**(a) The model is free; we charge only compute.** Closed vendors price in three margins: (1) model
R&D amortization / licensing, (2) their inference overhead and profit, and (3) platform/UX premium.
H3's weights cost $0 (Apache-2.0-style open release); open-video's director is $0 (Apache 2.0). Strip
all three margins and what remains is **marginal GPU cost**. A closed vendor physically cannot price
at marginal compute because they have to recover the model.

**(b) The sticker is 3×; the cost-per-generation is ~10×.** Be precise about the "10×":
- On the **monthly subscription**, $5 vs $15 is **3× cheaper**, not 10×.
- On **cost per generated second for a heavy user**, it is ~10× cheaper, because the closed $15 plan
  is **credit-capped** (it buys a bounded allowance of generation seconds) while PRO is
  **fair-use-unlimited**. A daily creator who would burn through the closed credit allowance in a
  week gets the whole month on open-video for $5 → the effective per-generation price collapses.
- And for anyone who opts out of paying us at all: **self-host is $0** (bring your own GPU). Closed
  vendors have no $0 tier beyond a token trial. That is the deepest cut.

**(c) Potential inference-efficiency upside (conditional, not yet verified).** The community
awesome-list (`docs/h3_ecosystem.md`) references a **4-step "Turbo" path** (Turbo LoRA + Dual-Clock
sampler, claimed ~5× faster than the 20-step default). The `research_h3` citation-grade pass **could
not confirm this from a primary source**, so it is **not** part of the base-case unit economics
(§7). If `bench/` measures and confirms it, hosted throughput rises ~5× and the $5 price becomes
comfortable; until then, the price story rests on the measured 10-step anchor plus the other levers
in §7 (owned GPUs, or a license-clean faster backend). Presenting Turbo as already-proven would be
the exact "fabricated throughput in the SaaS plan" failure mode.

**The honest caveat:** "~10× cheaper" is a *thesis* that holds when the unit economics in §7 come
out as modeled. The model R&D and director-layer savings are structural and real; the GPU-cost
arithmetic depends on measured generation time and GPU $/hr, which `bench/` must firm up before we
publish the number on the marketing page.

---

## 4. The `/try` page UX

The vision (per `README.md`): *natural language → video, like ChatGPT/Canva for video — usable by a
non-technical PM.* The target flow is **chat → prompt → preset → generate → video**.

```
┌──────────────────────────────────────────────────────────────────────────┐
│  open-video.ai/try                                          [Sign in] [Go Pro]│
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Chat (the director surface)                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ user: a neon koi swimming through heavy rain at night                 │ │
│  │ director: got it — moody, reflective, slow push-in. I'll lock a       │ │
│  │           cinematic preset, 16:9, ~10s. Draft or full quality?        │ │
│  │ user: draft is fine                                                    │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  ┌─ Compose ────────────────────────┐   ┌─ Director output ─────────────┐ │
│  │ Prompt  [textarea, editable]      │   │ ● directing    shot 01        │ │
│  │ ▸ chips: neon koi · astronaut · … │   │ ┌──────────────────────────┐ │ │
│  │                                    │   │ │ plan      ✓ coherence…   │ │ │
│  │ Preset  [Cinematic ▾]             │   │ │ craft     ✓ H3 3-field    │ │ │
│  │ Model   [MiniMax H3 ▾]            │   │ │ generate  ▸ T2V 54%       │ │ │
│  │ Aspect  [16:9 ▾]   Dur [10s]      │   │ │ judge     ○              │ │ │
│  │                                    │   │ │ refine    ○ best-of-N    │ │ │
│  │ [ ▶ Generate ]   2 / 3 free today  │   │ └──────────────────────────┘ │ │
│  └────────────────────────────────────┘   │ ┌──────────────────────────┐ │ │
│                                            │ │   <video result + receipt>│ │ │
│                                            │ │ model · preset · judge:PASS│ │ │
│                                            │ └──────────────────────────┘ │ │
│                                            └──────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

### The five steps a request goes through (mirrors `website/try.html`'s `STPS` array)

1. **Chat** — the user types naturally. An LLM **planner** turn (`core/planner.py`) confirms intent,
   asks the one or two clarifying questions that matter, and drafts the prompt. This is the
   "ChatGPT-for-video" entry — no node graphs, no jargon. *(Today's `try.html` ships prompt+preset
   only; the chat layer is the next increment.)*
2. **Prompt + preset** — the director rewrites intent into the **H3 3-field prompt**
   (`backends/h3/PROMPT_GRAMMAR.md`), picks a **preset** (cinematic / character / action / landscape
   / abstract / custom — already in `try.html`), and the **validator** hard-gates it against H3's
   constraints (duration ≤15s, ref counts, aspect).
3. **Generate** — the shot is rendered via ComfyUI + H3 (`engines/comfyui/adapter.py` →
   `backends/h3/workflows/`). Progress is streamed to the bar.
4. **Judge → refine** — frames are extracted and a vision judge (`core/judge.py`) scores the take
   vs intent + quality bar; below bar → diagnose → targeted fix → regenerate (optional best-of-N).
5. **Video** — the result is returned inline with a **receipt** (model, preset, aspect, duration,
   judge verdict, timings). One click to remix, one click to copy the prompt for the gallery.

### Quality tiers surface in `/try`
- **FREE**: Draft fast-path (10-step INT8 today; Turbo 4-step if `bench/` verifies), lower
  resolution, best-effort queue.
- **PRO**: draft for iteration, then a **standard-quality** render for the keep; higher queue
  priority.
- The "draft vs full quality" toggle (set via chat) is how we keep the free/PRO cost-to-serve down
  without the user thinking about GPU-seconds.

---

## 5. Queue management (peak load)

The naive failure mode: a viral tweet sends 1000 concurrent requests at one 5090 and every job
times out. The queue is how we survive that without over-provisioning GPUs.

### Lanes and priority

```
                    ┌─────────────── inbound requests ───────────────┐
                    │   FREE    PRO    API/Enterprise                 │
                    └────┬──────────┬──────────┬─────────────────────┘
                         │          │          │
                    ┌────▼──────────▼──────────▼─────┐
                    │   priority queue (Redis ZSET)    │   weighted fair queuing:
                    │   score = lane_weight + age      │   API > PRO > FREE, with
                    └────────────────┬────────────────┘   aging so FREE never starves
                                     │
                    ┌────────────────▼────────────────┐
                    │   GPU worker pool (N GPUs)       │   each worker pulls 1 job,
                    │   capacity scaler                │   runs it to completion,
                    └────────────────┬────────────────┘   fetches next
                                     │
                    ┌────────────────▼────────────────┐
                    │   back-pressure / autoscaler     │
                    └─────────────────────────────────┘
```

- **Weighted fair queuing.** API and PRO jobs jump the FREE lane, but FREE requests age upward in
  priority so a free user still gets served (minutes, not hours) — the `/try` page shows live ETA.
- **Back-pressure, not silent drops.** When the FREE queue depth exceeds a threshold (e.g. > N free
  jobs waiting), the gateway returns **HTTP 202 with a `Retry-After`** and the `/try` UI shows
  "busier than usual — try again in X min / upgrade for instant." We never accept a job we can't
  deliver; we never charge a quota credit for a rejected job.
- **Capacity scaler.** Worker pool size tracks a target latency SLO per lane. FREE is best-effort
  (elastic, spot GPUs); PRO/API SLOs (e.g. p95 start-time < 2 min) drive the minimum reserved pool.
- **Spot/preemptible for FREE, reserved for paid.** FREE runs on the cheapest preemptible capacity
  (killable, re-queued); paid lanes run on reserved GPUs so a preemption never kills a paying job.
- **Idempotent re-dispatch.** A worker dying mid-job (OOM, preemption, crash) re-queues the job;
  `core/pipeline.py` is driven by plan + seed so a fresh worker resumes deterministically.
- **Cost ceiling per job.** A hard cap on judge-refine iterations per job (default low, e.g. ≤2
  refines; best-of-N is a paid toggle) so one pathological request can't burn a GPU-hour. This is
  the same "refine-few, not best-of-many" lever `PLAN.md` Phase 2 calls out as the unit-economics
  hinge.

### Capacity envelope (illustrative, v0 — on the measured 10-step anchor)
One RTX 5090 ≈ one generation at a time. At the **measured** INT8/10-step path (~185 s/gen for a
10 s @ 864×480 clip, §7), one GPU delivers roughly **~10–19 raw generations/hour** (derated to
~5–14 effective after judge/overhead/queue gaps). The 20-step default roughly halves that. **If**
the community "Turbo" 4-step path verifies (~5× faster, currently unconfirmed — §7), throughput
rises to ~70–100/hour. A small pool (e.g. 8 GPUs) absorbs on the order of a hundred concurrent free
users with queuing on the measured path — the `bench/` receipt sizes the real pool.

---

## 6. Developer API (REST + MCP)

### REST

Versioned under `https://api.open-video.ai/v1`. Auth: `Authorization: Bearer <key>` (keys created in
the dashboard; anon `/try` uses a session cookie with the FREE quota).

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/v1/generations` | submit a job → `202` + `{ job_id, status:"queued", eta_s }` |
| `GET` | `/v1/generations/{id}` | poll status (`queued`/`running`/`judge`/`succeeded`/`failed`) + progress + result URL when done |
| `GET` | `/v1/generations/{id}/events` | SSE stream of director steps (plan→craft→generate→judge→refine) |
| `GET` | `/v1/generations/{id}/receipt` | the per-shot receipt (prompt, settings, judge verdict, timings) |
| `GET` | `/v1/models` | list backends + capabilities (mirrors `cli list-models`) |
| `GET` | `/v1/presets` | list prompt presets (mirrors `cli list-presets` / `library/prompts/`) |
| `GET` | `/v1/account/quota` | remaining daily/monthly quota for the key |

**`POST /v1/generations` body** maps 1:1 onto the existing `ShotRequest`/plan the CLI already builds:

```json
{
  "prompt": "A neon koi swimming through heavy rain at night, slow dolly toward the surface...",
  "preset": "cinematic",
  "model": "h3",
  "mode": "t2v",
  "aspect": "16:9",
  "duration_s": 10,
  "quality": "draft",          // "draft" (fast path) | "standard" (20-step) | "high" (+best-of-N)
  "seed": 42,
  "webhook_url": "https://your.app/callbacks/ov"   // optional, for async
}
```

**Webhooks:** when `webhook_url` is set, we POST the final receipt there on completion instead of
forcing polling. **Idempotency:** `Idempotency-Key` header dedupes retries. **Concurrency:** keys
carry a max-concurrent-jobs limit per tier.

### MCP (Model Context Protocol)

open-video already ships as a **skill** (`skill/open-video/SKILL.md` — a prompt-based skill for
Claude Code / agent hosts). The MCP server is the **tool** layer: it exposes the same generation
capability to *any* MCP-compatible host (Claude Desktop, Cursor, etc.) as callable tools, so an
agent can generate video as a first-class action rather than copy-pasting prompts.

```
MCP server:  open-video  (stdio or HTTP transport)
tools:
  generate_video(prompt, preset?, model?, aspect?, duration_s?, quality?)  → job_id
  get_generation_status(job_id)                                            → status + progress
  get_generation_result(job_id)                                            → video URL + receipt
  list_models()                                                            → backends + caps
  list_presets()                                                           → preset catalog
  estimate_cost(prompt, quality)                                           → GPU-seconds + $ (pre-flight)
```

The MCP server is a thin wrapper over the same REST API (same gateway, same auth, same queue), so
agent hosts and human users hit the identical backend. An `estimate_cost` tool lets an agent decide
`draft` vs `standard` before spending quota — useful when an agent is budget-aware.

### Parity guarantee
The REST/MCP surface and the self-hosted CLI (`cli/open_video.py`) call into the **same** `core/`
director. There is no hosted-only feature fork: anything the API can do, the open-source CLI can do
on your own GPU, for free.

---

## 7. Unit economics

This is the section that has to be honest, because the entire pricing story rests on it. The model
below is **parametric**: it states the formula, the assumptions (labelled), and the sensitivity, so
the conclusion can be re-evaluated the moment `bench/` produces measured numbers.

### The per-generation cost formula

```
cost_per_gen  =  G  ×  t_gen  / 3600
                 $/hr   seconds

where  t_gen  =  t_render  +  t_judge_overhead  +  t_queue_margin
       t_render     = render seconds for the chosen quality tier on the chosen GPU
       t_judge_overhead = frame extraction + vision assess + (0..cap) refines
       t_queue_margin   = scheduler/transfer overhead (small)
```

### Anchored data points (cited, with honest labels)

- **Render time — the one measured receipt:** on a single RTX 5090, a **10.125 s clip at 864×480**
  takes **185 s at INT8-ConvRot / 10 steps** (peak **~28.6 GB VRAM**) or **175 s at NVFP4 / 10 steps**
  (~26.9 GB peak). Source: ai-muninn H3-on-5090 benchmark, relayed by the `research_h3` agent
  (primary URL in provenance). **This is 10 steps, not 20, and 864×480, not 1080p.**
- **20-step default (what the repo actually ships, `backends/h3/backend.py`):** doubling steps
  roughly doubles wall time → **~350–370 s** for the same 864×480/10 s clip (`estimate`, not
  separately measured). 1080p is ~5.6× the pixels of 864×480 → expect **several hundred seconds per
  clip** at INT8/20-step before any judge overhead. `needs-hardware-test`.
- **"Turbo 4-step / Dual-Clock ~5× faster":** listed in the community awesome-list
  (`docs/h3_ecosystem.md`), but the `research_h3` citation-grade pass **could not verify these exist
  from a primary source**. **Do not bank unit economics on Turbo.** It is treated below as a
  *conditional upside* for `bench/` to confirm, not as a load-bearing input.
- **VRAM / concurrency:** measured **~28 GB peak** for one 864×480 job ⇒ **one concurrent generation
  per 32 GB GPU** (the older "~21 GB" in `docs/h3_ecosystem.md` is unverified and does not match the
  measured peak; the one-job-per-GPU conclusion holds either way). Concurrency = GPU count.
- **Judge overhead:** H3 ships **no** judge/refine loop — that is a product layer `core/judge.py`
  adds. Frame extraction + vision-model assess + (≤cap) refines is currently **unmeasured**; budget a
  placeholder of **~30–60 s/gen** for a 1-pass draft judge (`estimate, needs measurement`).
- **GPU $/hr (`G`):** the input we cannot fix without a provisioning decision and live market data.
  Web-search budget was exhausted this session, so no rate is verified — the `G` column below is
  **illustrative market-reference, not a quote**. The arithmetic is what matters: plug in a real `G`.

### Cost-to-serve at PRO's fair-use envelope (base case = measured 10-step path)

Assume a PRO user consumes **~150 short generations/month** (≈5/day — a conservative "daily creator"
target). Using the **measured INT8 / 10-step anchor** (~185 s render) + ~45 s judge/overhead ≈
**230 s/gen effective** (this is the *optimistic* sub-1080p case; 20-step/1080p is several× dearer):

| GPU route | `G` ($/GPU-hr) | cost/gen (230 s) | cost / PRO user / mo (150 gens) | vs $5 revenue |
|---|---|---|---|---|
| Own-and-amortize (high util) | $0.20 | $0.0128 | **$1.92** | **+62% margin** |
| Community spot (5090-class) | $0.50 | $0.0319 | **$4.79** | **+4% margin** |
| Cloud on-demand (5090-class) | $1.00 | $0.0639 | **$9.58** | **−92% (loss)** |
| H100 on-demand | $2.50 | $0.1597 | **$23.96** | **−379% (loss)** |

*(The `G` values are illustrative market-reference ranges, **not verified this session**; replace
with real provider quotes at provisioning. The math is what matters: plug your real `G`.)*

**Conditional upside — if Turbo verifies:** were a measured 4-step path to deliver ~5× throughput
(~185 s → ~37 s render, ~80 s effective/gen), the spot row would drop to ~$1.66/PRO-user/mo (+67%
margin) and even cloud on-demand approaches break-even. That is why confirming or replacing Turbo is
the highest-leverage open question — but the price must not be published on the assumption it holds.

### What this says — honestly

1. **On the measured 10-step path, $5/mo unlimited only works on owned/spot GPUs, not on-demand.**
   The margin flips negative at cloud on-demand rates. The OpenCode play is: own the GPUs (capex,
   amortized) or buy spot aggressively; do not resell on-demand compute and try to mark it up.
2. **"Unlimited" must be bounded by fair-use.** "Unlimited" cannot mean "unbounded automated load."
   The ~150-gens/mo target is roughly where margin holds at spot rates on the measured path; the
   queue's back-pressure (§5) enforces it structurally rather than via a hard paywall.
3. **Three credible routes to a defensible $5 price**, any one of which suffices: (a) confirm the
   Turbo fast path and run hosted on it; (b) own the GPUs (capex) so `G` is low; (c) ship a
   license-clean, faster open backend (LTX speed tier, or Wan 2.2) via the model-agnostic seam. The
   `bench/` receipt decides which lever to pull.
4. **Self-host is the floor and the moat.** A user with their own 5090 pays only their own
   electricity (~$0.20/hr amortized) → a few dollars/month for unlimited. We cannot and should not
   try to beat that; we sell *convenience* (no setup, no GPU ownership) for $5. Closed vendors cannot
   offer the self-host path at all.

### Break-even sensitivity (GPU-hours per PRO sub)

At $5/mo and `G = $0.50/hr` (spot, illustrative), break-even is **10 GPU-hours/month per user**. At
the measured ~230 s/gen effective, that is **~156 generations/month**. So fair-use must keep a PRO
user under ~150 gens/mo on the measured 10-step path at spot rates for the tier to stay profitable.
Two knobs defend the line: (a) the fair-use soft cap in the queue (§5), (b) landing one of the three
cost levers above (Turbo / owned GPUs / faster backend).

### What `bench/` must measure before we publish "~10× cheaper" on the marketing page
- [ ] Wall-clock `t_render` on our prod config (INT8 ConvRot, 5090, **1080p**, 10 s) at **10-step**
      and **20-step**. (Replace the 864×480 third-party anchor.)
- [ ] **Confirm or refute the Turbo 4-step / Dual-Clock path** from a primary source, with a measured
      receipt. Until then it stays out of the unit-economics base case.
- [ ] `t_judge_overhead` per generation (frame count + vision-model latency + observed refine count).
- [ ] Real `G` for our chosen provisioning route (owned amortized vs spot vs on-demand).
- [ ] VRAM-confirmed concurrency (1 vs 2 with offload) at 1080p to set GPU-pool sizing.

Until those land in `bench/` receipts, "~10× cheaper" is a **structural thesis** (open model ⇒ no
model margin to recover) that is sound at the line-item level, with the exact multiplier pending
measurement and at least one cost lever (§7 "three routes") in hand.

---

## 8. Rollout phasing (aligns with `PLAN.md`)

- **Phase 0–1 (now / open core):** no hosted SaaS yet. `/try` exists as a static mockup; generation
  runs self-hosted via the CLI against the user's own ComfyUI + H3. The free, open path is the proof.
- **Phase 2 (hosted):** stand up the FastAPI gateway + queue + a small GPU pool. Launch **FREE**
  (3/day, Draft fast-path) to make `open-video.ai/try` genuinely usable by non-technical visitors — the
  "for everyone" vision, and the flywheel top. Add **PRO $5/mo** once unit-econ receipts from `bench/`
  confirm the margin holds. Open the **REST + MCP API** for developers.
- **Phase 3 (marketplace):** take-rate on premium coherence-recipes / style LoRAs / reference-packs
  (`library/`), and enterprise licenses. The hosted tier becomes the distribution surface for the
  community marketplace.

The gating dependency for Phase 2 launch is **`bench/` measured unit economics** (§7 checklist).
Do not publish pricing claims before those receipts exist.

---

## 9. Open questions (need a call)

### ⚠️ Material constraint — H3 license geography (blocks paid hosted launch)
**H3 weights are license-blocked in the US, EU, UK, and South Korea** (H3 `LICENSE §I.3 / §I.5`,
verified by the `research_h3` agent). This is material to a hosted SaaS: we **cannot lawfully run H3
inference for the hosted product on US/EU/UK/KR servers.** Note this is a *geographic use
restriction*, not a per-call royalty — the "no model-licensing line item" thesis (§3) still holds;
what it constrains is *where* we can host. Mitigations (one must be chosen before Phase 2 paid
launch):

1. **Host in a permitted jurisdiction** with latency/cost tradeoffs to US/EU/UK/KR disclosed
   honestly in the product. Simplest, but those are the largest markets.
2. **BYO-GPU / BYO-key architecture.** The SaaS provides the director + UI + queue; the actual GPU
   worker runs on **user- or community-provisioned hardware** in their own jurisdiction. The
   model-license obligation attaches to the entity running inference, not to us as orchestrator.
   Most OpenCode-aligned and most defensible — but means our hosted *compute* is optional
   infrastructure, not the default revenue surface.
3. **Ship a license-clean second backend for restricted regions.** The model-agnostic seam
   (`backends/<model>/`) means a non-blocked open backend (Wan 2.2 is Apache-2.0 clean-license per
   `PLAN.md`'s competitive map; LTX for speed) can serve US/EU/UK/KR while H3 serves permitted
   regions. This is the strongest long-term answer and is already an architectural seam. Quality
   parity vs H3 must be checked per backend.

**Action:** legal review of H3 license terms + a documented hosting-jurisdiction decision before any
paid hosted inference goes live. This is the one item that can block the whole SaaS; everything else
in this doc is engineering.

### Other open questions
1. **Fair-use soft-cap number.** Is ~150 gens/mo (measured-path spot break-even, §7) the right PRO
   ceiling, or does real "daily creator" behavior land higher once FREE launches? Needs usage data.
2. **GPU provisioning route.** Own-and-amortize (capex, best margin) vs spot-heavy (opex, elastic)
   vs hybrid. This single decision dominates the unit-economics table.
3. **Watermark on FREE?** Closed vendors watermark free tiers; the open ethos argues against. Decide
   whether FREE is unwatermarked-best-effort (community goodwill) or watermarked (conversion lever).
4. **Best-of-N as PRO-only or paid-toggle?** It multiplies GPU cost; defaulting it off (refine-primary,
   per `PLAN.md` open decision #2) keeps unit econ defensible.
5. **2K upscale on hosted?** It's an extra GPU pass (`core/stitcher`); probably API/Enterprise only,
   not in the $5 PRO path.

---

### Document provenance
- Repo-cited facts: `README.md`, `PLAN.md`, `ARCHITECTURE.md`, `docs/architecture-overview.md`,
  `docs/h3_ecosystem.md`, `backends/h3/backend.py`, `engines/comfyui/adapter.py`,
  `cli/open_video.py`, `website/try.html`.
- **Render-time anchor (measured):** ai-muninn H3-on-5090 benchmark — **185 s (INT8-ConvRot, 10
  steps) / 175 s (NVFP4, 10 steps)** for a 10.125 s @ 864×480 clip, ~28 GB / ~27 GB peak VRAM,
  relayed by the `research_h3` agent. **10-step, sub-1080p, third-party** — `bench/` must replace
  with our own 20-step/1080p receipt. The repo's shipped default is **20 steps**
  (`backends/h3/backend.py`), which roughly doubles render time (~350–370 s, `estimate`).
- **VRAM correction:** earlier draft cited "~21 GB" from `docs/h3_ecosystem.md`; the measured peak
  is **~28 GB** (ai-muninn). The one-job-per-32 GB-GPU conclusion is unchanged.
- **"Turbo 4-step / Dual-Clock ~5× faster":** community-listed in `docs/h3_ecosystem.md` but
  **unverified from a primary source** (`research_h3`); treated as conditional upside only.
- **H3 license US/EU/UK/KR exclusion:** `research_h3` lane, H3 `LICENSE §I.3 / §I.5` — material to
  hosting jurisdiction (§9).
- GPU $/hr values: **illustrative market-reference ranges, not verified this session** (web-search
  budget exhausted); re-verify at provisioning.
- Competitor $15/mo figure: from the positioning brief — **re-verify at launch**.
