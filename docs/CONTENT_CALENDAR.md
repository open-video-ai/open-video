# OpenVideo — Content Calendar

> **Goal:** become the **#1 video-generation community + platform** — the open alternative to
> Runway/Seedance. Content is the growth engine: every post either *proves the thesis*
> (open + agent ≥ closed) or *lowers the barrier to contribute* (a new LoRA, a 3-line prompt, a
> single-GPU run). The product is Apache 2.0; the moat is the community library and the
> judge→refine loop. Content compounds both.
>
> **Positioning locked in every asset:** *OpenVideo = "OpenArt (product) + OpenCode (business
> model)."* Brand: **OpenVideo** (public) / **open-video** (code). Domain: **open-video.ai**.
> Baseline: **MiniMax H3** (#1 open video model, Arena parity with closed — T2V Elo 1238 / I2V
> 1189). Engine: **ComfyUI** (124k★). Core IP: **planner → craft → validate → judge → refine →
> stitch** loop. North star: **100K★**.

---

## 0. The one viral formula (read this first)

Every high-performing OpenVideo asset is built from the same five-part formula. Memorize it.

> **Hook:** *"100% open-source + free + runs on a single GPU."*
> **Proof:** a clip/film that looks too good to be "free and open."
> **Contrast:** the same prompt on a closed tool (Seedance/Sora/Veo) — side-by-side, let viewers guess.
> **Mechanism:** one sentence on *why* it works (the agent layer: plan → judge → refine → stitch).
> **CTA:** *"Star the repo / join the Discord / try it free at open-video.ai/try."*

If a planned post can't be rewritten into that shape, it's a support doc, not content. Send it to
the docs site and pick a different post.

**The three claims we never make without a receipt:**
- "Beats/beats-closed" → must cite the Arena Elo or a blind-test result.
- "Single GPU" → must name the GPU (e.g., "1× RTX 5090, 32GB") and the wall-clock time.
- "Coherent multi-minute film" → must be vision-judged (cx GPT-5.6 + Opus 4.8) per the project's
  anti-hallucination/done-claim gate. Never ship a film as "done" without that receipt.

---

## 1. Channels & formats (where this content lives)

| Channel | Primary format | Cadence | Owner | KPI |
|---|---|---|---|---|
| **X / Twitter** (`@openvideo_ai`) | Threads (build-in-public, blind tests, drops) | 4–6×/week | Growth lead | impressions, profile visits, repo stars attributed |
| **YouTube** (`OpenVideo`) | Shorts (≤60s) + long-form tutorials + film premieres | 1 short/wk, 1 long-form/2 wks | Video editor | watch time, subs, CTR to repo |
| **open-video.ai** | `/try` (free gen), `/gallery` (verified prompts), `/films` (premieres) | continuous | Web lead | gen completions, gallery remixes |
| **GitHub** (`open-video`) | Releases, Discussions, Showcase category | per-release + daily triage | Eng lead | ★ stars, PRs, contributors |
| **Discord** | `#showcase`, `#help`, `#lora-lab`, `#bench-racing` | continuous | Community lead | DAU, LoRAs submitted, films shared |
| **r/StableDiffusion, r/LocalLLaMA, HuggingFace** | Cross-posts + model/LoRA cards | when earned | Growth lead | upvotes, downloads |
| **Hacker News** | Launch posts, "Show HN", benchmark write-ups | ~monthly, earned only | Founder | front-page与否, stars spike |

**Golden rule of cross-posting:** the **canonical** home of every asset is `open-video.ai` (or the
GitHub release). Every social post links *back* to it. We never let a thread be the only copy of a
benchmark or a film — those are durable IP that must outlive any platform's algorithm.

---

## 2. The seven content pillars

### Pillar 1 — "OpenVideo Weekly" (the heartbeat)

**What:** a weekly digest thread (X) + companion YouTube Short, published every **Friday 09:00 PT**.
It is the single most important recurring asset: it gives the community a reason to come back every
week and gives prospects a predictable entry point.

**Why it works:** frequency + predictability beats virality for community trust. The Weekly is the
container for everything in pillars 2–6.

**Thread structure (7 tweets):**
1. **Opener** — one clip (best of the week) + the hook ("open-source, free, 1 GPU"). Tag the creator.
2. **Community spotlight** — 2–3 standout user outputs from `#showcase` / `library/prompts/`. Always
   credit the handle and link the prompt recipe. (This is the flywheel fuel.)
3. **New in core** — the one real change shipped this week (judge improvement, new backend, faster
   stitch). Link the PR/commit. Plain-English, one sentence on *why it matters to users*.
4. **New LoRAs / reference-packs** — anything merged into `library/` this week, with a 3-frame teaser.
5. **Blind test teaser** — one frame from this week's "Open vs Closed" entry; "guess which is open —
   answer + full video on YouTube."
6. **Call for contributions** — the single most-wanted issue this week (e.g., "want a Wan 2.2
   backend? here's the template, we'll merge it"). Link `CONTRIBUTING.md`.
7. **CTA** — repo link, Discord link, `open-video.ai/try`. "Star ⭐ if you want open video to win."

**YouTube Short (companion, ≤60s):** the 3 best clips of the week cut to a beat, end-card =
"open-video.ai." Same publish moment as the thread; thread links the Short, Short links the thread.

**Sourcing:** every Monday the growth lead reviews `#showcase`, new `library/` PRs, merged core PRs,
and the benchmark queue. The Weekly is *curated*, not *created* — if there's nothing genuinely good,
we say so honestly in tweet 2 rather than padding it.

**Cadence guardrail:** if the Weekly slips 2 weeks running, that's a signal the product isn't
shipping fast enough to feed it — surface it to the eng lead, don't fake content.

---

### Pillar 2 — "Open vs Closed" blind benchmark series (the viral engine)

**What:** the same prompt run on **OpenVideo + H3** vs a closed leader (**Seedance 2.x / Sora / Veo
/ Kling**), presented **side-by-side with no labels**, viewers guess which is open. Reveal + Arena
data + full repo link in the reply/second half.

**Why it works:** this is the highest-leverage format in the entire calendar. It does four things at
once: (1) it makes the *thesis* (open ≥ closed) visibly true or honestly not; (2) the "guess"
mechanic is a built-in engagement trap; (3) it positions OpenVideo as the standard open reference
against named competitors; (4) the answer — *the open one is the good one* — is a story the AI
community desperately wants to share.

**Cadence:** **one entry every two weeks**, rotated across difficulty axes:
- *Prompt-adherence* (complex 3-field H3 prompt with dialogue + camera moves)
- *Long-form coherence* (multi-shot 60s+ — the open-video specialty; closed tools often cap at 15s)
- *Motion quality* (fast camera, physics, hands)
- *Style lock* (consistent character across shots — where reference-packs shine)
- *Audio sync* (FL2VA dialogue vs closed TTS-dubbed)

**Production runbook (per entry):**
1. Pick a prompt that is **fair** — same text to both tools, no OpenVideo-favoring tricks. Log it.
2. Generate on OpenVideo + H3 (1× RTX 5090) **and** on the closed tool. Save seeds + settings.
3. **Vision-judge** both with cx GPT-5.6 + Opus 4.8 on the same rubric (adherence / coherence /
   motion / aesthetic). Log the verdict + scores. This receipt is non-negotiable — it's the
   integrity backbone of the whole series.
4. Cut a **blind** version (A/B unlabeled, 50/50 left-right, randomized) and a **reveal** version.
5. Post blind → wait 24h for votes/quotes → post reveal with the judge scores and the Arena Elo
   delta (e.g., "H3 Elo 1238 vs Seedance 1197 — within noise").
6. **Honesty rule:** when OpenVideo loses (and it will, sometimes), we **say so loudly** and file
   the gap as an issue. A loss posted honestly is worth more trust than a fake win. The series's
   credibility *is* the moat; one rigged test kills it.

**Format variations:** X thread (blind frame → reveal), YouTube Short (blind 15s → reveal 15s),
long-form YouTube ("We blind-tested OpenVideo vs Sora on 10 prompts — here's what happened"), and a
durable `/bench` page on the site that accumulates every entry with full receipts.

**Naming each episode** for shareability: *"OpenVideo vs Sora: the cinematic drone shot test."*
*"OpenVideo vs Seedance: can open do a 60-second short?"* Always name the closed competitor — that's
the SEO/curiosity lever, and it's true.

---

### Pillar 3 — Tutorial series (the contributor funnel)

**What:** a structured, evergreen YouTube + written series that turns curious visitors into users
and users into contributors. Evergreen = the gift that keeps giving; these will be the top search
results for "open source video generation" for years.

**Three tracks, published on alternating Wednesdays:**

**Track A — "Use OpenVideo" (for creators / PMs / non-technical):**
1. *From prompt to film in 5 minutes* (the `open-video.ai/try` walkthrough — zero install)
2. *Writing a great H3 prompt* (the 3-field style-first grammar, bracketed tags, camera prose,
   dialogue tags — this is the most-watched video we'll make)
3. *Storyboard preview & the coherence bible* (how the planner thinks — so users can steer it)
4. *Best-of-N vs refine: when to spend more GPU* (honest unit-economics explainer)
5. *2K upscale + audio continuity* (the "make it look finished" video)
6. *Using community reference-packs* (lock a character across a whole film)

**Track B — "Extend OpenVideo" (for developers):**
1. *The plugin architecture in 10 minutes* (core vs `backends/<model>/` vs `engines/<engine>/`)
2. *Writing a model backend* (copy `templates/model_backend.py` → ship a Wan 2.2 backend)
3. *Writing an engine adapter* (diffusers / SGLang / standalone runner)
4. *Writing a judge plugin* (VideoScore / your own vision model / human-in-the-loop)
5. *A custom pipeline step* (your own planner / stitcher / upscaler)
6. *Benchmarking on your GPU* (`bench/` profiles → PR a verified default)

**Track C — "Contribute a LoRA / recipe" (for the community):**
1. *What makes a good H3 LoRA* (style lock vs identity lock; what transfers, what doesn't)
2. *Training a style LoRA that survives the judge loop*
3. *Authoring a prompt recipe → PR to `library/prompts/`*
4. *Building a reference-pack (turnaround + lighting board)*
5. *Authoring a coherence recipe for a genre* (noir, anime, documentary)

**Production standard:** every tutorial ships with (a) a **copy-pasteable** repo path or prompt, (b)
a **real render** that the viewer can reproduce, (c) a **timestamped** chapter list, and (d) a link
to the matching `docs/` page. If a viewer can't reproduce it from the video alone, it's not done.

**The funnel mechanic:** each tutorial ends with the next-easiest contribution that fits the topic —
"liked this? PR your prompt to `library/prompts/`, we'll feature it in next week's OpenVideo Weekly."

---

### Pillar 4 — Demo film releases (each film is a launch)

**What:** every new multi-shot film open-video produces is treated as a **product launch**, not a
demo reel. A film is the single most convincing proof that the agent layer (plan → judge → refine →
stitch) matters — no single model does >15–30s, so a coherent multi-minute film is *impossible
without open-video*. Each one is a marketing nuke.

**Cadence:** **one flagship film per month**, escalating in ambition along the roadmap:
- **Month 1:** 1-min film (the Phase-0 milestone — proves the loop end-to-end)
- **Month 2–3:** 2–3 min film, single genre
- **Month 4+:** the **5-min flagship** — the north-star demo, the open answer to a Seedance short
- **Ongoing:** one film per month thereafter, rotating genre + demonstrating one new capability
  (a new backend, a new judge, a new LoRA family)

**Each film = a launch event with a runbook:**
1. **T-minus 7 days:** teaser frame on X ("in 7 days, an open 2-min noir short. fully open. 1 GPU.").
2. **T-minus 2 days:** "making-of" thread — the coherence bible, the shot list, how the judge caught
   a dropped character in shot 4 and the refine loop fixed it. This is the *mechanism* content that
   proves it's not a fluke.
3. **Launch day:** YouTube premiere + pinned X thread + top of `open-video.ai`. The thread tells the
   story (concept → plan → 9 shots → judge → refine → stitch → film) with the film embedded.
4. **Release the receipts:** the full prompt bible, per-shot judge scores (cx + Opus), GPU/time log,
   and the `library/` PR containing the coherence recipe used. **This is the moat** — closed vendors
   can't match "here's exactly how we did it, copy it."
5. **T-plus 2 days:** "remix it" post — link the prompt bible + LoRAs so the community can make
   their own cut. Feature the best remix in the next OpenVideo Weekly.

**Naming films for shareability:** give each film a real title and a one-line logline, not
"demo_03.mp4". *("The Last Lighthouse" — a 2-min open-source animated short. Every frame, open.")*

**The escalation headline:** every film should let us claim a first — *"first open 1-min film,"*
*"first open 5-min film,"* *"first open film with locked character identity across all shots."*
Firsts are earnable, factual, and shareable.

---

### Pillar 5 — Build-in-public thread (X, the trust layer)

**What:** the founder/core-team X cadence between the big drops. Real benchmarks, honest challenges,
visible progress. This is what separates OpenVideo from a hype-posting closed startup: we show the
wires.

**Cadence:** **2–3 build-in-public threads per week**, from these recurring templates:

- **"What we shipped this week"** (Mon) — 3–5 bullets, each a PR link + one plain-English sentence.
  No fluff. If the week was thin, say "slow week — here's why" (GPU down, refactoring, etc.).
- **"A benchmark + the receipt"** (rotating) — one concrete number with the method: *"H3 + our judge
  loop: 3.2× fewer re-gens than naive best-of-8 on the 50-prompt suite. Here's the script + logs."*
- **"What broke"** (rotating) — an honest failure postmortem: a film that fell apart, a judge that
  hallucinated a pass, a backend that OOM'd. What we learned. *These are trust gold.*
- **"Open question"** (rotating) — surface a real `PLAN.md` open decision to the community and ask
  for input. Turns lurkers into participants.
- **"Receipt of the day"** — a single judge verdict (frame + score + verdict) from that day's runs,
  showing the loop actually working in the wild.

**Voice rules:**
- Numbers always come with a method link (script, log, or `/bench` page). No bare "10x faster."
- Named competitors only with Arena Elo or a fair blind test behind it — never a vague dunk.
- Failures are first-person and specific ("we lost a character's hat in shot 7"), not performative.
- Every thread ends with a contribution hook or a star ask, never just a flex.

**The reason this matters:** build-in-public is what makes the *community* believe they can join and
shape the project. Closed tools post polished wins; we post the messy middle + the wins. That
asymmetry is how a 0-star repo out-trusts a $1B closed darling.

---

### Pillar 6 — Monthly hackathon (the contributor engine)

**What:** a themed, month-long community contest with real categories, real judges, and real
spotlight. This is the structured funnel that converts the Weekly's audience into the
`library/` contributors who compound the moat.

**Cadence:** **first Monday of every month**, winners announced in that month's final OpenVideo
Weekly + a dedicated X drop. Each hackathon has **one theme** and **three categories**.

**Theme rotation (recurring annually so the community can prep):**

| Month | Theme | Why this theme |
|---|---|---|
| Jan | **New Year, New Backend** | ship the most-wanted new model backend (Wan 2.2 / Hunyuan / LTX) |
| Feb | **Love Your LoRA** | best style/identity LoRA for H3 |
| Mar | **One-Minute Masterpiece** | best 60s open film |
| Apr | **Spring Clean the Judge** | best judge-plugin / quality-rubric improvement |
| May | **Single-GPU Speedrun** | best `bench/` profile + speed optimization |
| Jun | **Summer Blockbuster** | best multi-shot film (genre: action) |
| Jul | **Open vs Closed** | community contributes entries to the blind-test series |
| Aug | **Reference-Pack Roundup** | best reference-packs / coherence bibles |
| Sep | **Back-to-School Tutorials** | best tutorial / explainer contributed |
| Oct | **Hacktoberfest** | first-PR friendly — any contribution counts, bonus for docs |
| Nov | **Audio/Dialogue Special** | best FL2VA dialogue / audio-continuity work |
| Dec | **Year-End 5-Minute Film** | the annual flagship-film contest |

**Three categories per hackathon (fixed):**
1. **Best LoRA** — style or identity, judged on transfer + judge-loop survival.
2. **Best Film** — short open-video-generated film, judged on coherence + aesthetic + concept.
3. **Best Backend / Plugin** — code contribution (backend, engine adapter, judge, pipeline step),
   judged on correctness + cleanliness + mergeability.

**Prizing (Apache-2.0-friendly, no cash-gate on winning):**
- **Spotlight:** winners featured in OpenVideo Weekly + a permanent `/hackathons` hall of fame.
- **Merge:** winning code merged into core/`library/` with author credit.
- **Swag:** OpenVideo sticker pack + (sponsor-permitting) a single-GPU cloud credit drop.
- **Status:** a `Hackathon Winner` Discord role + GitHub org invite for repeat winners.

**Runbook per month:**
- **Week 1 (launch):** announce theme + categories + judging criteria + a starter issue per category.
  Pin in Discord, post on X, add a `library/hackathons/<month>/` README.
- **Weeks 2–3:** mid-point showcase thread; office-hours voice session in Discord for help.
- **Week 4:** submissions close (PR to the month's folder); judges (cx GPT-5.6 + Opus 4.8 + 1
  community lead) score on the published rubric; winners announced.

**Judging integrity:** the rubric is published at launch, scores are public per entry, and the
receipt is logged under `artifacts/verify/hackathon-<month>-<date>.md`. No vibes-based wins.

---

### Pillar 7 — The viral hook library (swap into any post)

The formula from §0, broken into reusable hooks. Mix, match, and localize.

**The core hook (use most):**
> "100% open-source. Free. Runs on a single GPU. This film was made with OpenVideo + H3."

**Anti-closed hooks (use vs named competitors, only with a receipt):**
> "OpenVideo just matched Seedance on a 60-second prompt. Open. Free. Local."
> "Same prompt. OpenVideo vs Sora. Guess which is open. ↓"
> "The #1 open video model (H3, Arena Elo 1238) + an open agent layer. That's it. That's the pitch."

**Capability hooks (tie a feature to a wow clip):**
> "The judge caught a dropped prop in shot 6 and the refine loop fixed it. Open."
> "Character locked across 9 shots. No closed API. No cloud. Just a reference-pack + open code."
> "5-minute film. One model can't do that. One agent can."

**Community hooks (feature people, build belonging):**
> "Built by the community in `#lora-lab`. Merged this morning. Try it free."
> "Your prompt, on H3, free at open-video.ai/try. Post yours in `#showcase`."

**Contribution hooks (always pair with a CONTRIBUTING.md link):**
> "Want a Wan 2.2 backend? Copy the template, we'll merge it. 1 PR = a real model tier."
> "Your prompt could be next week's spotlight. PR to `library/prompts/` — 5 minutes."

**Anti-hype / honesty hooks (use sparingly, they earn the most trust):**
> "We lost this one. Here's why — and the issue we filed to fix it."
> "Open isn't always ahead. Today it is. Here's the blind test."

---

## 3. The weekly production rhythm (how the team executes)

A repeatable week, so content never blocks on a single person's inspiration.

| Day | Action | Owner | Output |
|---|---|---|---|
| **Mon** | Triage `#showcase`, new `library/` PRs, merged core PRs; pick Weekly's community picks; post "what we shipped" thread | Growth lead | Weekly draft skeleton, Mon thread |
| **Tue** | Publish one **tutorial** (alternating track) + companion doc PR | Video editor + eng | YT video + `docs/` page |
| **Wed** | Publish one **build-in-public** thread (benchmark or postmortem) | Founder/eng | X thread + `/bench` update |
| **Thu** | Cut/finish the **OpenVideo Weekly** Short + thread; finalize this week's blind-test reveal if any | Video editor + growth lead | Scheduled Friday assets |
| **Fri 09:00 PT** | Publish **OpenVideo Weekly** (thread + Short); reveal this week's blind test | Growth lead | Live thread + Short |
| **Sat/Sun** | Light engagement only; seed one **remix prompt** in Discord for the following week | Community lead | Discord activity |
| **Bi-weekly (Tue)** | Publish one **Open vs Closed** blind-test entry | Growth lead + eng | Blind → reveal pair |
| **Monthly (launch day)** | **Demo film premiere** + making-of thread + receipts PR | Whole team | Film + bible + judge receipts |
| **Monthly (1st Mon)** | **Hackathon** theme launch; last Weekly of month = winners | Community lead | Hackathon README + winners drop |

**Buffer policy:** maintain a **2-week content buffer** for evergreen assets (tutorials, blind tests,
filmmaking receipts) so a slow eng week never forces a thin Weekly. Pillar 5 (build-in-public) is
*not* buffered — it must be current to be credible.

---

## 4. Sample 12-week editorial calendar (Phase 1 launch quarter)

Assumes a public launch at week 1. Adjust dates to the actual ship date.

| Wk | OpenVideo Weekly theme | Open vs Closed | Tutorial (Tue) | Film / drop | Hackathon |
|---|---|---|---|---|---|
| 1 | **Launch week** — "what is OpenVideo" + first 5 community clips | — | A1: prompt → film in 5 min | **Launch drop**: 1-min proof-of-loop film | — |
| 2 | Best launch-week remixes | *OpenVideo vs Seedance: prompt-adherence* | C1: prompt recipe → PR | Build-in-public: the loop, explained | **Hackathon #1 "One-Minute Masterpiece" launches** |
| 3 | New core feature (judge v2) | — | A2: writing a great H3 prompt | — | mid-point showcase |
| 4 | Community LoRA spotlight | *OpenVideo vs Sora: 60s coherence* | B1: plugin architecture | **Film #2**: 2-min genre short | **Winners announced** |
| 5 | Bench-racing: H3 vs Wan on our suite | — | B2: writing a model backend | — | **Hackathon #2 "Love Your LoRA" launches** |
| 6 | Audio/FL2VA spotlight | *OpenVideo vs Veo: dialogue sync* | C2: training a style LoRA | Build-in-public: what broke making film #2 | mid-point |
| 7 | Best-of-N vs refine explainer | — | A3: storyboard + coherence bible | — | **Winners** |
| 8 | Reference-pack spotlight | *OpenVideo vs Kling: style lock* | B3: engine adapter | **Film #3**: 3-min, locked-character | **Hackathon #3 "Spring Clean the Judge"** |
| 9 | New backend merged (Wan 2.2?) | — | B4: judge plugin | — | mid-point |
| 10 | Community film remixes | *OpenVideo vs Seedance: long-form 90s* | C3: reference-pack | Build-in-public: the receipts | **Winners** |
| 11 | Year-of-open-video teaser | — | A4: best-of-N vs refine | — | **Hackathon #4 "Single-GPU Speedrun"** |
| 12 | **5-min flagship film week** | *OpenVideo vs Sora: the 5-min test* | A5: 2K + audio finish | **🏆 Film #4: the 5-min flagship** | mid-point → winners wk13 |

---

## 5. KPIs & success metrics

Content exists to grow the community and prove the thesis. Track these, weekly.

**North star**
- **GitHub ★** — trajectory to 100K. Report weekly delta + 4-wk rolling avg.
- **#1 open video project** by ★ (track the next open competitor: Open-Sora, Mochi, etc.).

**Funnel (channel → repo → contribution)**
- X/YouTube → `open-video.ai/try` gen completions (weekly).
- `open-video.ai` → GitHub star conversion rate (stars / unique visitors).
- GitHub stars → first-PR conversion rate (contributors / stars).

**Engagement quality (not vanity)**
- Discord DAU + weekly active contributors.
- `library/` PRs/week (prompts, LoRAs, reference-packs, recipes) — **the moat metric.**
- Hackathon entries/month + repeat-contributor rate.
- Blind-test series: votes + "I guessed open" rate (the thesis signal).

**Integrity (non-negotiable, do not skip)**
- % of "beats closed" / "coherent film" / "single GPU" claims with a logged receipt (target: 100%).
- % of films vision-judged (cx GPT-5.6 + Opus 4.8) before publish (target: 100%).
- Honesty incidents: any rigged blind test or unlabeled mock = P0, public correction required.

**Cadence health**
- OpenVideo Weekly: published on time ≥ 90% of weeks.
- Tutorial cadence: 1/week met ≥ 80%.
- Film cadence: 1/month met (if missed, that's a roadmap signal, not a content problem).

---

## 6. Asset templates (appendix)

### 6.1 OpenVideo Weekly — thread template
```
1/ Best of the week 👇 [clip] 100% open-source, free, 1 GPU. Made with OpenVideo + H3.
   h/t @<creator> — prompt: open-video.ai/gallery/<slug>

2/ 🌟 Community spotlight: @<u1> locked a noir look, @<u2> did a 60s chase, @<u3> shipped a Ghibli LoRA.

3/ 🛠️ New in core: <one-line>. Why it matters: <one-line>. PR #<n>: <link>

4/ 🎨 New in library: <LoRA/pack name> — <what it does>. 3-frame teaser 👇

5/ 🆚 Blind test: which is OpenVideo, which is Sora? Guess ↓ — reveal + scores tomorrow.

6/ 🤝 Most-wanted this week: <issue/contribution>. Template: CONTRIBUTING.md — we'll merge it.

7/ ⭐ Star open-video: <github> · Discord: <discord> · Try free: open-video.ai/try
   #OpenVideo #OpenSource #VideoGeneration
```

### 6.2 Open vs Closed — blind-test post template
```
Same prompt. Two tools. One is 100% open-source + free + runs on 1 GPU. Which? 🤔

[A: clip]   [B: clip]

Vote 👇 — reveal + the Arena numbers (H3 Elo 1238 vs <closed> <elo>) in 24h.

Receipt: open-video.ai/bench/<slug> (full prompt, seeds, judge scores)
Star the open one: <github>
```

### 6.3 Demo film — launch thread template
```
1/ Today: "<Film Title>" — a <N>-min open-source film. Every frame, open. 1 GPU. Free. 🎬
   ▶ <youtube premiere>   ·   receipts: open-video.ai/films/<slug>

2/ The concept: <logline>. The challenge: no single model does >15–30s. This needs an agent.

3/ The plan: <X> shots, one coherence bible (chars/style/lighting/props), each ≤15s.

4/ The loop: planner → crafter → H3 → judge → refine → stitch. The judge caught <real thing>;
   refine fixed it. Here's the per-shot scorecard: <link>

5/ The receipts (open means you can copy this): prompt bible, LoRAs, ref-packs, GPU/time log →
   PR: <library link>

6/ Remix it: fork the bible, swap the genre, post your cut in #showcase. Best one → next Weekly.

7/ ⭐ Open video can win. Star <github> if you want it to. · open-video.ai/try
```

### 6.4 Build-in-public — postmortem template
```
What broke this week: <one-line>. We're posting it because open means honest. 🧵

1/ We tried <thing>. We expected <X>. We got <Y>.

2/ Root cause: <specific — e.g., "judge gave shot 7 an 8.2 but the character's hat vanished">

3/ The fix (filed as issue #<n>): <link>. Status: <open/in-progress/merged>.

4/ Lesson: <one durable sentence — this becomes a CONTRIBUTING note or a PLAN.md decision>.

5/ Onward. Star <github> if building in the open is your thing.
```

---

## 7. Operating rules (the integrity backbone)

1. **Every "beats closed" / "coherent film" / "single GPU" claim has a receipt.** No receipt →
   reword to something honest or don't post. (Source: project anti-hallucination + done-claim gate.)
2. **Every film is vision-judged (cx GPT-5.6 + Opus 4.8) before it ships as "coherent."** Log the
   verdict under `artifacts/verify/film-<slug>-<date>.md`. (Source: cross-model-review rule.)
3. **Named-competitor claims cite Arena Elo or a fair blind test.** No vague dunks.
4. **One rigged blind test = P0.** Post a public correction within 24h. Credibility is the moat.
5. **Credit every community asset by handle and link the PR.** The flywheel dies without credit.
6. **Canonical home of every asset is `open-video.ai` or the GitHub release.** Social posts link back;
   no asset exists only inside a platform we don't control.
7. **When OpenVideo loses, say so loudly and file the issue.** Honest losses earn more stars than
   fake wins. This is the single biggest brand differentiator vs closed vendors.
8. **Content doesn't block on inspiration.** The weekly rhythm (§3) + the 2-week evergreen buffer
   keep cadence mechanical. If cadence slips, it's a roadmap signal — surface it, don't fake it.

---

*Owner: Growth lead. Reviewers: Founder (positioning integrity), Eng lead (technical receipts),
Community lead (credit + contributor funnel). Last updated: 2026-08-06.*
