# open-video — Community Building Plan

> The white-space hub for **open video generation**. The closed world has Runway/Seedance/Sora
> communities behind paywalls; the open world is fragmented across image-focused forums. open-video
> builds the **single home** for open video creators, developers, and researchers — and the
> community itself is a moat closed vendors cannot copy (their know-how is internal; ours is shared).
>
> Brand: **OpenVideo** (public) · **open-video** (code/repo) · **open-video.ai** (domain).
> License: Apache 2.0. Baseline: MiniMax H3 (#1 open video model, Arena parity with closed).
> North star: **100K★ — the #1 open video project + community.**

## Thesis: the community IS the product moat

Closed vendors (Seedance, Sora, Veo) keep their prompt craft, reference-packs, and quality loops
internal. open-video's differentiator is that **every recipe, prompt, LoRA, and coherence bible is
public and shared** (`library/prompts/`, `library/reference_packs/`, `library/coherence_recipes/`).
This compounds: more recipes → more users → more contributions → more recipes. A closed competitor
can clone our Apache-2.0 code; they cannot clone a community that freely publishes its craft.

This is the **OpenArt (product) + OpenCode (business model)** play executed through community:
build the open product, give the business model (free + open + local) to the community, and let the
flywheel run. The plan below operationalizes that flywheel.

---

## 1. Discord server setup

Discord is the home base — it is where ComfyUI's own community already lives, where video creators
expect to share work, and where the library flywheel (§3) gets its daily contributions. **One
server, well-organized, from day one.** Vanity URL `discord.open-video.ai` (redirect).

### Channel map

Categories group the named channels so the server reads top-to-bottom as: orient → make → build →
discuss → govern.

| Category | Channel | Purpose |
|---|---|---|
| **Start here** | `#welcome` | Onboarding flow, role picker, link to this plan + CONTRIBUTING.md. |
| | `#rules` | Short rules + Code of Conduct link (§4). |
| | `#announcements` | Releases, events, milestones. Read-only. |
| | `#roadmap` | Mirror of PLAN.md phases; community reacts on priorities. |
| **Create (for everyone)** | `#showcase` | Post your films/clips. **The front window of open-video.** Reactions only, no critique unless asked. |
| | `#gallery` | Bot-curated mirror of `open-video.ai/gallery` verified prompts — each post = prompt + video + quality verdict. The flywheel's public face. |
| | `#help` | "How do I…" for app/CLI/skill users (non-technical welcome). Triaged by `@Helpers`. |
| | `#prompts` | Prompt craft, 3-field H3 grammar tips, prompt-engineering discussion. Feeds `library/prompts/`. |
| | `#loras` | Style LoRAs, Turbo LoRA, finetune pipeline (HF #27 ka1029). Feeds `library/style_profiles/`. |
| **Build (for makers)** | `#backends` | Model-backend work — H3 today, Wan 2.2 / Hunyuan 1.5 / LTX-2.3 tomorrow (see `backends/`). |
| | `#dev` | Core agent (planner/crafter/validator/judge/stitcher), engine adapters, PR review chatter. |
| | `#bench` | Benchmark profiles + GPU timings (feeds `bench/`). |
| | `#judges` | Quality-judge plugins (VideoScore, custom VLM judges) — the core-IP loop's scorer. |
| **Debate** | `#open-vs-closed` | Open-video vs Runway/Seedance/Sora/Veo/Kling — head-to-heads, Arena watch, "open caught up" thesis. **The recruiting funnel.** |
| **Off-topic** | `#jobs` | Hiring / for-hire (video artists, ML engineers). |
| | `#random` | Everything else. |

### Roles

- `@Founder` / `@Maintainer` — repo write access (mirrors GOVERNANCE.md BDFL → council path).
- `@Helpers` — triage `#help`; granted after sustained good answers. This is the first rung of community leadership.
- `@Contributors` — auto-assigned by GitHub linking (bot) on merged PR. Visible badge, no perms.
- `@Creators` — self-assign; for non-coding artists who contribute prompts/LoRA/showcase work.
- `@Model authors` — for backend/LoRA maintainers (ComfyUI ecosystem authors invited here).
- `@everyone` — read + post; slowmode on `#showcase` (to prevent spam) and `#help` (to let Helpers answer).

### Bots & automation (day-one)

- **GitHub link bot** — PR merge → posts in `#announcements`; issue → `#dev`. Single source of truth = the repo.
- **Gallery bot** — every merged `library/prompts/` PR with a linked render auto-posts to `#gallery` (prompt + video + verdict). Turns contributions into visibility, which turns visibility into more contributions.
- **Contribution tracker** — leaderboard (weekly) of prompt/LoRA/recipe/code contributors; feeds the contributor spotlight (§2).
- **Welcome bot** — DMs new members a 3-step onboarding (pick a role → read `#rules` → post in `#introduce-yourself`).
- **Auto-mod** — spam/raid/links protection (§4).

### Server settings

- Verification level: **Medium** (verified email).
- Default notification = **mentions only** (high-volume servers die in @everyone fatigue).
- `#showcase` slowmode 30s; `#help` slowmode 15s during peak; everything else off.
- Server boost: prioritize upload limit (video showcase needs >25 MB; Nitro boosts get us to 100 MB / 500 MB).

---

## 2. Growth tactics (the programs)

Each program is designed to feed §3 (the flywheel) and recruit from §5 (partnerships). Programs are
**weekly or monthly cadence** — predictable rhythm is what makes a community feel alive.

### Weekly: Film Showcase (Fridays)

- **Format:** every Friday, post a theme ("2-shot horror", "product ad", "20s comedy"). Members
  generate with open-video, drop the clip + their prompt in `#showcase`.
- **Winner:** community vote (reactions) → pinned to `#gallery` + posted to
  `open-video.ai/gallery` + cross-posted to r/comfyui and r/StableDiffusion.
- **Why it works:** generates original, reusable prompts each week (flywheel), produces shareable
  proof that open-video works (marketing), and gives creators a reason to return weekly (retention).

### Monthly: "Open vs Closed" Challenge

- **Format:** pick a Seedance/Sora showcase clip; challenge the community to match or beat it
  **open** with open-video. Publish the prompt + coherence bible + receipt (seed/model/settings).
- **Verdict:** cross-model vision judge (cx GPT-5.6 + Opus 4.8, per the project's evidence standard)
  scores open vs closed blind. Results posted to `#open-vs-closed` + a blog post.
- **Why it works:** this is the project's thesis (open + agent ≥ closed) made tangible every month.
  Win or lose honestly, it recruits: open devs see what's possible; closed users see open is viable.
  Honest losses are as valuable as wins (credibility = the quality-first doctrine in GOVERNANCE.md).

### Quarterly: Hackathon (48–72h)

- **Themes:** "Best new backend" (Wan 2.2 / Hunyuan 1.5 / LTX-2.3 plugin), "Best coherence recipe"
  (new `library/coherence_recipes/*.yaml`), "Best judge plugin", "Fastest preset" (Turbo LoRA +
  Dual-Clock + caching, per `docs/h3_ecosystem.md`).
- **Output:** merged PRs, not slide decks. Every entry integrates an existing ecosystem tool (per
  CONTRIBUTING.md "don't reinvent — integrate as plugin" rule).
- **Sponsors:** GPU credits (runpod/vast/autodl), LoRA authors as mentors. Prize = merging + spotlight.

### Weekly: Contributor Spotlight

- One contributor per week (rotating across prompts / LoRAs / backends / core). Posted in
  `#announcements` + pinned. Links their merged PRs and what they unlocked.
- Recognition is the currency of open-source communities; this makes contribution visible and
  aspirational. Tracks the leaderboard (§1 bot).

### One-off: Office hours + AMAs

- Founder/maintainer office hours weekly (30 min, voice) — `#help` live.
- AMAs with ecosystem authors (ComfyUI-H3-Multishot, Director, quants maintainers, TIGER-AI-Lab
  VideoScore authors). Builds the partnership graph (§5) and pulls their audiences into our server.

### Launch arcs (force-multipliers)

Each ships with a community moment, not just a blog post:
- **Backend launch** (e.g., Wan 2.2 plugin lands) → "race" in `#backends` (H3 vs Wan on same prompt).
- **Version release** → release-notes stream in `#announcements` + a "what's new" clip in `#gallery`.
- **Milestone hits** (100/1K/10K/100K) → celebration event + retrospective blog.

---

## 3. The library flywheel

**More prompts / LoRAs / recipes → more users (the library is the product surface) → more
contributions.** The `library/` directory is the flywheel's physical form; this section makes it spin.

### The loop, concretely

```
library/prompts/ + coherence_recipes/ + reference_packs/ + style_profiles/
        │
        ├── every entry is verified on H3 (render + judge verdict)
        ├── mirrored to open-video.ai/gallery  (public browse/copy/remix)
        ├── posted to Discord #gallery by the bot (visibility)
        │
        ▼
more users find a prompt that works → run it → remix it → PR the remix
        │
        ▼
        back to the top (library grows; searchability grows; SEO grows)
```

### Contribution friction = near-zero (the whole strategy)

This is the single most important mechanic. CONTRIBUTING.md already defines the easiest path:

1. Copy `templates/prompt_recipe.md` → fill in → PR.
2. Bot verifies the render exists + links it.
3. Merged → auto-posted to `#gallery` → contributor gets the spotlight.

**Target: a first-time contributor's PR is merged within 24h, with a human thanking them by name.**
Friction kills flywheels; responsiveness fuels them. A `good first issue` queue and the
`templates/` scaffolding already exist to support this.

### Library growth targets (tied to milestones, §6)

| Milestone | Prompts | Coherence recipes | Reference packs | LoRAs/profiles |
|---|---|---|---|---|
| 100 members | 25 | 5 | 3 | 2 |
| 1K members | 100 | 15 | 10 | 8 |
| 10K members | 500 | 40 | 30 | 25 |
| 100K members | 2,000+ | 100+ | 100+ | 75+ |

Numbers are floors, not ceilings. Each recipe is a SEO page (`open-video.ai/gallery/<slug>`) and a
recruiting asset — the library is simultaneously a product, a moat, and a growth engine.

### Verification gate (quality is the doctrine)

Per GOVERNANCE.md (quality-first, no silent downgrade), **no library entry ships without a verified
render + judge verdict.** A prompt that "sounds good" but doesn't render well is rejected with a
note. This is what makes `#gallery` trustworthy vs a generic prompt dump — and trust is what makes
the flywheel accelerate rather than pollute itself.

---

## 4. Moderation & Code of Conduct

Community quality is the doctrine in `GOVERNANCE.md`; the same applies to the community itself.
Be kind, be constructive, welcome newcomers — and enforce it so the kind people stay.

### Code of Conduct (short, enforceable)

Mirrors CONTRIBUTING.md's stance, expanded for a real-time chat setting:

1. **Be kind and constructive.** Critique work, not people. Assume good faith.
2. **Welcome newcomers.** Non-technical creators and first-time contributors belong here. "RTFM"
   is not an answer; `#help` answers assume the asker is new.
3. **Stay on topic per channel.** Open video generation. `#random` exists for everything else.
4. **No spam, no self-promotion outside `#jobs`.** Posting your open-video film in `#showcase` is
   the point; dropshipping/AI-shilling is not.
5. **No harassment, bigotry, doxxing, or NSFW in non-NSFW channels.** Zero tolerance, instant ban.
   (NSFW policy below.)
6. **Honesty about results.** Do not present closed-model output as open-video output, or hide
   heavy post-processing as "raw generation." This is the community side of GOVERNANCE.md's
   disclosure obligations — credibility is non-negotiable.
7. **License hygiene.** Contributions are Apache 2.0; don't paste GPL/proprietary code or
   copyrighted reference media without rights.

### NSFW policy (decided early — it will come up)

H3 can generate adult content; video-gen communities inevitably ask. Default: **server is SFW; a
single age-gated `#nsfw-showcase` (18+, opt-in, behind a verification gate) is permitted for legal
adult content, hard-banned for anything illegal or non-consensual.** Revisit at 10K members. This
is a pragmatic stance: ignoring it pushes the activity to unmoderated spaces; managing it openly
keeps it bounded. (Founder call; revisit via the §6 milestone review.)

### Enforcement ladder

Warn → mute (1h–24h) → kick → ban. Documented, consistent, no surprise escalations. The quality of
moderation is judged by whether the kind, productive members feel safe enough to stay.

### Moderation team

- 2–3 `@Moderators` at founding (founder + trusted early contributors).
- Scale to a dedicated mod team by 10K (see §6).
- Mod actions logged in a private `#mod-log`; transparency report published quarterly.
- Adopt a standard CoC framework (Contributor Covenant 2.1) as the formal backbone behind the
  short version above, so reporting/escalation has a recognized path.

---

## 5. Partnerships

open-video does **not** compete for the "AI image" or "local LLM" audiences — it partners with
the incumbents and becomes the **video-generation layer** their communities reach for. The
positioning is "we are the open video home; you are the open image / open LLM / engine home — let's
cross-pollinate." Every partnership below is a recruiting funnel into Discord + GitHub.

### Subreddits (figures are approximate; re-verify quarterly before each campaign)

| Subreddit | Size | Angle for open-video |
|---|---|---|
| **r/StableDiffusion** | ~978K | Largest open-gen community, but **image-dominant**. open-video = the video home they lack. Post: weekly showcase winner, "open vs closed" results, H3 prompt craft. Respect 10:1 self-promo norms — lead with value (free prompts, recipes), not asks. |
| **r/LocalLLaMA** | ~787K | Local-first ethos aligned with "open + local + free." Cross-angle: open-video runs local on a 5090, agent layer is model-agnostic. Post the architecture (planner/judge/stitcher) as a local-agent story. |
| **r/comfyui** | ~178K | Our **engine partner**. Most aligned audience. Post: open-video as the "autonomous brain on ComfyUI," backend/adapter work, ecosystem integrations (`docs/h3_ecosystem.md`). This is the #1 conversion sub. |

**Reddit discipline (do not get banned):** read each sub's rules; participate as a member for weeks
before promoting; always link to `library/` value (free recipes) over `discord` invites in the post
body; invite lives in the comments/profile. One misstep on a 978K sub costs the channel.

### ComfyUI Discord (the engine's home)

- Most important single partnership. open-video = the agent brain on their engine; we **add** to
  their ecosystem, we don't fragment it.
- Cross-pin: their `#showcase` ↔ our `#backends`/`#dev`. Maintain presence in their H3-specific
  channels; open-video adapters/plugins land as contributions to their world.
- Co-run events: a "ComfyUI + open-video" hackathon (§2) leverages their reach.

### H3 / MiniMax ecosystem (the model's home)

- Engage HuggingFace discussions (the `docs/h3_ecosystem.md` ecosystem authors: jlucasmcrell,
  seesee75-commits, cushycrux, ka1029, shunyang90, T8mars, etc.). Each is a potential contributor
  and amplifier.
- Invite ecosystem authors into `@Model authors`; their tools become open-video plugins
  (CONTRIBUTING.md's "integrate, don't reinvent" rule). When we integrate someone's tool, we credit
  and link — that reciprocity is the partnership.

### Model-agnostic future partners

- **Wan / Hunyuan / LTX communities** — as those backends land (PLAN.md Phase 1), bring those
  communities in via `#backends`. Each new backend is a new partnership + recruiting lane.
- **TIGER-AI-Lab (VideoScore)** — judge-plugin partner; credibility for our quality loop.
- **Open-source AI orgs** (EleutherAI, LAION, local AI discords) — model-agnostic-agent angle.

### What we do NOT partner with

Closed vendors (Runway/Seedance/Sora). They are the `#open-vs-closed` **comparison target**, not
partners. Keep the line crisp — partnerships are with open ecosystems only.

---

## 6. Milestones (100 → 1K → 10K → 100K)

Each milestone has a **single defining metric, a program focus, and a governance shift.** The
community grows by changing what we optimize for at each stage, not by spamming one tactic.

### Stage 0 → 100 members (the seed) — *now*

- **Metric:** 100 Discord members + 25 prompts in `library/prompts/`.
- **Focus:** **Make the thesis real.** Ship the Phase-0 flagship: a vision-judged coherent 1–5 min
  open film (per PLAN.md make-or-break). That film is the founding recruiting asset — every early
  member joins because they saw it.
- **Programs:** none yet — just `#showcase` + `#help` + responsiveness. Founder answers every
  `#help` post personally inside 24h. This is what makes 100 → 1K possible.
- **Governance:** BDFL (founder, per GOVERNANCE.md).
- **Exit gate:** the flagship film is judged at parity-or-better vs a Seedance short on the same
  concept, and the `library/` has enough recipes that new members can immediately make something.

### Stage 1 → 1K members (the flywheel ignites)

- **Metric:** 1,000 members + 100 prompts + 15 coherence recipes; weekly active contributors ≥ 20.
- **Focus:** **Start the cadence.** Weekly Film Showcase (§2) goes live; first "Open vs Closed"
  challenge ships; first contributor spotlight. The flywheel (§3) becomes visible — members see
  their PRs land in `#gallery`.
- **Programs:** Weekly Showcase + monthly Open-vs-Closed + weekly spotlight.
- **Partnerships:** first intentional r/comfyui + r/StableDiffusion posts (member-first, value-first).
- **Governance:** BDFL + first `@Helpers` and `@Moderators` promoted from active members.
- **Exit gate:** flywheel is self-sustaining — at least 50% of new `library/` entries come from
  non-founding members.

### Stage 2 → 10K members (the movement)

- **Metric:** 10,000 members + 500 prompts + 40 recipes; monthly active contributors ≥ 200.
- **Focus:** **Become the category.** open-video is *the* place open video gen is discussed. The
  "Open vs Closed" results are now a monthly blog/YouTube series with reach. First hackathon ships.
- **Programs:** + quarterly hackathons + AMAs with ecosystem authors + office hours.
- **Partnerships:** formal cross-pins with ComfyUI Discord; recurring r/comfyui + r/LocalLLaMA +
  r/StableDiffusion presence; H3 ecosystem authors as regulars.
- **Governance:** transition BDFL → **community council** (per GOVERNANCE.md); RFC process opens for
  architecture; dedicated mod team (3–5); first Contributor Covenant reporting path live.
- **Exit gate:** a closed-vendor user can name open-video as the open alternative unprompted (brand
  recognition check in r/StableDiffusion / r/comfyui surveys).

### Stage 3 → 100K members (the #1 open video community) — *north star*

- **Metric:** 100,000 Discord members + 100K★ GitHub (the README north star) + 2,000+ prompts.
- **Focus:** **Defend the position.** open-video is the default open video tool and community.
  Library is large enough to be the reference; the quality loop (core IP) is proven at scale.
  PLAN.md Phase 2/3 (hosted SaaS + marketplace) is funded by this community's size and trust.
- **Programs:** full program calendar; global community events; regional/language chapters.
- **Governance:** council + elected seats; working groups (models / judges / library / events);
  foundation consideration if scale demands it.
- **Exit gate:** open-video is the answer to "what's the open alternative to Runway/Seedance," and
  the community is the reason closed vendors cannot catch up on craft (it's all public here).

---

## 7. Operational cadence (how the plan runs)

| Cadence | Event | Owner |
|---|---|---|
| Daily | `#help` triage; PR review within 24h | `@Helpers` / `@Maintainer` |
| Weekly (Fri) | Film Showcase theme + winner | Community lead |
| Weekly | Contributor spotlight | Bot + maintainer |
| Weekly | Office hours (voice) | Founder |
| Monthly | "Open vs Closed" challenge + verdict blog | Founder + judges |
| Monthly | Library flywheel review (did contributions grow? friction up?) | Maintainer |
| Quarterly | Hackathon | Community lead + sponsors |
| Quarterly | Subreddit size re-verification + mod transparency report | Maintainer |
| Per-milestone | Governance review (BDFL → council → seats) | Founder/council |

## 8. Anti-patterns (explicit — these are how video-gen communities die)

- **Becoming an image-gen community.** We are video-only (project focus). Image posts redirect to
  r/StableDiffusion. Drift kills positioning.
- **Promoting over contributing on Reddit.** A 978K sub ban is fatal. Lead with free `library/`
  value, never a Discord invite in the post body.
- **Letting the flywheel pollute.** Unverified prompts in `#gallery` destroy trust. The judge gate
  (§3) is non-negotiable — it's the community face of GOVERNANCE.md's quality doctrine.
- **Competing with ComfyUI.** We are its agent brain, not its rival. Any framing that pits us
  against the engine cuts off our biggest partnership lane.
- **Hiding losses in "Open vs Closed."** Credibility is the asset; honest losses recruit more than
  inflated wins. This mirrors the project's evidence standard (cx + Opus vision-judged).
- **Founder as bottleneck at scale.** Promote `@Helpers`/`@Moderators` by 1K; council by 10K. A
  community that depends on one person's replies caps at that person's bandwidth.

---

## Cross-references

- `README.md` — project pitch, three interfaces, repo layout.
- `PLAN.md` — phased roadmap, competitive map, success metric.
- `GOVERNANCE.md` — quality-first doctrine, disclosure obligations, BDFL→council path.
- `CONTRIBUTING.md` — contribution paths that this plan's flywheel feeds.
- `docs/h3_ecosystem.md` — the ecosystem authors who are this plan's first partners/contributors.
- `library/` (`prompts/`, `coherence_recipes/`, `reference_packs/`) — the flywheel's physical form.
- `templates/prompt_recipe.md` — the zero-friction on-ramp (§3).
