# OpenVideo — Growth Playbook (How to Get 100K★)

> **Source of truth for growth tactics.** Distilled from the documented growth arcs of five
> 100K★-class open-source projects (Ollama 178K, ComfyUI 124K, OpenHands 83K, Cline 66K,
> Continue 35K). Every tactic below is grounded in a real move one of those projects made, not
> invented theory. Where a tactic is already in `LAUNCH_PLAN.md` / `COMMUNITY.md`, this doc names
> it and adds the missing piece — it does not duplicate.
>
> Status: v0 / planning · License: Apache 2.0 · North star: **100K★ — the #1 open video community.**
> Companion docs: `LAUNCH_PLAN.md` (day-of choreography), `COMMUNITY.md` (Discord + library),
> `POSITIONING.md` (the "OpenVideo → Runway" analogy), `PARTNERSHIPS.md`.

---

## 0. Executive summary — the one-paragraph thesis

The five projects that crossed 100K★ in <3 years share the same five-move pattern. They
(1) **reduce the install to one command** (Ollama `curl|sh`; ComfyUI desktop; Cline VS Code
extension), (2) **ship a hero demo that proves the thesis** (a working film / resolved GitHub
issue / generated image) and lead every launch surface with it, (3) **embed themselves in a
larger ecosystem rather than fight it** (Ollama on llama.cpp; ComfyUI on every diffusion model;
OpenHands as "open Devin"; Cline on Claude+VS Code), (4) **open a contribution marketplace**
that turns users into producers (ComfyUI's 60K+ custom nodes; Ollama's library; Cline's MCP
servers), and (5) **compound with weekly, datable, sharable releases** (Ollama's per-model blog
posts; ComfyUI's weekly cut; OpenHands SWE-bench updates). OpenVideo is already built for moves
1, 3, and 4 (one-command install, ComfyUI partner, `library/` flywheel). **The two missing
moves are the hero demo as the durable growth engine, and the weekly release rhythm.** Fix those
two and the rest of this playbook compounds. Realistic trajectory: **5–15K★ in the launch month
(PH+HN+Reddit), 30–50K by month 6 if the weekly demo cadence holds, 100K inside 18 months if a
single partner model drop (Wan 2.2 or Hunyuan) lands while the library is hot.**

---

## 1. What the five 100K★ projects actually did

Each project has a **tipping point** (the single event that kicked exponential growth), a
**community mechanic**, a **launch strategy**, a **retention engine**, and **one thing OpenVideo
should copy**. Numbers verified against each repo's public page on 2026-08-06.

### 1.1 Ollama — 178K★, MIT, 8.9M devs, $88M raised

- **Tipping point:** the **one-command install + one-command model run** combination. `curl -fsSL
  https://ollama.com/install.sh | sh` followed by `ollama run llama2` collapsed the "run a local
  LLM" task from a weekend of llama.cpp compilation to 30 seconds. That single UX collapse is what
  turned Ollama from "another llama wrapper" into the default. The second tipping point was the
  **Meta Llama 3 launch partnership** (Apr 2024) — Ollama was the recommended way to run it locally
  day-one, which put it in front of every Llama-launch news cycle.
- **Community mechanics:** Discord (`discord.gg/ollama`), Reddit (`r/ollama`, ~rapid growth
  parallel to the repo), X (`@ollama`). The real mechanic is the **per-model blog post cadence**:
  every new model (Llama, Gemma, Qwen, gpt-oss, Kimi-K2.6, GLM-5.2) gets its own ollama.com/blog
  post, which becomes the share object for that model's launch. Each post = another HN/Reddit/X
  cycle = another star wave.
- **Launch strategy:** no single Product Hunt moment. **Model drops AS launches.** Ollama's blog
  is effectively a launch calendar: each model release is a mini-launch with its own assets. The
  partnership with Meta/OpenAI/NVIDIA/IBM/Google multiplied this — each partner launch funnels
  their developer base into Ollama.
- **Retention:** (a) **ecosystem gravity** — the README lists 100+ community integrations across
  editors, frameworks, RAG tools, databases; (b) the **REST API + official Python/JS SDKs** make
  Ollama trivially embeddable, so projects build on it and become distribution surfaces; (c)
  `ollama launch` (Jan 2026) extended it from "model server" to "coding-agent orchestrator",
  giving existing users a new reason to update.
- **The ONE thing OpenVideo should copy:** **make every model-backend release a launch.** When the
  Wan 2.2 / Hunyuan / LTX-2.3 backend ships, it is NOT a merged PR — it is a blog post + a demo
  film on the new model + a `library/prompts/<model>/` seed pack + an X thread + a ComfyUI-sub
  Reddit post. Ollama's growth curve is literally the sum of its model-launch curves; OpenVideo
  has the same shape available because every backend is a new model launch.

### 1.2 ComfyUI — 124K★, GPL-3.0, 26K newsletter subs

- **Tipping point:** the **custom-node registry reaching critical mass (~60K nodes today)**. Once
  "there's a node for that" became true for almost any media task (image, video, 3D, audio, text),
  ComfyUI stopped being "an app" and became "the platform you have to be on." The second,
  under-appreciated tipping point is the **embedded-workflow-in-PNG mechanic**: every image ComfyUI
  renders has the full workflow JSON baked into the file. That turned every shared render into a
  portable, remixable workflow — a built-in viral distribution for the node graph itself.
- **Community mechanics:** Discord (`#help`, `#feedback`), Matrix, ComfyUI-Manager (the built-in
  node registry), the Substack newsletter (26K+ subs). The **weekly release cadence** (Mondays)
  trains the community to expect fresh drops and creates a recurring reason to visit.
- **Launch strategy:** organic, low-theatre. ComfyUI's growth was driven by the **node ecosystem
  solving real problems faster than closed tools** (Flux, SDXL, video, all day-one). The product
  sold itself via shared renders on r/StableDiffusion and X.
- **Retention:** (a) **partial graph re-execution** (only rerun changed nodes) makes iteration
  cheap; (b) **broad hardware support** (NVIDIA, AMD, Intel, Apple Silicon, even Ascend NPUs) —
  every platform's users are retained; (c) **App Mode** for beginners + node graph for power users
  = two retention surfaces in one product.
- **The ONE thing OpenVideo should copy:** **make every render embed its full recipe.** When
  OpenVideo delivers `film.mp4`, the prompt + coherence bible + per-shot judge scores + the model
  + the LoRAs used should be embedded (as a sidecar JSON or in metadata). A creator who shares
  their film should automatically share a remixable recipe. This is the **single highest-leverage
  viral mechanic in the entire 100K★ playbook**: it turns every output into a distribution surface
  for the input, for free, forever. (ComfyUI 124K★ partly exists because of this one feature.)

### 1.3 OpenHands — 83.3K★, MIT, formerly OpenDevin

- **Tipping point:** the **"open Devin" narrative**. Cognition launched Devin (the "first AI
  software engineer") in Mar 2024 with a viral demo and a closed waitlist. OpenHands launched as
  **OpenDevin** days later, framed explicitly as "the open-source Devin." The narrative was
  pre-built by Cognition's marketing budget — OpenHands just had to occupy it. The second tipping
  point was **SWE-bench leaderboard wins**: every benchmark update where OpenHands rose was a
  shareable artifact that proved "open caught up."
- **Community mechanics:** Slack (not Discord — notable, since most dev projects use Discord), an
  **incubator program** badge, GitHub-first communication. The rebrand from OpenDevin → OpenHands
  preserved search equity (the old name still redirects) while letting the project broaden scope
  beyond "Devin clone."
- **Launch strategy:** Show HN immediately after Cognition's demo, riding the wave of
  "open-source alternative to this thing everyone just saw." The launch surfed a *pre-existing*
  cultural moment rather than trying to create one. Now it's pivoting to Agent Canvas (multi-agent
  control center), which is a second-derivative bet on the agent-orchestration thesis.
- **Retention:** (a) **active sustained development** (7,981 commits, weekly cadence); (b)
  **commercial tier (OpenHands Cloud + Enterprise)** for users who outgrow self-hosting; (c)
  **automations** (Slack, GitHub, Linear, Notion) — once OpenHands is wired into a team's
  workflow, switching cost is high.
- **The ONE thing OpenVideo should copy:** **ride a pre-existing cultural moment at launch.**
  OpenVideo's existing positioning ("OpenCode → Cursor, OpenVideo → Runway") is exactly the
  OpenHands-Devin pattern. The execution lesson: **do not launch into a vacuum**. Time the Show
  HN / X thread to land within 7–14 days of either (a) a closed competitor's price hike
  (Runway/Seedance), (b) a new open model release (Wan 2.2, Hunyuan), or (c) a viral closed
  product demo. Launching into a moment buys you 10× the reach at the same quality.

### 1.4 Cline — 65.8K★, Apache 2.0, ~1 year from launch to 65K

- **Tipping point:** **VS Code Marketplace distribution + riding the Claude 3.5 Sonnet quality
  jump**. Cline launched its VS Code extension in mid-2024 just as Claude 3.5 Sonnet made
  autonomous coding genuinely useful. The marketplace made it discoverable to every VS Code user
  searching "AI coding agent"; the model jump made it actually work. The "Plan and Act" mode with
  **human-in-the-loop approval** (every edit requires a click) solved the trust problem that kept
  autonomous agents niche.
- **Community mechanics:** Discord (`#contributors`), r/cline subreddit, GitHub Discussions. Heavy
  reliance on **community demos on X** — users posting "look what Cline built for me" videos drove
  the next wave of installs. The model-agnostic stance (Anthropic, OpenAI, Google, OpenRouter
  200+, Ollama) meant no model fanbase was excluded.
- **Launch strategy:** marketplace-first, not HN-first. The VS Code Marketplace is a search engine
  with intent already present ("I want an AI coding agent"). Cline optimized for that search, then
  rode organic word-of-mouth.
- **Retention:** (a) **multi-platform** (IDE + CLI + SDK + Kanban board + headless CI/CD) — once
  you use Cline in one place, the others pull you in; (b) **MCP servers** as an extensibility
  surface (databases, APIs, cloud infra) — each MCP integration is a new reason to stay; (c)
  **`.clinerules` files** make the agent project-aware and hard to replace once tuned.
- **The ONE thing OpenVideo should copy:** **be discoverable where intent already exists.** For
  Cline that's the VS Code Marketplace. For OpenVideo it is **ComfyUI-Manager** (the registry
  every ComfyUI user already uses to install custom nodes) and **Hugging Face Spaces** (where
  every model evaluator looks). Ship OpenVideo as a one-click ComfyUI custom node / manager entry
  on day one, and a Hugging Face Space for the hosted try page. Do not make ComfyUI's 124K-star
  user base come to you — go to where they already search.

### 1.5 Continue — 35.4K★, Apache 2.0, now archived (cautionary tale)

- **Tipping point:** **being early** to the "open Cursor" thesis with multi-IDE support (VS Code
  + JetBrains + CLI). At launch, Continue was one of very few open-source AI coding agents. The
  cross-IDE reach (especially JetBrains, which most competitors ignored) captured a real audience.
- **Community mechanics:** contributor graph (contrib.rocks), GitHub-first. Less of a Discord
  culture than Cline/OpenHands.
- **Launch strategy:** product-led, IDE-extension distribution.
- **Retention (the failure mode):** Continue was **overtaken by Cline** despite a head start. The
  README now says the repo "is no longer actively maintained." Why Cline won: Continue stayed
  horizontal (config-driven, multi-provider, cross-IDE) while Cline went vertical (autonomous
  agent with a sharp opinionated UX — Plan/Act mode, checkpoints, multi-agent teams). Continue
  optimized for flexibility; Cline optimized for the 80% use case. **Flexibility loses to
  opinionation when the market matures.**
- **The ONE thing OpenVideo should copy:** **do NOT repeat this.** Stay opinionated. The
  OpenVideo director loop (plan → generate → judge → refine → stitch) is a sharp default. Resist
  the urge to make it a configurable pipeline where every stage is optional. Ship one excellent
  default path; expose the knobs later. Every time someone asks "can I disable the judge?", the
  answer is "no, the judge is the product" — until v0.3 when it becomes a plugin for power users.

---

## 2. Cross-cutting patterns — what all five did

| Pattern | Ollama | ComfyUI | OpenHands | Cline | Continue |
|---|:--:|:--:|:--:|:--:|:--:|
| One-command install | ✅ | ✅ (desktop) | ✅ (npm/Docker) | ✅ (VS Code ext) | ✅ |
| Hero demo on every surface | ✅ (per model) | ✅ (shared renders) | ✅ (SWE-bench) | ✅ (user videos) | ⚠️ (weaker) |
| Rides a pre-existing moment | ✅ (per model) | ✅ (per model) | ✅ (Devin) | ✅ (Sonnet 3.5) | ❌ |
| Embeds in an ecosystem | ✅ (llama.cpp) | ✅ (every model) | ✅ (ACP) | ✅ (VS Code + MCP) | ✅ |
| Contribution marketplace | ✅ (library) | ✅ (60K nodes) | ⚠️ | ✅ (MCP) | ❌ |
| Weekly release cadence | ✅ (per model) | ✅ (Mondays) | ✅ | ✅ | ❌ (lost) |
| Per-render virality (embed recipe) | ⚠️ | ✅ (PNG JSON) | ❌ | ❌ | ❌ |
| Trusted license (MIT/Apache) | ✅ | ❌ (GPL) | ✅ | ✅ | ✅ |
| Multi-platform surfaces | ✅ | ✅ | ✅ | ✅ | ✅ |
| Commercial tier | ✅ (Cloud) | ✅ (hiring) | ✅ (Enterprise) | ✅ (careers) | ✅ |

Three patterns separate the 100K★ club (Ollama, ComfyUI) from the 30–80K tier (OpenHands,
Cline, Continue):

1. **The per-render virality mechanic** — ComfyUI embeds workflows in PNGs; Ollama embeds via its
   API in every integration. OpenHands/Cline/Continue have no equivalent. **This is the single
   highest-leverage mechanic OpenVideo can adopt that no 100K★ project in the agent space has.**
2. **A contribution marketplace with critical mass** — ComfyUI's 60K nodes; Ollama's model
   library. The marketplace turns users into producers and makes the project a platform.
3. **A weekly release rhythm tied to shareable artifacts** — Ollama's per-model posts, ComfyUI's
   Monday cuts. Without it, Continue lost momentum and got archived.

---

## 3. The Top 10 growth tactics for OpenVideo (ranked by expected star impact)

Each tactic has: **why it works** (grounded in the case studies), **expected star impact** (rough
order-of-magnitude over 12 months), **execution plan**, **owner**, and **metric**.

### #1. Embed the full recipe in every render (the ComfyUI-PNG mechanic, for video) — **highest leverage**

- **Why:** ComfyUI's single highest-leverage feature is the workflow JSON baked into every PNG.
  It turned every shared image into a remixable workflow. Video has no equivalent today. OpenVideo
  can be the first.
- **Expected impact:** **+15–25K★ over 12 months** from organic share-remix loops. This is the
  one mechanic that compounds without you spending marketing effort — every user's share is
  distribution.
- **Execution plan:**
  1. **Spec the sidecar.** Define `film.recipe.json` (or use the MP4 metadata box / a `.json`
     sibling): concept, coherence bible, per-shot prompts + judge scores, model+quant+LoRAs,
     engine+workflow-ref, OpenVideo version, license. Decide sidecar vs. embedded early —
     embedded (MP4 `udta`/`moov` atoms, or a WAV-style BWF chunk) is more durable; sidecar is
     easier to ship v0.
  2. **Write it on every render** in `core/stitcher/` — non-negotiable, on by default, no opt-out
     in v0.
  3. **Round-trip it.** `open-video import film.mp4` re-loads the recipe and re-runs / remixed
     the film. This is the "remix" surface.
  4. **Per-shot receipts.** Already planned in the architecture — surface them in the recipe so a
     remix creator can see which shots cleared the judge and which needed refine.
  5. **Landing-page converter.** A `open-video.ai/remix?url=...` page that ingests a shared film
     URL and shows the recipe + a "remix this" button. Every shared film becomes a funnel.
  6. **Launch it as a feature, not a side effect.** Blog post: "Every OpenVideo film carries its
     own recipe. Share the film, share the film school." This is a headline feature, not a
     footnote.
- **Owner:** Core/stitcher lead + a UX writer for the landing copy.
- **Metric:** % of renders with valid embedded recipe (target 100%), # of remix events per week
  (target >0 by week 4, >50 by month 3). **This metric IS the leading indicator of virality.**

### #2. Make every backend release a launch (the Ollama per-model-blog-post cadence)

- **Why:** Ollama's star curve is the sum of its model-launch curves. Each model (Llama, Gemma,
  Qwen, gpt-oss, Kimi, GLM) produced its own HN/Reddit/X cycle. OpenVideo has the same shape
  available: every new backend (Wan 2.2, Hunyuan, LTX-2.3) is a model launch.
- **Expected impact:** **+8–15K★ per major backend launch**, 2–3 launches in year 1 = +20–40K.
- **Execution plan:**
  1. **Lock a launch template for each backend merge:** blog post on `open-video.ai/blog/`,
     one demo film on the new model, a `library/prompts/<model>/` seed pack of 6–10 verified
     prompts, an X thread, a ComfyUI-sub + r/aivideo + r/LocalLLaMA post, a Show HN if the model
     is itself newsworthy.
  2. **Coordinate with the model's own launch.** When MiniMax / Wan / Hunyuan drop a new model,
  OpenVideo's "run it as a multi-minute film, judged" post should land within 24–72h. Be the
  reference use-case the model launcher links to. (Ollama does this with Meta Llama launches.)
  3. **Maintain a public launch calendar** in `docs/` and on the website so the community knows
  what's coming. Anticipation is a distribution asset.
  4. **Backend-agnostic demo format.** Same concept, three models, side-by-side. The "which open
  model makes the best 90s noir?" frame is a recurring shareable.
- **Owner:** Backend lead + social lead.
- **Metric:** # of backend launches per quarter (target ≥1/quarter in year 1); per-launch star
  spike (measure delta-stars in the 72h window).

### #3. Ship as a ComfyUI custom node + Hugging Face Space (go where intent already exists)

- **Why:** Cline won by being searchable in the VS Code Marketplace where intent ("I want an AI
  coding agent") was already present. The ComfyUI equivalent is **ComfyUI-Manager**, used by the
  entire 124K-star ComfyUI base to install extensions. A Hugging Face Space is where every model
  evaluator looks first.
- **Expected impact:** **+5–10K★ in the first 3 months** from users who discover OpenVideo while
  searching ComfyUI-Manager or browsing HF Spaces, not from launch buzz.
- **Execution plan:**
  1. **Package OpenVideo as a ComfyUI custom node** distributed via ComfyUI-Manager registry. The
  existing `engines/comfyui/` adapter is the foundation; add a `nodes/open_video/` entry that
  exposes the director loop as a single high-level node ("plan → generate → judge → stitch") for
  ComfyUI users who want the brain without leaving their graph.
  2. **List it on ComfyUI-Manager's registry** with a clear name, icon, and the demo film as
  preview. This is the single most leveraged discoverability move — ComfyUI users search
  ComfyUI-Manager, not GitHub.
  3. **Deploy a free Hugging Face Space** at `huggingface.co/spaces/open-video/open-video` running
  the `try.html` flow on community GPUs (apply for a ZeroGPU grant). HF Spaces is the default
  discovery surface for model evaluators; being there means every "H3 demo" search finds you.
  4. **Cross-link:** README badges for "Also on ComfyUI-Manager" and "Try on Hugging Face."
- **Owner:** Engine/ComfyUI lead + a DevRel for HF Space setup.
- **Metric:** # ComfyUI-Manager installs/week; HF Space visits/week; conversion to GitHub stars
  from both (track via UTM params on the badge links).

### #4. The hero demo as a durable growth engine, not a launch-day asset

- **Why:** ComfyUI's shared renders and OpenHands' SWE-bench wins are not launch assets — they
  are **recurring shareable artifacts**. The launch plan treats the demo film as a one-time gate.
  It should be a weekly output.
- **Expected impact:** **+5–10K★ over 6 months** from the compounding effect of one share-worthy
  film per week (each is a small launch).
- **Execution plan:**
  1. **Weekly demo ritual:** every Friday, ship one new concept-to-film render to
  `open-video.ai/gallery`, X, r/aivideo, and the Discord `#gallery`. One concept, the resulting
  film, the recipe (see #1), and a one-paragraph "what the judge caught" note.
  2. **Concept sourcing from the community.** Let Discord pick the Friday concept (rotating). This
  turns the weekly demo into a community event, not a marketing broadcast.
  3. **Quality bar:** every weekly demo passes the same cx + Opus 4.8 visual review as the launch
  film (already in `LAUNCH_PLAN.md §0`). Never ship a mediocre demo — it costs more than it earns.
  4. **Quarterly "best-of" reel.** A 3-minute compilation of the quarter's best renders, posted
  to YouTube + X. Long-tail search asset.
- **Owner:** A "demo lead" — distinct from the core engineering lead. This is a real role, not a
  side task; budget 4–8h/week for it.
- **Metric:** weekly demo shipped on time (target ≥45/52 in year 1); per-demo X impressions +
  star delta in the 48h window.

### #5. A real contribution marketplace for prompts, LoRAs, and reference-packs

- **Why:** ComfyUI's 60K custom nodes are its moat. Ollama's model library is its moat. OpenHands,
  Cline, and Continue have weaker marketplaces and weaker retention. OpenVideo already has
  `library/` planned — make it a first-class marketplace, not a docs folder.
- **Expected impact:** **+5–10K★ + significantly higher retention**. A marketplace turns users
  into producers; producers recruit their friends.
- **Execution plan:**
  1. **Define the marketplace primitives:** prompts, LoRAs, reference-packs, coherence-recipes,
  judges. Each is a versioned, reviewable artifact in `library/<type>/<name>/` with a manifest
  (`prompt.md`, `lora.json`, etc.), a preview render, and a license.
  2. **One-click install:** `open-video install <name>` pulls from the registry (a HF dataset or
  GitHub-hosted index). The UX must be as easy as `ollama run <model>`.
  3. **Gallery bot in Discord** (already in `COMMUNITY.md §1`): every merged library PR with a
  render auto-posts to `#gallery`. **This is the single most important loop in the marketplace** —
  contribution → visibility → more contribution.
  4. **Contributor spotlight** weekly (already planned) + a monthly "top contributors" post on
  the blog. Recognition is the currency of open-source marketplaces.
  5. **Quality gate:** every library item ships with a verified render + judge score. No orphan
  prompts. The bar is what makes the library trustworthy vs. a Pinterest board.
- **Owner:** Library lead (likely the founder in v0).
- **Metric:** # of library items; # of contributors; weekly contribution velocity. Target by month
  6: 100+ prompts, 20+ LoRAs, 10+ reference-packs, 30+ contributors.

### #6. The "OpenVideo → Runway" narrative, weaponized

- **Why:** OpenHands became "open Devin" and 83K★ followed. The narrative was pre-built by
  Cognition. OpenVideo's positioning doc already names this pattern ("OpenCode → Cursor,
  OpenVideo → Runway"). The lesson is to **weaponize** it, not just have it in the README.
- **Expected impact:** **+3–8K★** from being the canonical "open Runway/Seedance" in every
  comparison article, tweet, and Reddit thread.
- **Execution plan:**
  1. **Comparison content as a flywheel:** every time Runway/Seedance/Sora announce pricing
  changes, region blocks, watermarks, or model downgrades, OpenVideo publishes a "here's the open
  alternative" response within 24h. Be the default citation.
  2. **Own the search term.** SEO target "open source Runway", "Runway alternative", "Seedance
  alternative", "free AI video generator" — produce definitive comparison pages on
  `open-video.ai/compare/`. (Ollama owns "local LLM"; OpenHands owns "open Devin" — both
  deliberately.)
  3. **Head-to-head films.** Same concept, render on Runway/Seedance AND on OpenVideo, post
  side-by-side. Win or lose, the comparison is shareable. (OpenHands did this with SWE-bench.)
  4. **Press kit + spokesperson.** When a journalist writes "open source video generation in
  2026," OpenVideo should be the first quote. Pre-seed reporters with the positioning doc.
- **Owner:** Founder + content/PR lead.
- **Metric:** # of inbound press mentions; # of "X alternative" searches landing on
  open-video.ai/compare/; share-of-voice in "open video generation" discussions.

### #7. Partnerships with every open-model launcher (the Ollama-Meta pattern)

- **Why:** Ollama's partnerships with Meta, OpenAI, NVIDIA, IBM, and Google put it in front of
  each partner's developer base at every model launch. OpenVideo can do the same with MiniMax,
  Alibaba (Wan), Tencent (Hunyuan), Lightricks (LTX), and the open-video research community.
- **Expected impact:** **+5–10K★** over year 1, concentrated around partner model launches.
- **Execution plan:**
  1. **For each open video model launcher, establish a contact** before their next release. Offer
  OpenVideo as the reference "agent + multi-minute stitch" layer they can link from their launch
  blog. MiniMax H3 is the baseline; cultivate the Wan/Hunyuan/LTX relationships now.
  2. **Co-marketing assets.** When MiniMax (or Wan) launches a model, OpenVideo publishes a
  same-day "running it as a judged multi-minute film" post + demo, and the partner links to it
  from their launch. Both sides win.
  3. **ComfyUI partnership formalization.** ComfyUI is already the engine partner. Take it
  further: co-publish the "OpenVideo node in ComfyUI-Manager" with the ComfyUI team, get their
  X account to amplify, and ship joint demos. The 124K-star ComfyUI base is the single biggest
  warm audience.
  4. **Academic/research partnerships.** OpenHands worked with Stanford Hazy Research. OpenVideo
  should work with the VISTA/VideoWeaver/coherent-video-gen research community — their papers
  become features, and their labs become distribution nodes.
- **Owner:** Founder (this is founder-work, not delegable).
- **Metric:** # of partner co-marketing events per quarter (target ≥1); # of inbound model-launch
  collaborations.

### #8. The Tuesday launch sequence, executed at a moment (not into a vacuum)

- **Why:** The `LAUNCH_PLAN.md` choreography is correct. The missing variable is **when**. Cline
  launched on the Claude 3.5 Sonnet wave; OpenHands launched on the Devin wave. Both surfed a
  cultural moment. Launching into a vacuum throws away 5–10× of the potential reach.
- **Expected impact:** the difference between **3K★ and 15K★ in launch month**.
- **Execution plan:**
  1. **Do not launch until a moment is present.** A moment = (a) a closed competitor's pricing /
  policy change (Runway/Seedance), (b) a major open model release (Wan 2.2, Hunyuan) within 14
  days, OR (c) a viral closed product demo (Sora/Veo) in the prior week. If none of these is
  live, **wait**.
  2. **The launch day stays as `LAUNCH_PLAN.md` prescribes** — PH at 00:01, X at 06:15, four
  reddits, HN at 09:30, Discord all day. The choreography is right.
  3. **One addition to the launch plan: a "moment hook" tweet.** Tweet 1 in the X thread should
  reference the moment explicitly. If a closed competitor just raised prices: "Runway got more
  expensive today. Here's the free, open alternative." If a new model dropped: "Wan 2.2 is here.
  Here's how to run it as a 5-minute film, judged and stitched, on your own GPU."
  4. **Pre-seed the Show HN** with a build comment that names the moment, not just the product.
- **Owner:** Launch lead + founder.
- **Metric:** launch-week star delta (target ≥3K, stretch ≥8K); HN front-page yes/no.

### #9. A free, generous, no-waitlist hosted tier at `open-video.ai/try`

- **Why:** Ollama's hosted features, OpenHands Cloud, and Cline's free tier all serve the same
  function: **let people try in 30 seconds without a GPU**. The local-only story caps growth at
  the size of the GPU-owning population. A free hosted tier expands the funnel 10×.
- **Expected impact:** **+3–6K★ + a much larger email/community funnel.** Most stars come from
  people who tried it hosted and then starred the repo.
- **Execution plan:**
  1. **`open-video.ai/try` is a first-class product**, not a "demo page." It runs the full
  director loop on community/partner GPUs, outputs the film + the embedded recipe (#1), and
  pushes a "Star the repo" CTA at the end of every render.
  2. **No waitlist, no signup for the first render.** Ollama-style: the first taste is free, no
  email gate. Email is requested (not required) to send the recipe + film.
  3. **Rate-limit kindly.** Cap concurrent jobs on the single-5090 (per the launch plan risk
  register); show a real wait-time estimate; queue with a friendly message. Do not let the queue
  become a paywall — that kills the funnel.
  4. **Apply for HF ZeroGPU / community GPU grants** so the hosted tier isn't bottlenecked on one
  machine. Partner with a GPU cloud (Modal, Replicate, RunPod) for free credits in exchange for
  "Powered by" attribution.
  5. **Future SaaS tier (Phase 2 in PLAN.md).** Bring-your-key + our-GPUs options. The free tier
  feeds the paid tier; do not invert.
- **Owner:** Infra lead + product.
- **Metric:** # of first-renders per day on /try; conversion % to GitHub star; conversion % to
  Discord join.

### #10. Trust signals: Apache 2.0, honest limitations, per-shot receipts, commercial-use clarity

- **Why:** Ollama (MIT) and Cline (Apache) are trusted because their licenses are
  commercial-friendly and their docs are honest. OpenHands and ComfyUI (GPL) carry more
  license-friction. **Trust is the silent multiplier** — every enterprise evaluation, every
  "can I use this commercially?" Reddit thread, every press mention hinges on it.
- **Expected impact:** **+2–5K★ + much higher conversion in enterprise/press contexts.** Trust
  doesn't spike stars; it stops leaks.
- **Execution plan:**
  1. **Apache 2.0, no CLA friction, commercial-ok stated in the README hero.** Already done —
  keep it that way. Do not relicense.
  2. **Per-shot receipts on every render** (planned in architecture). Surface them in the UI and
  in the embedded recipe. Receipts = trust, especially for the judge loop (the core IP). A
  skeptic who sees "shot 3: judge score 0.71, refined to 0.88, here's the diagnosis" becomes a
  believer.
  3. **Honest limitations in the launch assets.** The `LAUNCH_PLAN.md` HN build comment already
  does this (15s shot ceiling, wide-shot face corruption, stitched-coherence drift). Keep this
  posture forever — HN/Reddit reward it; marketing-speak gets flag-killed.
  4. **Security posture.** No telemetry by default (opt-in only). State it in the README. (Ollama
  removed anonymous telemetry in its final release; trust trend in the space.)
  5. **Enterprise FAQ.** One page answering: license? commercial use? on-prem? audit? support?
  Make it easy for an enterprise buyer to say yes.
- **Owner:** Founder + legal/ops.
- **Metric:** # of "can I use this commercially?" questions that get a one-link answer;
  enterprise inquiries/month.

---

## 4. The 90-day roadmap (what to do, in order)

| Week | Tactic(s) | Deliverable | Gate |
|---|---|---|---|
| **W0** (pre-launch) | #1 (spec the recipe) | `film.recipe.json` schema decided; round-trip POC in `core/stitcher/` | Round-trip a render → recipe → re-render |
| **W0** | #3 (ComfyUI node + HF Space) | OpenVideo node in ComfyUI-Manager; HF Space live | Install via Manager; /try on HF |
| **W0** | #8 (moment-hook launch) | Launch day executed per `LAUNCH_PLAN.md` at a moment | ≥3K★ in launch week |
| **W1–4** | #4 (weekly demo) + #5 (marketplace seed) | 4 weekly demos; 20 seeded library items; gallery bot live | #gallery has >0 posts/day |
| **W2–6** | #6 (narrative + SEO) + #9 (/try maturation) | 5 comparison pages live; /try GPU grant secured | "Runway alternative" ranks top 5 |
| **W6–10** | #2 (first backend launch — Wan 2.2 or Hunyuan) | Backend + blog + demo film + library seed pack | Backend-launch star spike ≥5K |
| **W8–12** | #7 (partner co-marketing) | First joint post with a model launcher or ComfyUI | Partner-linked traffic >0 |
| **W12** | all | 90-day review: which tactics compounded, which didn't | Decide year-1 bet allocation |

**90-day target:** **15–25K★**, a live marketplace with 30+ contributors, one partner co-marketing
event shipped, the weekly demo cadence locked in. If the recipe-embed (#1) round-trips and the
weekly demo (#4) holds, the path to 100K inside 18 months is realistic.

---

## 5. Anti-patterns — what NOT to copy

- **Continue's horizontalism.** Do not make the director loop a configurable pipeline where every
  stage is optional. Ship one sharp default. (Continue's failure mode.)
- **GPL-style license friction.** Apache 2.0 is a growth decision. Do not switch to GPL or
  AGPL even if a downstream partner asks. (ComfyUI is GPL and still won — but in spite of it, not
  because of it; for a director-layer project, Apache is the right call.)
- **Vanity launches into a vacuum.** If no moment is present, wait. A launch into silence wastes
  the one first-impression. (See #8.)
- **Telemetry-by-default.** Trust trend in the 100K★ class is toward opt-in only. Do not ship
  anonymous telemetry.
- **Marketplace without quality gate.** A `library/` full of orphan prompts without verified
  renders is a Pinterest board, not a moat. Every item ships with a render + a judge score or it
  doesn't ship.
- **Skipping the recipe-embed.** If you skip tactic #1, you give up the single highest-leverage
  viral mechanic in this entire playbook. Do not skip it.

---

## 6. The receipt — what this doc is grounded in

Each project's metrics and mechanics in §1 are drawn from the project's own GitHub README and
official blog/site, fetched 2026-08-06:

- **Ollama** — 178K★, blog arc Aug 2023 → Jul 2026 (8.9M devs, $88M raised), per-model launch
  cadence, ecosystem integrations. Source: github.com/ollama/ollama, ollama.com/blog.
- **ComfyUI** — 124.3K★, GPL-3.0, 60K+ custom nodes, 26K+ newsletter subs, weekly Monday
  releases, embedded-workflow-in-PNG mechanic. Source: github.com/comfyanonymous/ComfyUI,
  comfy.org, blog.comfy.org.
- **OpenHands** — 83.3K★, MIT, formerly OpenDevin, Agent Canvas pivot, SWE-bench-driven early
  narrative, incubator program. Source: github.com/All-Hands-AI/OpenHands.
- **Cline** — 65.8K★, Apache 2.0, VS Code marketplace distribution, MCP servers, multi-platform
  surfaces, Plan/Act mode. Source: github.com/cline/cline.
- **Continue** — 35.4K★, Apache 2.0, multi-IDE (now archived), horizontalism-as-failure-mode.
  Source: github.com/continuedev/continue.

Open-source top-project ranking patterns (educational content, awesome-lists, self-hosted-alternative
positioning) drawn from github.com/EvanLi/Github-Ranking. OpenVideo's current positioning,
launch plan, community plan, and architecture are in this repo's `POSITIONING.md`,
`LAUNCH_PLAN.md`, `COMMUNITY.md`, `README.md`, and `ARCHITECTURE.md` — this playbook is designed
to layer on top of those, not replace them.

---

## 7. One-line summary

**Make every film carry its own recipe (#1), make every backend a launch (#2), go where intent
already lives — ComfyUI-Manager and HF Spaces (#3), ship one great demo every week (#4), and
build a real library marketplace (#5). Hold the rest of the launch plan as written. Do that and
100K★ inside 18 months is a target, not a hope.**
