# open-video — Partnership Strategy

> The open alternative to Runway/Seedance. **"OpenArt (product) + OpenCode (business model)."**
> We integrate, we don't reinvent: ComfyUI is the engine, H3/Wan/Hunyuan are the models, open-video
> is the autonomous **director** layer on top. North star: 100K★ — the #1 open video project + community.
> Status: v0 / planning. License: Apache 2.0. Domain: open-video.ai.

## The one principle: partner, don't compete

open-video wins by **growing the open video pie**, not by capturing slices of allies. Every
partnership below is a force-multiplier; every entry into a partner's surface (their Discord, their
model card, their Space, their newsletter) is worth more than a feature we could build alone.

This principle is already encoded in the architecture (see `README.md`, `PLAN.md`, `CONTRIBUTING.md`):

- **We do not fork or replace ComfyUI.** ComfyUI won the engine layer (124k★ / ~$500M, GPL —
  `PLAN.md` L7, L55). We drive it via its HTTP API (`engines/comfyui/`), and the brain it lacks
  (planner → judge→refine loop → stitcher) is our IP, not the node-graph.
- **We do not train competing models.** H3/Wan/Hunyuan are the backends (`backends/<model>/`);
  open-video is model-agnostic by design (`PLAN.md` L30-35). We make *their* model look great.
- **We do not reinvent existing community work** — we wrap it as plugins
  (`CONTRIBUTING.md`: "if it exists and works, integrate it — don't rewrite").

The corollary: **closed vendors win when the open ecosystem fragments.** Every partnership here is
also a defensive move — keeping ComfyUI, the model makers, and HF aligned *with us* rather than
indifferent to us.

## Partnership portfolio

| # | Partner | Their incentive | Our ask | Our offer | Phase |
|---|---|---|---|---|---|
| 1 | **ComfyUI** (comfyanonymous + community) | A killer agent app on their engine → engine stickiness, GPU usage, marketplace reach | Featured/verified extension; mutual GitHub + Discord shoutout | The flagship "autonomous director" showcase for ComfyUI; we send them users | 1 |
| 2 | **Model makers** (MiniMax, Wan-AI/Alibaba, Tencent Hunyuan) | A product layer that makes their open model look great vs closed; ecosystem ammo | Co-marketing (RT/blog/model-card mention); early access to new model versions | Day-1 polished showcase film on each new release; we are "the open product" for their weights | 0→1 |
| 3 | **Content creators** (AI-art YouTubers, AI filmmakers, Reels/TikTok) | Free compute + early access + attribution for novel work | "Made with open-video" + link; permission to feature in our gallery | Early access, GPU credits, prompt-engineering help, creator profile | 0→1 |
| 4 | **HuggingFace** | A flagship open Spaces project that drives traffic to open models | Featured/trending Space; ZeroGPU/community grant consideration | A polished, citable Space that links back to MiniMax/Wan/Hunyuan model pages | 1 |
| 5 | **OSS alliances** (AI Alliance, ASWF, Linux Foundation) | A flagship open-AI / open-media project under neutral governance | Legitimacy, co-marketing, speaking slots, governance templates | A real, shipped flagship their members can rally around | 2→3 |
| 6 | **(self)** The "partner don't compete" doctrine | — | — | A non-fragmenting, complementary stance that makes us the safe hub | always |

---

## 1. ComfyUI — the engine partnership (Tier 1)

**Relationship:** open-video is to ComfyUI what a flagship app is to an OS. ComfyUI owns the engine
and the node-graph community; we own the autonomous director and the non-technical creator audience
ComfyUI can't reach on its own. **Different audiences, same stack — pure complement.**

### Why they'd want us
- ComfyUI's growth ceiling is "power users who can wire a node graph." open-video is the **front door
  for everyone else** (the App/`/try` interface — `PLAN.md` L38) — net-new engine users who would
  never touch a node graph.
- The agent loop (judge → refine → stitch) is the showcase that proves ComfyUI can power
  *autonomous* workflows, not just manual ones — that's a new category for their marketplace.
- Every open-video generation routes through `engines/comfyui/` → more ComfyUI deployments, more
  custom-node installs, more marketplace traffic.

### The asks (concrete, in order)
1. **Listed / verified extension** in the ComfyUI custom-node registry under an "Agent / Autonomous"
   category, so installing open-video is one click from ComfyUI.
2. **Mutual cross-promotion, Phase 1:** a mention in their README/Discord `#showcase` (we star/RT
   them first); we credit "Powered by ComfyUI" in our footer, app, and every receipt.
3. **A joint showcase demo** — the open 5-min flagship film (`PLAN.md` L42-44) rendered *through*
   ComfyUI, with a public workflow + receipt. This is the single best piece of co-marketing content
   for both projects.
4. **Coordination, not coupling:** keep the `engines/comfyui/` adapter thin; track their API changes;
  upstream bug reports, never fork.

### What we never do
- No competing node-graph editor in the App. The App is natural-language → video; power users who want
  nodes are sent *to* ComfyUI.
- No re-implementation of custom nodes that already exist (Turbo LoRA, Dual-Clock Sampler, video
  tiler, etc. — see `docs/h3_ecosystem.md`). We wrap, we don't rebuild.
- No "ComfyUI-killer" framing anywhere — internally or externally.

**Owning principle:** *the engine is theirs; the director is ours; the user is shared.*

---

## 2. Model makers — MiniMax / Wan / Hunyuan (Tier 1)

**Relationship:** open model makers ship raw weights + a notebook. They have no flagship *product*
that makes their model look as good as a closed vendor's demo reel. **We are that product.** Their
model + our director = a delivered multi-minute film that closes the "open vs closed" quality debate
on the day they ship a new release.

### The shared pitch to each maker
> "Your open model is already at Arena parity with closed (`README.md` L29-31). What it lacks is a
> product layer that turns single-shot clips into coherent films. open-video is that layer, open.
> Partner with us: when you ship [H4 / Wan 3 / Hunyuan 2], we ship a polished showcase film the same
> day — and you get the 'open can match closed' story told with your weights, not just your Elo."

### Per-maker specifics
- **MiniMax (MiniMaxAI, HuggingFace org `MiniMaxAI`)** — baseline backend (`backends/h3/`).
  - *Ask:* "Official showcase partner" line on the H3 model card; a co-authored blog/X post on the
    flagship film; early access to H4 weights / quants before public release.
  - *Offer:* Day-0 open-video support for any new H3 mode/major version; our `library/prompts/` H3
    recipes upstreamed to their prompt-writing guide; credit "Baseline model: MiniMax H3" everywhere.
  - *Leverage:* the `awesome-minimax-H3` ecosystem (`docs/h3_ecosystem.md`) — we are the integration
    point that unifies that scattered community tooling into one product.
- **Wan-AI / Alibaba (`Wan-AI`)** — Apache-2.0 "clean-license global anchor" backend
  (`ARCHITECTURE.md` L33). The license-compatibility story is our wedge: open-video is the
  Apache-2.0-clean product layer for the Apache-2.0-clean model.
  - *Ask:* co-marketing around the Wan backend launch in open-video; cross-link from their model card.
  - *Offer:* we prove open-video's model-agnostic claim on Wan (`PLAN.md` L46-47) — concrete evidence
    their model is a first-class citizen, not an H3-only tool.
- **Tencent Hunyuan (`Tencent-Hunyuan`)** — future backend.
  - *Ask/offer:* same template — day-1 showcase, model-card cross-link, "Hunyuan-powered" tier.

### The day-1 launch playbook (reusable for every new model)
1. Backend plugin lands in `backends/<model>/` (capabilities + prompt grammar + workflow).
2. We generate a 1-min (then 5-min) showcase film on the new model, vision-judged
   (`PLAN.md` L70-72).
3. Publish film + prompt + receipt to gallery; tag the maker.
4. Maker RTs / blogs → their audience meets open-video → flywheel.

**Owning principle:** *we are the product layer that makes open weights look unbeatable — every maker wants that ally, not a competitor.*

---

## 3. Content creator outreach — the showcase flywheel (Tier 1→2)

**Relationship:** creators are our marketing channel *and* our gallery seed (`PLAN.md` L39 — the
Verified Prompt Gallery). Their "look what open video can do" posts are how an open project goes
viral without an ad budget. We trade early access + compute + help for attribution + showcase rights.

### Target tiers (in order of ROI)
1. **AI-art / AI-film YouTubers** (long-form tutorials + showcase) — highest credibility, slowest to
   land. Goal: a "I made a short film with open-video" video.
2. **AI-filmmaker / VFX Twitter + indie creators** — fast, viral, set the aesthetic tone.
3. **Reels / TikTok / Shorts AI creators** — volume + reach; 15-30s clips that show motion+audio.
4. **ComfyUI / generative-art community creators** — already our audience; lowest friction, convert
   them to open-video power users.

### The deal we offer creators
- **Early access** to the hosted `/try` + new features (long-film, 2K upscale) before public release.
- **Compute credits / free generations** during the early-access window (we eat the RTX 5090 cost —
  `PLAN.md` L38).
- **Prompt-engineering help** from us (the crafter + validator) to make their concept land.
- **Attribution + profile** in the gallery; we feature their work in our channels.

### What we ask in return
- A **"Made with open-video"** card + link to open-video.ai in the video / description / bio.
- **Permission** to feature the output (with credit) in `library/prompts/` and the gallery.
- Honest disclosure of model/judge settings (matches our own `GOVERNANCE.md` disclosure doctrine).

### Outreach DM template (cold → warm)

> **Subject/DM (≤300 chars for Twitter/Bluesky):**
>
> Hey [name] — your [specific recent piece] is exactly the kind of cohesive long-form AI film we're
> building open-video for: an open-source autonomous director (planner → generate → judge → refine →
> stitch) on MiniMax H3, Apache 2.0. We're opening early access to a handful of creators — free
> compute, day-1 long-film + 2K, your work featured in our gallery. Want in?
>
> ---
>
> **Follow-up (if reply / for YouTube/email):**
>
> Hi [name],
>
> I'm [your name] from open-video (open-video.ai) — the open-source alternative to Runway/Seedance.
> It's an autonomous director: you describe a concept, it plans the shots, generates on the #1 open
> video model (MiniMax H3, at parity with closed), judges each shot with a vision model, refines the
> weak ones, and stitches a coherent multi-minute film with audio.
>
> Why I'm reaching out to you: your [specific piece] shows you care about [coherence / a specific
> style / narrative] — the exact thing the judge→refine loop is built for. We'd love to give you:
>
> - Early access to the hosted app (no setup — type a prompt, get a film)
> - Free compute for the early-access window (we cover GPU cost)
> - Day-1 access to the 5-min long-film pipeline and 2K upscale
> - A creator profile + your work featured in the launch gallery
>
> In return: a "Made with open-video" mention + link, and permission to feature the output (always
> credited). No exclusivity, no content ownership claims — your work stays yours (Apache 2.0 ethos).
>
> If you're open to it, I'll set you up this week. Happy to jump on a 15-min call or async — whatever
> you prefer.
>
> [name] · open-video · open-video.ai · github.com/open-video

### Anti-patterns for creator outreach
- **No paid placements dressed up as organic.** If we pay, we label it sponsored (credibility > reach).
- **No "we'll generate it for you" bait-and-switch.** The point is *they* create with our tool.
- **No exclusivity asks.** Creators who also use Runway/Sora are fine — open-video wins on merit.

---

## 4. HuggingFace — featured Spaces + ecosystem citizen (Tier 2)

**Relationship:** HuggingFace Spaces is the discovery surface for the open-AI world. A
featured/trending open-video Space is "Product Hunt for ML" — distribution + credibility we cannot
buy. We also need HF to be a first-class citizen because that's where MiniMax/Wan/Hunyuan live.

### The asks
1. **Featured / trending Space** — a polished `open-video` Space on HF that mirrors `open-video.ai/try`
   (type a prompt → H3 generates → video returned). Goal: hit the featured/trending rotation.
2. **ZeroGPU / community GPU grant** — for the Space's free-tier generation (qualifies as an
   open-community-use case; we already run an RTX 5090 — `PLAN.md` L38).
3. **Model-collection inclusion** — an open-video-curated HF collection ("open-video's recommended
   open video models + quants") linking to MiniMaxAI/Wan-AI/Tencent-Hunyuan model pages — drives
   traffic to the makers (helps partnership #2) and positions us as a tastemaker.

### What we offer HF
- A flagship, actively-maintained open Spaces project (the kind HF features).
- A good HF citizen: every backend links to the upstream model card; we cite `MiniMaxAI/MiniMax-H3`
  and friends prominently; our gallery drives traffic to model pages.
- We integrate HF-native tooling (VideoScore as judge — `README.md` L23; HF datasets for reference
  packs where license allows).

### Concrete first steps
- Ship the Space as part of Phase 1 (`PLAN.md` L45-47 — "open + community"), pinned to a stable H3
  quant from `docs/h3_ecosystem.md`.
- Submit to HF for featuring once the Space reliably produces a coherent 1-min film.
- Cross-link: Space ↔ open-video.ai ↔ GitHub ↔ model cards (the discovery loop).

**Owning principle:** *be the project HF wants to feature — open, well-built, and pointing traffic at the models HF hosts.*

---

## 5. Open-source community alliances (Tier 3, Phase 2→3)

**Relationship:** as open-video grows past BDFL (`GOVERNANCE.md` L36-39), neutral consortia give
legitimacy, governance templates, co-marketing, and a home if the project ever outgrows single-owner
stewardship. These are *long-game* relationships — start with attendance and contribution, not paid
membership.

### Candidates, by fit
- **The AI Alliance** (IBM + Meta founded, open-AI advocacy; dozens of member orgs).
  - *Fit:* open-video is a textbook flagship — open-licensed (Apache 2.0), open-model, open-weights,
    directly advancing the "open AI ecosystem" mission.
  - *Ask (later):* membership / sponsorship; speak at their events; co-marketing on open-AI showcases.
  - *Now:* follow their working groups, cite their materials, align messaging with "open AI" framing.
- **Academy Software Foundation (ASWF)** (Linux Foundation joint foundation; hosts OpenTimelineIO,
  OpenEXR, OpenColorIO — the open film-pipeline stack).
  - *Fit:* long-term, as open-video becomes the open pipeline for AI-assisted film, alignment with the
    open film stack is natural (e.g., export to OpenTimelineIO).
  - *Ask (later):* present at ASWF events; explore working-group participation; OTIO export as a
    concrete technical bridge.
  - *Now:* nothing paid — but track OTIO and design our stitcher output to be OTIO-friendly.
- **Linux Foundation** (umbrella).
  - *Fit:* the neutral governance home if/when open-video moves beyond BDFL (`GOVERNANCE.md` L38).
  - *Ask (much later):* consider LF-hosted governance / fiscal sponsorship at Phase 3
    (`PLAN.md` L50 — marketplace maturity).
  - *Now:* adopt LF governance/code-of-conduct templates (already done in spirit — `GOVERNANCE.md`,
    `CONTRIBUTING.md`).

### Sequencing rule
Alliances are a Phase 2→3 move. **Do not chase membership logos in Phase 0/1** — they cost time/money
and distract from the only thing that makes any partnership real: a shipped, loved product. Earn the
flagship status first (`PLAN.md` L70-72 success metric), then the alliances come to us.

---

## 6. The "partner don't compete" doctrine (always-on)

This is the meta-partnership — the rule that governs all the others. Stated as a checklist every new
feature/partnership must pass:

1. **Does this duplicate an ally's core?** If yes, stop. We don't build a node-graph engine
   (ComfyUI's), we don't train a base model (MiniMax/Wan/Hunyuan's), we don't build a model-hosting
   hub (HF's).
2. **Does this send users to an ally, or away from one?** Prefer *to*. Power users → ComfyUI; model
   curious → HF model cards; open-AI advocates → AI Alliance. We are the hub, not the walled garden.
3. **Does this fragment the open ecosystem?** If a feature would split the ComfyUI / H3 community,
   don't ship it standalone — upstream or wrap instead (`CONTRIBUTING.md` rule).
4. **Is our IP actually ours?** The brain (planner, judge→refine loop, stitcher, ref-pack builder,
   coherence recipes) is our moat (`PLAN.md` L10-11). Partnering on everything *else* is what lets us
   concentrate investment on the part that's actually defensible.
5. **Would a closed vendor benefit from us fighting this ally?** If yes, that's the signal to stop
   and realign. Closed vendors win when open fragments.

**In one line:** *open-video's moat is the brain + the community recipes. Everything else — engine,
model, hosting, governance — we get from partners, and we make each partner stronger for it.*

---

## Sequencing (aligned to `PLAN.md` phases)

| Phase | Primary goal | Partnerships active |
|---|---|---|
| **0 — thesis proof** (now) | 1-min coherent film, vision-judged | MiniMax (showcase the baseline); first 3-5 creators (early access) |
| **1 — open + community** | open-source core, `library/`, Discord, 2nd backend | ComfyUI (extension listing + cross-promo); HuggingFace (Space + featuring); Wan maker (2nd backend launch); broader creator cohort |
| **2 — hosted** | managed SaaS/API + enterprise license | Deepen all of the above; begin OSS alliance outreach (attend/present) |
| **3 — marketplace** | premium recipes/LoRAs/ref-packs | AI Alliance / ASWF membership; LF governance consideration; maker "official showcase" status mature |

## Metrics — how we know a partnership is working
- **ComfyUI:** open-video extension installs; "Powered by ComfyUI" credit live everywhere; ≥1 joint
  showcase demo shipped; mutual Discord/GitHub cross-post per quarter.
- **Model makers:** ≥1 day-1 showcase film per major model release; model-card backlink from each
  maker; ≥1 co-marketing post (RT/blog) per partnership.
- **Creators:** # creators in early access; # "Made with open-video" posts; gallery entries
  contributed; viral posts (≥100k views) attributable to the program.
- **HuggingFace:** Space live + featured/trending at least once; ZeroGPU grant secured; curated
  model collection published; traffic Space → open-video.ai tracked.
- **Alliances:** attendance/presentation at ≥1 event per org by Phase 2; membership decision
  (in/out, with reasoning) documented by Phase 3.

## Anti-patterns (what we don't do in partnerships)
- No paid creator placements labeled as organic.
- No exclusivity that blocks an ally (no "only on open-video" model locks).
- No claiming partnerships that don't exist — every "partner" claim must point at a real, public,
  mutual signal (a listing, a backlink, a co-post).
- No duplicating an ally's core product, even when it'd be a quick win.
- No chasing alliance/membership logos before there's a shipped flagship to rally around.
