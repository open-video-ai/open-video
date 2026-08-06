# OpenVideo — Launch Sequence Plan

> The single source of truth for launch day. Every block of copy is paste-ready. Handles,
> invite codes, and the one-line description of the actual demo film content are the only
> placeholders (marked `[FILL]`) — everything else is locked.
>
> **Brand:** "OpenVideo" (public-facing) · "open-video" (code/repo).
> **Domain:** open-video.ai · **License:** Apache 2.0 · **Engine:** ComfyUI · **Model:** MiniMax H3.
> **Canonical handles (already wired into the website):**
> GitHub `github.com/open-video/open-video` · Discord `discord.gg/open-video` · X `@openvideo_ai`.
>
> **Iron rule: every social post is sent ONLY after infra is confirmed live.**
> A dead CTA on a hot tweet is the #1 launch failure mode. Pre-flight gate (§4) goes green first.

---

## 0. The one thing that must be true

**The demo film must be GOOD.** It is the hook for the X thread, the hero of the website, the
proof in the Reddit posts, the gallery on Product Hunt, and the substance of the Show HN.
Everything in this plan is an amplifier; the film is the signal. If the film is mediocre, **do not
launch** — delay a week and fix it. There is no second first-impression.

- **Pass bar (non-negotiable):** the flagship film passes the project's own cross-model visual
  review — both **cx (GPT-5.6) and Opus 4.8** open the actual frames and judge it coherent and at
  least on-par with a Seedance short on the same concept. Record both verdicts in
  `artifacts/verify/demo-film-<date>.md`. No receipt → not good → no launch.
- **Format:** a vertical **9:16 clip (≤60s, ≤5 MB) for X autoplay**, and the full film (16:9,
  60–300s) for the website + PH + Reddit. Cut a 3-second "thumb-stopper" opening (X users decide in
  the first loop).
- **Name it once:** `demo.mp4` (full) in repo root AND `website/`; `demo-clip-9x16.mp4` for social.

---

## 1. Launch day at a glance

- **Ideal day:** a **Tuesday** or **Wednesday** (HN/PH/reddit all underperform Fri–Mon). Avoid US
  holidays and major Apple/NVIDIA keynotes.
- **All times Pacific (PT), same calendar day.** Stagger posts so each gets its own comment window
  and you can be present to reply. Order is **megaphone first, communities second, HN last**.
- **Day-minus-1 hard gate:** demo film passed review, repo public-readiness signed off, site
  deployed green, Discord live, all copy in this doc reviewed by a second pair of eyes.

| Time (PT) | Action | Owner |
|---|---|---|
| 00:01 | **Product Hunt** launch published (full 24h voting window). Maker monitors from wake. | PH launcher |
| 05:30 | Final pre-flight: make repo **public**, push final commit, confirm `open-video.ai` live, confirm Discord invite resolves, confirm `demo.mp4` hot. | Infra |
| 06:00 | **GO / NO-GO gate** (§4 checklist all green). | Launch lead |
| 06:15 | **X thread** live (catches US morning + EU afternoon). Pin it. | Social |
| 07:30 | **Reddit r/comfyui** (friendly, technical warmup). | Social |
| 08:00 | **Reddit r/LocalLLaMA** (open-weights crowd). | Social |
| 08:30 | **Reddit r/StableDiffusion** (biggest audience, prime time). | Social |
| 09:00 | **Reddit r/aivideo** (creator audience). | Social |
| 09:30 | **HackerNews Show HN** (US morning peak). | Social |
| All day | **Engage**: reply to every comment in <60 min for the first 4h; be live in Discord. | Everyone |

> Why PH at 00:01 and not at 06:00? PH's day resets at midnight PT; launching at 00:01 buys the full
> 24-hour voting cycle, and every subsequent post (X/reddit/HN) drives traffic *upward* into an
> already-live PH listing. Tradeoff: you won't be awake for the first comments — accept it, or move
> PH to 06:00 and lose ~6h of voting (ok if you'd rather be present for the kickoff).

---

## 2. Pre-launch checklist (T-7d → T-1d)

### T-7d — Demo film (the gate)
- [ ] Flagship film rendered end-to-end from a one-line concept (1-min minimum, 5-min stretch).
- [ ] Vertical 9:16 ≤60s clip cut for X; 3s thumb-stopper opening identified.
- [ ] **Cross-model visual review passed: cx (GPT-5.6) AND Opus 4.8**, receipt in
      `artifacts/verify/demo-film-<date>.md`.
- [ ] `demo.mp4` committed to **repo root** and **`website/`**; `demo-clip-9x16.mp4` for social.

### T-3d — Surfaces
- [ ] **GitHub org secured:** `github.com/open-video` org exists; repo transferred from private
      `robotlearning123/open-video` → `open-video/open-video` so the website's links resolve. (If
      `open-video` org is taken, either negotiate it or update ALL links site-wide — do not ship
      mismatched links.)
- [ ] README "first scroll" polished: 1-line tagline, the 9:16 demo GIF/MP4 inline at the top,
      badges (License Apache-2.0, H3 model, ComfyUI), "Three ways to use it" table, quickstart, link
      to `open-video.ai/try`. **The README is the product page for devs — it must be the best doc in
      the repo.**
- [ ] **Social cards — currently MISSING (`og:image`/`twitter:card` = 0 in index.html).** Add before
      launch or link previews will be text-only on X/Reddit/FB:
      - `og:image` → `https://open-video.ai/og-image.png` (1200×630, the demo frame + logo + tagline).
      - `twitter:card` = `summary_large_image` (or `player` with the demo video for autoplay preview).
      - Same tags on `try.html`.
- [ ] X `@openvideo_ai`, Discord `discord.gg/open-video` secured and **aged** (5–10 warm-up posts on
      X in the week before so the account isn't a zero-history shell on launch day).
- [ ] Cloudflare Pages project configured; production branch deploys `website/` to `open-video.ai`;
      DNS verified; HTTPS active.

### T-2d — Community
- [ ] Discord server built (§9): channels, rules, `#announcements` first message drafted, roles,
      a `#start-here` with the 3 links. Invite `discord.gg/open-video` resolves.
- [ ] Product Hunt listing drafted in the PH dashboard (gallery images = demo frames + logo + UI
      shot; demo video = the full film on YouTube/loom; all copy in §8).

### T-1d — Dry run (no public changes)
- [ ] Every URL in this doc opened in an incognito window; no 404s.
- [ ] CF deploy dry-run from a throwaway commit (then reverted) — pipeline is green.
- [ ] Copy in §3–§9 reviewed by a second person for tone, typos, and broken claims.
- [ ] Bank of 4–6 "demonstration replies" pre-written for common questions (VRAM? license? vs
      Seedance? how long to render? can I use it commercially?).

---

## 3. Step 1 — GitHub repo public

**Sequence (do this at 05:30 PT, before any post):**

1. **Transfer/visibility:** `open-video/open-video` → Settings → Danger Zone → **Make public** (or
   complete the transfer from `robotlearning123/open-video` if not already done at T-3d).
2. **Final commit** pushed: polished README, `demo.mp4` in root, `LICENSE` (Apache 2.0, present),
   `CONTRIBUTING.md`, `GOVERNANCE.md`, `docs/`, topics set
   (`video-generation`, `comfyui`, `minimax-h3`, `text-to-video`, `agent`, `open-source`).
3. **About panel:** tagline + website `https://open-video.ai` + topics + release tag `v0.1.0`.
4. **Pin** an issue: *"Launch thread — ask anything"* that links to X/reddit/PH/Discord.
5. **Verify incognito:** repo loads, README renders, `demo.mp4` plays inline, star button works.

**README hero block (top of file, paste over current intro if needed):**

```markdown
# OpenVideo

**Open-source autonomous video generation — from concept to film, for everyone.**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Model: MiniMax H3](https://img.shields.io/badge/Model-MiniMax%20H3-fbbf24)](https://huggingface.co/MiniMaxAI/MiniMax-H3)
[![Engine: ComfyUI](https://img.shields.io/badge/Engine-ComfyUI-22b14c)](https://github.com/comfyanonymous/ComfyUI)

![OpenVideo demo film](demo.mp4)

> **OpenVideo: Runway-quality video, 100% open-source, free.** No API costs, no watermarks, no
> region locks. Run it locally or use our free hosted version at **open-video.ai/try**.

You describe it. OpenVideo plans, generates, judges, refines, and delivers — a complete agentic
director, open and free. Built on **ComfyUI** (engine) + **MiniMax H3** (#1 open video model) + a
**judge→refine loop** (the core IP). Apache 2.0.

**→ Try it free (no install):** [open-video.ai/try](https://open-video.ai/try)
**→ Star & contribute:** [github.com/open-video/open-video](https://github.com/open-video/open-video)
**→ Community:** [discord.gg/open-video](https://discord.gg/open-video)
```

> After the hero, keep the existing README sections (Three ways to use it / What it is-isn't / Thesis
> / Flagship demo / Why it can win / Repo layout). The hero is the only block that must change.

---

## 4. Pre-flight GO / NO-GO gate (06:00 PT)

All must be green. **Any red = hold every post until fixed.**

- [ ] `github.com/open-video/open-video` loads in incognito, demo plays, star works.
- [ ] `https://open-video.ai` and `/try` load over HTTPS; `demo.mp4` streams.
- [ ] `og:image`/`twitter:card` present (test with `opengraph.xyz` or Twitter Card Validator).
- [ ] `discord.gg/open-video` invite resolves to the server.
- [ ] Product Hunt listing is published (00:01) and visible at `producthunt.com`.
- [ ] X `@openvideo_ai` logged in, media ready (`demo-clip-9x16.mp4`).
- [ ] Reddit accounts ≥7 days old, ≥50 karma each (to post in the big subs without automod kills).
- [ ] HN account ≥2 karma, not flag-new.

**Launch lead signs the gate** (a single thumbs-up in the war-room channel) → §5 begins.

---

## 5. Step 2 — Website deploy (Cloudflare Pages)

If the dry-run (T-1d) is green, launch morning is "confirm only":

1. Confirm the production deploy is the latest commit (`website/index.html`, `try.html`,
   `demo.mp4`, `logo.svg`, `og-image.png`).
2. Confirm custom domain `open-video.ai` bound and active (Pages → Custom domains → Active).
3. Confirm `https://www.open-video.ai` redirects to `https://open-video.ai` (or vice-versa).
4. Load-test sanity: hit `/try` and `/demo.mp4` simultaneously from a second machine; CF handles
   the spike, but confirm the origin/asset isn't misconfigured.
5. Leave the CF Pages tab open with access logs visible through the morning.

**Asset manifest (all must be present in `website/`):** `index.html`, `try.html`, `demo.mp4`,
`logo.svg`, `og-image.png`, `favicon.ico` (or rely on `logo.svg` icon link — already set).

---

## 6. Step 3 — X launch thread (06:15 PT)

Post from `@openvideo_ai`. **Attach `demo-clip-9x16.mp4` to Tweet 1** so it autoplays in the
timeline next to the hook. Pin the thread. Quote-tweet it from any personal accounts.

**Tweet 1 — Hook (media: `demo-clip-9x16.mp4`):**
```
OpenVideo: Runway-quality video, 100% open-source, free.

No API costs. No watermarks. No region locks. Run it locally, or use the free hosted version.

The closed era of video generation just ended. ↓
```

**Tweet 2 — The demo film (media: full `demo.mp4` or a 60s horizontal cut):**
```
Made end-to-end from a one-line prompt. [FILL: one line describing the actual film — e.g.
"A 90-second noir short, generated, judged, and stitched by the agent."]

Plan → generate → judge → refine → stitch. No human in the edit.
```

**Tweet 3 — The thesis:**
```
The open models already caught up.

MiniMax H3 = #1 open video model on the Arena (T2V #2 / I2V #3 overall) — within benchmark noise
of the closed leaders (Sora, Veo, Seedance).

The gap was never quality. It was the AGENT LAYER.
```

**Tweet 4 — What OpenVideo is:**
```
OpenVideo is that agent layer, open:

→ Plans a film from a concept (coherence bible: acts → shots)
→ Crafts + validates each shot's prompt
→ Generates via H3
→ JUDGES each shot with a vision model
→ Refines anything below the bar
→ Stitches shots into a multi-minute film, with audio

A real autonomous director. Apache 2.0.
```

**Tweet 5 — Three ways to use it:**
```
Use it three ways:

🖥️ App — type a concept → get a video. For everyone, no code.
⌨️ CLI/API — `open-video "concept" --duration 300`
🤖 Skill — drop it into Claude Code / Cursor

From non-technical creators to senior devs.
```

**Tweet 6 — Why it wins:**
```
Why OpenVideo wins:

• Open + local + free vs closed API cost & lock-in
• Built ON ComfyUI (124k★) — we drive the engine, we don't fight it
• Model-agnostic: H3 today, Wan 2.2 / next open model tomorrow — the director survives churn
• Community recipes (prompts, ref-packs, coherence bibles) = a moat closed vendors can't match
```

**Tweet 7 — CTA:**
```
100% open-source. Apache 2.0. No paywall.

⭐ GitHub: github.com/open-video/open-video
▶️ Free try: open-video.ai/try
💬 Discord: discord.gg/open-video

North star: 100K★ and the #1 open video community.

Help us get there. 🤝
```

**Reply strategy:** for the first 4 hours, answer every reply in <60 min. Pre-canned answers ready
for: VRAM reqs (NF4 ~8 GB, INT8 ~21 GB default), license (Apache 2.0, fully commercial-ok), "vs
Seedance?" (open + local + model-agnostic), "how long to render a minute?" `[FILL with measured
number]`.

---

## 7. Step 4 — Reddit (07:30 → 09:00 PT)

**Rules for all four:** post as link+comment (not pure text) so the demo is the hero; lead with
what YOU built (Reddit rewards builders, punishes marketers); be in the comments for 3h; never
cross-post the identical body — tailor the opening line to each sub's culture; **read each sub's
rules on self-promotion first** (r/LocalLLaMA and r/StableDiffusion have explicit ratio rules).

### 7a. r/comfyui (07:30 PT) — partner pitch, technical

**Title:**
```
OpenVideo — an autonomous "director" layer that drives ComfyUI via API: multi-shot H3 films with a judge→refine loop. Open-source, Apache 2.0.
```

**Body:**
```
Hi r/comfyui — OpenVideo is not a replacement for ComfyUI, it's a brain on top of it. We drive your
existing ComfyUI install over its API: the agent plans a film, writes + validates per-shot prompts,
calls the H3 workflow, judges each rendered shot with a vision model, refines below-bar shots, and
stitches them past the 15s ceiling into a multi-minute film with audio.

Why I'm posting here: ComfyUI already won the engine layer (124k★). What it doesn't ship is the
agent loop — the planner/judge/refine/stitch that turns single-shot renders into delivered films.
OpenVideo is that loop, open, and it talks to *your* workflows.

**Demo film (made this way):** [FILL one-liner] → https://open-video.ai  (demo.mp4 on the landing page)
**Repo (Apache 2.0):** https://github.com/open-video/open-video
**Engine adapter:** `engines/comfyui/` — the adapter is where Comfy-fluent folks will feel at home.

What I'd love from this community:
- Workflow authors: help us harden the H3 ComfyUI workflow (the backends/h3 + engines/comfyui seam).
- Backend contributors: a Wan 2.2 / LTX plugin is the next milestone — the model-agnostic contract
  is documented in CONTRIBUTING.md.
- Brutal feedback on the judge loop — it's the core IP and I want it picked apart.

Happy to go deep in the comments on the API call pattern, the FL2VA first-frame handoff between
shots, and how the validator hard-gates duration/ref-counts/dialogue.
```

### 7b. r/LocalLLaMA (08:00 PT) — local + open-weights

**Title:**
```
OpenVideo — autonomous video generation, 100% local + open-source (MiniMax H3, runs on a single RTX 5090). The open answer to Seedance.
```

**Body:**
```
The thesis: open video models already caught up to closed. MiniMax H3 is the #1 open model on the
Artificial Analysis Arena (T2V #2 / I2V #3 overall, ~Elo 1238/1189 — within noise of Gemini Omni
Flash and Seedance). The thing that was missing was the AGENT layer — the planner/judge/refine/
stitch that turns single-shot model output into a delivered multi-minute film. OpenVideo is that
layer, and it runs on your own GPU.

Local story:
- Model: MiniMax H3, native stereo audio, 4–15s per shot.
- VRAM tiers (verified on RTX 5090): NF4 from ~8 GB, W4 ConvRot ~10 GB, INT8 ConvRot ~21 GB (the
  default we ship), BF16 ~62 GB.
- No API calls, no region locks, no telemetry, no watermark. Apache 2.0 — commercial use is fine.

What it does, end to end: you give it a concept → it writes a coherence bible (logline → acts →
shots ≤15s) → crafts + validates each shot's H3 prompt → generates via your local ComfyUI → judges
each shot with a vision model → refines the ones below bar → stitches into one film with cross-shot
audio continuity.

**Demo film:** https://open-video.ai  (full film on landing)
**Try it free (hosted) if you don't have the GPU yet:** https://open-video.ai/try
**Repo:** https://github.com/open-video/open-video
**Discord:** https://discord.gg/open-video

I know this sub's rule on self-promo — I'm here as a builder, happy to answer any technical
question about the H3 quant path, the FL2VA handoff, or how the judge loop is unit-economiced for a
future hosted tier. AMA in the comments.
```

### 7c. r/StableDiffusion (08:30 PT) — biggest audience, creator+dev

**Title:**
```
I built OpenVideo — an open-source autonomous video director on MiniMax H3 + ComfyUI (Runway-quality, 100% free, Apache 2.0). Full demo film inside.
```

**Body:**
```
Hey r/StableDiffusion — long-time lurker, first post here. I've been watching open video models
close the gap with closed products for a year, and they finally did: MiniMax H3 is the #1 open video
model on Arena, within benchmark noise of Sora/Veo/Seedance. The missing piece was never the model —
it was a director layer that can plan a film, judge each shot, refine the bad ones, and stitch past
the 15s ceiling. So I built it, open.

OpenVideo = ComfyUI (engine) + MiniMax H3 (model) + a judge→refine loop (the core IP). You describe
the film; it plans → generates → judges → refines → stitches → delivers, with audio.

**The demo (a [FILL: e.g. 90-second] short, generated end-to-end from a one-line prompt):**
https://open-video.ai   ← the film autoplays on the landing page

Three ways to use it:
- 🖥️ Web app: type a concept → get a video (free, no install): https://open-video.ai/try
- ⌨️ CLI/API: `open-video "concept" --duration 300`
- 🧩 Local: clone, point at your ComfyUI, run.

Everything is Apache 2.0, no watermarks, commercial use fine, local-first.

Repo: https://github.com/open-video/open-video
Discord (prompts, ref-packs, coherence recipes): https://discord.gg/open-video

This sub has taught me a lot. If this is useful, the things I need most are: prompt-library
contributions (community recipes are the moat), a Wan 2.2 backend plugin, and brutal feedback on the
judge loop. AMA.
```

### 7d. r/aivideo (09:00 PT) — creator audience, less technical

**Title:**
```
OpenVideo — a free, open-source alternative to Runway/Seedance. Type a concept, get a finished video. Just launched.
```

**Body:**
```
Posting for the creators here who are tired of credits, watermarks, and region locks.

OpenVideo is a fully open-source video-generation director: you describe what you want, and it plans,
generates, judges, refines, and stitches a finished video for you — free, and you can run the whole
thing on your own machine (no subscription, no per-video cost).

It's built on the best open video model right now (MiniMax H3, #1 open on the Arena, basically tied
with the closed leaders) plus an agent loop that does the work a human editor would: writing the
shot list, judging each take, fixing the bad ones, and joining everything into one film with sound.

**Watch the demo film:** https://open-video.ai  (plays right on the page)
**Try it free, no signup walls:** https://open-video.ai/try
**It's open-source (Apache 2.0):** https://github.com/open-video/open-video
**Community (prompts, help, show & tell):** https://discord.gg/open-video

What makes it different from Runway/Seedance/Sora:
- Free and open — no credits, no watermarks, no region blocks.
- Run it locally on your own GPU (NF4 quant runs on as little as ~8 GB VRAM).
- Community recipes: the prompt/ref-pack library is shared and growing — closed vendors keep their
  know-how internal; we publish ours.

I'll be in the comments. If you make something with it, drop it in r/aivideo and tag me — I want to
feature the best ones.
```

---

## 8. Step 5 — HackerNews "Show HN" (09:30 PT)

**Title (pick one — HN likes understated):**
```
Show HN: OpenVideo – Open-source autonomous video generation
```
(Alt: `Show HN: OpenVideo – an open agent layer for video generation (MiniMax H3 + ComfyUI)`)

**URL field:** `https://open-video.ai` (your site, not GitHub — HN prefers the product URL; GitHub
link goes in the first comment).

**First comment (the "build" comment — post immediately after submitting):**
```
Hi HN, builder here.

OpenVideo is an open-source agent layer for video generation. You give it a concept; it plans a
film, writes and validates per-shot prompts, generates each shot via MiniMax H3, judges each rendered
shot with a vision model, refines the ones below bar, and stitches the shots (with audio) into a
multi-minute film.

The thesis is simple: open video models have caught up to closed ones. MiniMax H3 is the #1 open
model on the Artificial Analysis Arena — T2V #2 / I2V #3 overall, within benchmark noise of Gemini
Omni Flash and Seedance. The gap that remained wasn't quality; it was the agent layer (plan / judge /
refine / stitch) that closed products ship and open models don't. OpenVideo is that layer, open.

Architecture, for the curious:
- `core/` — model-agnostic: planner, crafter, validator, judge loop, stitcher, reference-pack
  builder.
- `backends/<model>/` — plugin per model. H3 is the first; Wan 2.2 / LTX are planned. Adding a
  model is one folder; the core doesn't change.
- `engines/<engine>/` — adapter per engine. ComfyUI is the first; we drive it over its API rather
  than replacing it.

It's Apache 2.0, runs locally (NF4 quant from ~8 GB VRAM; INT8 default ~21 GB on a 5090), and there's
a free hosted try page for anyone who doesn't have the GPU yet.

Honest caveats: the long-film pipeline is early (call it v0.1); single shots are capped at ~15s by
H3 so everything longer is stitched; wide shots can still corrupt faces (known H3 issue); the judge
loop's unit economics for a future hosted tier hinge on refine-few rather than best-of-many.

- Demo film: https://open-video.ai
- Free try: https://open-video.ai/try
- Source: https://github.com/open-video/open-video

Happy to go as deep as you want on the judge loop, the FL2VA first-frame handoff between shots, the
model-agnostic contract, or the quant path. AMA.
```

**HN engagement rules:** answer technical questions with technical depth, never marketing-speak;
acknowledge limitations up front (HN rewards honesty); do **not** ask for upvotes anywhere (against
HN rules, will get the post killed). Be present for 4–6 hours.

---

## 9. Step 6 — Product Hunt (00:01 PT)

In the PH dashboard, pre-build everything; at 00:01 PT switch to **Published**.

- **Name:** `OpenVideo`
- **Tagline (≤60 chars):** `Open-source Runway-quality video generation` (43 chars) —
  alt: `The open, free alternative to Runway and Seedance` (49 chars).
- **URL:** `https://open-video.ai`
- **Demo video URL:** the full film on a YouTube/loom unlisted upload (PH wants a video).
- **Gallery (6 images, 1270×760):**
  1. Hero card — demo frame + logo + tagline.
  2. The 3-ways-to-use-it table (App / CLI / Skill).
  3. The pipeline diagram (plan → generate → judge → refine → stitch).
  4. A `try.html` UI screenshot.
  5. A "model-agnostic" card (H3 today, Wan/LTX next).
  6. License + community card (Apache 2.0 + Discord/GitHub).
- **Topics:** `Artificial Intelligence`, `Open Source`, `Video Streaming`, `Design Tools`.
- **Description (PH body):**
```
OpenVideo is the open-source, fully free alternative to Runway and Seedance. Describe a video; an
autonomous agent plans, generates, judges, refines, and stitches a finished film for you — no
credits, no watermarks, no region locks.

It's built on the best open video model today (MiniMax H3 — #1 open on the Arena, within benchmark
noise of Sora/Veo/Seedance) plus the agent layer closed products ship and open models don't: a
planner, a per-shot validator, a vision judge, a refine loop, and a multi-shot stitcher that breaks
past the model's 15-second ceiling into multi-minute films with sound.

Three ways to use it:
• Web app — type a concept, get a video (free, no install).
• CLI / API — `open-video "concept" --duration 300`.
• Skill — drop it into Claude Code or Cursor.

100% Apache 2.0. Run it locally on your own GPU (from ~8 GB VRAM), or use the free hosted version.
Community recipes (prompts, reference-packs, coherence bibles) make the library better for everyone.

North star: 100K★ and the #1 open video community.
```
- **Maker comment (post the moment it goes live):**
```
Hey Product Hunt 👋 — I'm the builder of OpenVideo.

I started this because open video models finally caught up to closed ones in raw quality, but the
thing that makes Sora/Seedance feel like a *product* — the agent that plans, judges, and stitches —
was still closed. OpenVideo is that agent, open and free.

It's early (v0.1), it's Apache 2.0, and the community library of prompts and recipes is the part I'm
most excited to grow with you. If you make something with it today, come share it in our Discord —
I'll feature the best ones.

Thanks for the support. AMA in the comments. 🙏
  • Try it free: https://open-video.ai/try
  • Source: https://github.com/open-video/open-video
  • Discord: https://discord.gg/open-video
```

---

## 10. Step 7 — Discord server (open before 06:00 PT)

**Invite:** `discord.gg/open-video` (vanity — must be set in Server Settings → Custom Invite Link).
Put this link in **every** post above (it already is).

**Channel structure:**
```
📄 INFO
  #start-here        → the 3 links (site / repo / try), one pinned message
  #announcements     → launch-day pinned: "We just launched. X thread: <link>. PH: <link>."
  #rules             → short, friendly, Apache-2.0 ethos
💬 COMMUNITY
  #general           → watercooler
  #showcase          → drop what you made (the flywheel seed)
  #help              → install / running issues
  #prompts           → prompt library contributions
🛠 BUILD
  #dev               → contributor chat
  #backends          → H3 now, Wan 2.2 / LTX next
  #judge-loop        → core-IP discussion
🔊 VOICE
  # launch-day lounge → hang out on launch day
```

**`#start-here` pinned message:**
```
👋 Welcome to OpenVideo — the open-source autonomous video director.

🎬 Watch the demo: https://open-video.ai
▶️ Try it free: https://open-video.ai/try
⭐ Source (Apache 2.0): https://github.com/open-video/open-video
📖 Getting started: https://github.com/open-video/open-video/blob/main/docs/getting-started.md

Pick a role in #roles, drop a prompt in #prompts, show what you made in #showcase.
We're building the #1 open video community. Glad you're here.
```

**Roles:** `@Builder` (contributor), `@Creator` (uses the app), `@Model` (backend/model author),
`@Core` (core team). Self-assign in `#roles`.

**Day-0 moderation:** at least one moderator awake and in `#general` from 06:00–22:00 PT, replying
fast; spam filter on; `#showcase` seeded with 2–3 example generations so it's never empty when the
first visitor arrives.

---

## 11. The critical dependency — demo film (deep-dive)

Repeating §0 because everything hinges on it. The launch is **demo-first**: every channel leads
with the film. If the film is weak, the thread flops, reddit downvotes, HN flags "marketing", and PH
stalls. If the film is great, all five channels compound.

**Definition of "good" (must pass ALL):**
1. **Coherence** — a viewer who doesn't know it's AI cannot immediately tell it's stitched; shots
   share characters, style, lighting, and continuity anchors.
2. **Adherence** — the film visibly matches the one-line prompt that generated it (the validator +
   judge loop's whole point).
3. **Parity** — blind-side-by-side vs a Seedance short on the same concept, viewers don't
   systematically prefer the closed one. Verified by **cx (GPT-5.6) + Opus 4.8** visual review, both
   verdicts recorded.
4. **Thumb-stop** — the first 3 seconds (the X autoplay loop) make a scroller stop. Cut the single
   best 3s as the 9:16 opening.

**If it does NOT pass:** delay. Use the extra days to run the refine loop harder, add a reference
pack for identity lock, or pick a stronger concept. A one-week delay costs nothing; a weak launch
costs the project's one chance at first-impression.

**If the 5-minute stretch is shaky:** ship the **1-minute film** as the hero (per PLAN.md Phase-0
decision — 1-min is the milestone). It's better to launch a flawless 60s than a wobbly 5min.

---

## 12. Post-launch (same day, through EOD)

- **First 4 hours:** reply to everything, everywhere, in <60 min. Visibility in this window
  determines whether each post hits critical velocity.
- **Monitor:** X impressions/likes, reddit upvote velocity (don't refresh obsessively — check every
  30 min), HN rank (if it climbs past ~page 2, drop everything and answer comments), PH position.
- **Cross-amplify:** if the HN post takes off, tweet "We're #N on HN 🔥 <link>". If PH trends, same.
  Update the pinned GitHub issue with live links + star count milestones.
- **Star ask:** in every reply on Discord/reddit, a soft "⭐ if you'd build with us" — never beg.
- **Capture:** screenshot every leaderboard position (HN front page, PH top-5, reddit hot) for the
  closeout receipt and the next funding/partnership conversation.
- **End of day:** write `artifacts/verify/launch-<date>.md` — stars gained, traffic, signups, what
  landed, what didn't, top 3 pieces of feedback to act on this week.

---

## 13. Risk register & contingencies

| Risk | Mitigation |
|---|---|
| `open-video` GitHub org not available | T-7d: secure the org (or pick `openvideo-ai` and rewrite all links site-wide — must be consistent). |
| Demo film fails visual review | **Delay launch.** Fix the loop. 1-min flawless > 5-min wobbly. |
| Reddit automod removes posts (low-karma/young accounts) | Accounts aged ≥7d / ≥50 karma; post as **Link** with demo URL; message mods of each sub 2 days prior ("I'm launching an open-source project, here's the demo, may I post Tuesday?"). |
| HN post flagged | Keep title understated, lead with the build comment, answer technically, never ask for upvotes off-site. |
| CF Pages spike / `demo.mp4` hot | Cloudflare CDN handles it; pre-warm cache; have a YouTube mirror of the demo as a fallback link in the build comment. |
| Traffic to `/try` overwhelms the single RTX 5090 | Queue with a friendly wait message + email capture; cap concurrent jobs; show estimated wait time. |
| og:image missing → text-only previews on launch | **Fix at T-3d (§2).** This alone can cut X CTR ~30%. |
| Mismatched links (site says open-video/open-video, repo is robotlearning/open-video) | Transfer the repo BEFORE going public; grep the whole repo for `robotlearning123` before launch. |
| Single point of failure (you) | Have a second person on each channel for the first 4h; shared war-room doc with all logins. |

---

## 14. One-line summary

**Make a great film → make the repo public → deploy the site → open Discord → fire X → fire four
reddits → fire HN → ride PH all day → reply to everything for 4 hours. All on a Tuesday, in that
order, infra-confirmed before each post.**
