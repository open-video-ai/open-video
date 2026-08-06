# OpenVideo — Positioning

> **The definitive positioning document.** This is the canonical source of truth for how OpenVideo
> describes itself — to users, contributors, partners, press, and the community. If a README,
> website, or pitch disagrees with this file, **this file wins** (then we update the other one).
>
> Status: **v0 / planning** · License: **Apache 2.0** · Domain: **open-video.ai**
> North star: **100K★ — the #1 open video project + community.**
> Baseline model: **MiniMax H3** (the #1 open video model, at Arena parity with closed).

---

## 0. The one-line pitch (TL;DR)

> **OpenCode is to Cursor what Open Design is to Claude Design what OpenVideo is to Runway.**
>
> Shorter: **OpenCode → Cursor. Open Design → Claude Design. OpenVideo → Runway.**

Unpacked: *Cursor* is the polished, closed, commercial AI coding product. *OpenCode* is its open alternative — same destination, open road. *Runway* (and *Seedance*) are the polished, closed, commercial AI video products. **OpenVideo is their open alternative** — the autonomous director that turns today's open models into a delivered film, open and free.

Everything below is a fuller telling of that one line.

---

## 1. The analogy: OpenCode → Cursor, OpenVideo → Runway

The structural pattern is identical across both domains, and it is the single most useful frame for explaining OpenVideo to anyone in 15 seconds.

| | **Closed incumbent** | **Open alternative** | **What the open layer actually adds** |
|---|---|---|---|
| **Code** | Cursor — closed AI code editor | OpenCode | An open, local, model-agnostic coding *brain* on top of open models and open tooling. |
| **Video** | Runway / Seedance — closed AI video | **OpenVideo** | An open, local, model-agnostic video *director* on top of open models (H3) and an open engine (ComfyUI). |

Three things make the analogy hold, not just sound good:

1. **The closed product is a whole product; the open world has the parts but not the product.** Cursor wraps open models into a polished editor; before OpenCode, the open side had the models but no polished agent. Runway/Seedance wrap video models into a polished director; before OpenVideo, the open side had H3 (arena-parity quality) but **no director** — only a manual node-graph (ComfyUI). OpenVideo is the missing product layer.
2. **The differentiator is the agent layer, not the model.** Open models have closed the raw-quality gap. The remaining gap is the *brain* that plans, judges, refines, and stitches. That brain is exactly what closed products ship and what the open world lacked — until now.
3. **Open wins the same way in both: local, free, private, extensible, community-owned.** The product arrives at parity; openness is what compounds past it.

**One caution when using this analogy:** the specific closed peer we are technically racing is **Seedance** (it already ships a closed agentic long-video pipeline). **Runway** is the category shorthand everyone recognizes. Use *Runway* for broad audiences ("the open Runway"), use *Seedance* for technical/competitive audiences ("open answer to Seedance's long-film pipeline"). Both are accurate; pick by audience.

---

## 2. Why OpenVideo is the open alternative to Runway/Seedance

Because the three things that make Runway/Seedance good are now available open, and the three things that make them painful are exactly what openness fixes.

### The quality is already there (open models caught up)
MiniMax H3 is the **#1 open** video model and sits at **T2V #2 / I2V #3 overall** on the Artificial Analysis Arena (Elo ~1238/1189) — **within benchmark noise of the closed #1** (Gemini Omni Flash ~1244 / Seedance ~1197). The raw model quality is no longer the gap. (Numbers from `README.md` / `docs/model-comparison.md`; re-check Arena before quoting in press — Elo drifts.)

### The remaining gap is the agent layer, not the model — and that is our core IP
Closed products ship a *director*: a planner, a prompt-crafter, a judge→refine loop, a multi-shot stitcher. Open models ship as **single-shot engines** (ComfyUI = manual node-graph; no judge, no refine, no stitch). OpenVideo is that director, open:

- **Planner** — concept → coherence bible (logline → acts → sequences → shots ≤15s, with continuity anchors).
- **Crafter + validator** — each shot → model-specific 3-field prompt; mode-aware hard-gate on duration/refs/timeline/dialogue.
- **Generate with handoff** — FL2VA chain: each shot's last frame seeds the next (continuous handoff beyond the 15s ceiling).
- **Judge** — vision judge scores each shot vs intent + a quality bar (the VISTA/VideoWeaver pattern, productized).
- **Refine** — below bar → diagnose → targeted fix → regenerate. Optional best-of-N.
- **Stitch + deliver** — concat shots, cross-shot audio continuity, optional 2K upscale, **per-shot receipts**.

This is the capability Seedance ships closed and natively; OpenVideo ships it open, via orchestration, on community infrastructure. *Honest gap, stated plainly:* stitched coherence is weaker than a single native long generation (drift accumulates across shots); the judge loop exists to catch drift at each transition. We lead with the orchestration story, not by claiming native coherence we don't have.

### Openness fixes what closed breaks
- **Cost & lock-in** — closed APIs bill per second and own your workflow; OpenVideo runs free on your GPU.
- **Region restrictions** — closed products geo-block; OpenVideo runs anywhere hardware exists.
- **Opacity** — closed products are a black box (you get an MP4 and a bill); OpenVideo ships open, exportable, reproducible workflows.
- **Censorship** — closed products refuse concepts; OpenVideo has no content filter because it runs on your machine.
- **Model churn** — closed products are one model, fixed; OpenVideo is model-agnostic and inherits every future open model as a plugin.

---

## 3. The dual DNA: OpenArt (product) + OpenCode (business) + Open Design (agent packaging)

> See also `docs/REFERENCES.md` for live URLs and install-UX parity.


OpenVideo is built from two open-source archetypes. **OpenArt contributes the *product* DNA. OpenCode contributes the *business-model* DNA.** Neither alone is enough; the combination is the point.

| DNA strand | Inspired by | What it gives OpenVideo |
|---|---|---|
| **Product DNA** | **OpenArt** | A polished, end-user-facing *product*, not just a library or engine. App-first UX, a verified gallery, presets, "for everyone." |
| **Business DNA** | **OpenCode** | A sustainable open-core *business*: Apache 2.0, hosted tier, enterprise license, marketplace. The open-source-commercial playbook. |

### Product DNA (OpenArt) — "ship a product, not a node-graph"
The lesson: an open project can and should ship a beautiful, usable artifact for non-technical people — not just an engine for developers. Concretely, this is why OpenVideo has **three interfaces**, with the **App primary**:

| Interface | For | Experience |
|---|---|---|
| **App** (primary) | Everyone — PMs, creators, non-technical | Natural language → video. Presets, storyboard preview, one-click generate. *Like ChatGPT/Canva for video.* |
| **CLI / API** | Developers | `open-video "concept" --duration 300` or REST. Automate, integrate, extend. |
| **Skill** | Agent hosts (Claude Code, Cursor) | `SKILL.md` — OpenVideo as a skill inside your AI workflow. |

And why the flagship community surface is a **Verified Prompt Gallery** (`open-video.ai/gallery`): every prompt is tested on H3 with the output shown alongside (prompt → video → quality verdict). Browse, copy, remix. This is the flywheel seed *and* the public proof that OpenVideo works — the OpenArt pattern applied to video.

> Without the product DNA, OpenVideo is "ComfyUI with a judge step" — technically interesting, culturally invisible. The product DNA is what makes it reach the 100K★ community, not just the 1K★ Hacker News crowd.

### Business DNA (OpenCode) — "open core, sustainable"
The lesson: open-source can build a real commercial layer **without closing the core**, and that is what funds longevity. The phased business, lifted from the open-core playbook:

- **Phase 1 — open + community**: Apache 2.0 core; `library/` (prompts, reference-packs, coherence recipes, style LoRAs) as the flywheel; Discord; partner with ComfyUI/H3 ecosystems.
- **Phase 2 — hosted**: managed OpenVideo SaaS/API (bring-your-key or our GPUs) + **enterprise license** (Apache 2.0, so the core stays free; enterprises pay for hosted/SLA/support).
- **Phase 3 — marketplace**: premium coherence-recipes / style LoRAs / reference-packs; take-rate.

> Without the business DNA, OpenVideo is a brilliant repo that dies when the maintainer gets bored. The business DNA is what funds the judge loop's GPU economics and the hosted tier that makes "for everyone" literally true.

### Why both, and why now
Open-source video has tried **product-without-business** (beautiful demos, no sustainability) and **business-without-product** (API wrappers around a single model, no moat). The dual DNA is the third path: a genuinely open *product* with a genuinely open *business*. Open models finally being at parity (H3) is what makes 2026 the moment this combination becomes viable.

---

## 4. Focus: video generation ONLY (not all-modalities)

**OpenVideo generates video. That is the entire product.** It is a *film director*, not a general-purpose AI studio.

### What "video" includes
The moving-image artifact **and its native audio**. H3 ships stereo audio; OpenVideo treats dialogue, music continuity, and soundscape as part of the film and orchestrates them (cross-shot audio continuity in the stitcher). Audio that is *part of the video* is in scope.

### What is explicitly OUT of scope
- ❌ **Standalone image generation** (we consume reference images as inputs; we don't compete with image models).
- ❌ **Standalone music generation** (we use audio that ships with the video model or that you provide; we are not a DAW).
- ❌ **3D asset generation.**
- ❌ **Code/document/artifact generation** of any non-video kind.
- ❌ **"All-modalities" / AGI studio** positioning of any flavor.

### Why this focus
1. **Depth beats breadth.** The director IP — coherence bible, judge→refine loop, multi-shot stitching, reference-packing — is *video-specific*. Spreading to images/music/3D would dilute the one IP that matters.
2. **The incumbents we're beating are video-first too.** Runway and Seedance are video products. We win by being a *better, open* video director — not by being a worse, open everything-studio.
3. **The open ecosystem already covers the rest.** ComfyUI is the broad node-graph engine (124k★); image, music, and 3D open tools exist. OpenVideo partners with that ecosystem; it does not try to absorb it.
4. **The flagship demands focus.** A coherent 5-minute open film is impossible without a single-minded director. Half-measures across modalities produce no film at all.

**The test for any feature request:** *"Does this make OpenVideo generate better, longer, or more coherent video?"* If yes, in scope. If it's "also generate X (non-video)," out of scope — route it to the ecosystem partner that owns X.

---

## 5. Brand guidelines

### The name, in two registers

| Register | Name | Where it lives |
|---|---|---|
| **Public / product / marketing** | **OpenVideo** | Website copy, README hero, docs prose, press, social, Discord, the product UI, the gallery. One word, capital O, capital V. |
| **Code / technical** | **open-video** | GitHub repo (`open-video`), Python package, CLI binary (`open-video "..."`), import paths, config files, URLs under `open-video.ai`. Lowercase, hyphenated. |

**Rule of thumb:** if a human reads it as a *product*, it's **OpenVideo**. If a machine types it as a *command or path*, it's **open-video**.

- ✅ "OpenVideo turns a description into a finished film." (product prose)
- ✅ `pip install open-video` · `open-video "a neon city at dawn" --duration 60` (code)
- ✅ Domain: **open-video.ai** (hyphenated, matches the code register)
- ❌ "Open-Video" (never hyphenate the product name)
- ❌ "open video" two words as a proper noun (fine as a generic adjective, wrong as the brand)
- ❌ "OpenVideoAI", "OV", or other invented variants in primary branding

### Domain, license, north star
- **Domain:** `open-video.ai`
- **License:** **Apache 2.0** (max adoption, contributor-friendly; chosen over AGPL for ecosystem growth). State it wherever the repo is mentioned.
- **North star:** **100K★ — the #1 open video project + community.** This is the success metric everyone rallies to.

### Voice
- **Honest, evidence-first.** We cite Arena Elo, VRAM floors, and per-shot receipts. We state our gaps (stitched vs native coherence) plainly. We never claim we beat closed on raw model quality — we claim *parity* on quality and *open advantage* on everything else.
- **For everyone, not just devs.** The hero speaks to PMs and creators; the docs speak to developers. Both registers are "us."
- **Partner, don't fight.** We lift ComfyUI (the engine), H3 (the model), and the community ecosystem. We never position ourselves as replacing them.

### Quick style reference
| Say | Don't say |
|---|---|
| "the autonomous director" / "director layer" | "a video engine" (ComfyUI is the engine) |
| "model-agnostic; H3 is the baseline backend" | "an H3 wrapper" / "a model" |
| "open alternative to Runway / Seedance" | "Runway killer" / "better than Sora" |
| "from concept to film, for everyone" | "AGI video studio" / "all-modalities" |
| **OpenVideo** (product) / **open-video** (code) | Open-Video, open video (as brand) |

---

## 6. The three unique advantages vs closed

Closed products can outspend us on models and polish. They **cannot** match these three, because each is a structural consequence of being closed that they cannot copy without stop being closed.

### Advantage 1 — Local-first, private, no censorship
OpenVideo runs **entirely on your own GPU**: from ~8 GB VRAM (NF4 quant) up to ~21 GB (INT8 default, proven on RTX 5090), or full BF16 on multi-GPU. Your prompts, reference imagery, and raw footage **never leave your machine**. There is no API key, no usage logging, no server-side content filter, and no regional block.

- **Privacy:** film studios, enterprises, and anyone with footage they can't upload get a tool that actually shows up. Closed products log your prompts and inputs server-side; OpenVideo physically cannot, because it runs on your hardware.
- **No censorship:** closed products refuse concepts; OpenVideo has no content filter to refuse with. (Note: the *upstream model* may have its own baked-in tendencies; the *platform* adds none.)
- **No region locks:** closed products geo-block; OpenVideo runs anywhere a GPU exists.
- **No per-second billing:** closed APIs charge by the second of output; OpenVideo's cost is your electricity.

### Advantage 2 — Pluggable community LoRAs, reference-packs, and coherence recipes
The `library/` is a **shared, compounding know-how base**: style LoRAs, identity turnaround sheets, lighting boards, verified prompt recipes, and pre-built coherence bibles for common film types. Any contributor drops in a LoRA or a recipe and **every user inherits it instantly**.

- **Closed vendors' craft knowledge is internal** — locked inside their company, invisible, non-transferable.
- **Ours is a public library** that grows with every contributor and compounds across every backend model.
- This is the **structural moat**. Closed can outspend us on a single model; they cannot out-compound a community library that turns their own internal best-practices into a public good. When the next open model ships, the entire library carries over to it unchanged — because the core is model-agnostic.

### Advantage 3 — Open, exportable, reproducible workflows
The entire pipeline — planner → crafter → validator → judge → stitcher — is **open Python and open ComfyUI workflows**, not a black box. Every generation ships with **per-shot receipts**: the prompt, the settings, the judge's verdict, and the fix log.

- **Audit:** you can read exactly how a film was made.
- **Modify:** you can fork a workflow and change any step.
- **Reproduce:** given the same inputs and settings, you get the same result — and you can prove it.
- **Port:** workflows are engine- and model-portable (ComfyUI adapter today; diffusers/sglang later; H3 today, Wan/LTX tomorrow).
- Closed products hand you an MP4 and a bill. There is no workflow to inspect, no receipt to verify, no way to reproduce or adapt the result. OpenVideo's workflows are a **public artifact you own**.

> These three advantages share one root: **the value lives on the user's side of the fence, not the vendor's.** That is what "open" buys, and it is the one thing a closed competitor structurally cannot replicate.

---

## 7. Tagline options

Pick by context. The **hero** tagline is the default everywhere; the others serve specific surfaces.

### Hero (default, everywhere)
- **"Open-source autonomous video generation — from concept to film, for everyone."**
  *(Current README hero. Lead with this unless you have a reason not to.)*

### Analogy-forward (investors, press, technical audiences)
- **"OpenCode is to Cursor as OpenVideo is to Runway."**
- **"The open alternative to Runway."**
- **"Cursor for video — open."**

### Product / benefit (website, gallery, onboarding)
- **"If you can describe it, OpenVideo makes it."**
- **"Direct your film, in the open."**
- **"From concept to film, open and free."**

### Community / mission (Discord, GitHub, contributor outreach)
- **"Building the #1 open video community — 100K★."**
- **"Open models. Open engine. Your film."**
- **"The open film studio."**

### Technical (CLI `--help`, docs, README tagline line)
- **"The autonomous director layer on ComfyUI + open models."**
- **"An open, model-agnostic video director. H3 today, every open model tomorrow."**

### Anti-taglines (do NOT use)
- ❌ *"The open Sora / open Veo / open Kling"* — anchors us to a closed product we don't need; use Runway/Seedance instead.
- ❌ *"Better than [closed model]"* — we claim parity + openness, not superiority on raw quality.
- ❌ *"AI video for everyone"* / *"All-in-one AI studio"* — collapses into the all-modalities trap; we do video only.
- ❌ *"The free Runway"* — price is a feature, not the positioning.

---

## Appendix A — Positioning do / don't (contributor cheat-sheet)

**DO**
- Anchor on the **director layer**: planner + judge→refine + stitcher. That is the IP.
- Cite **H3 as the #1 open model at Arena parity with closed**, then say the agent layer is the remaining gap.
- Lead with **"from concept to film, for everyone"** and the three interfaces (App / CLI-API / Skill).
- Credit **ComfyUI** (engine) and **H3** (model) as partners we build on.
- State the **Apache 2.0** license and the **open-core** business openly.
- Use **OpenVideo** for the product, **open-video** for the code.

**DON'T**
- Don't call OpenVideo a "video engine" or a "model" — it is the director on top.
- Don't claim OpenVideo beats closed on **raw model quality**. We are at parity; we win on the agent layer + openness.
- Don't promise **native single-generation long films** — we *stitch* shots (state the honest gap).
- Don't position as **all-modalities**. Video only.
- Don't quote **specific Arena Elo / VRAM numbers** in press without re-checking them — they drift (see `docs/model-comparison.md`).
- Don't invent new brand variants (**OpenVideoAI**, **OV**, hyphenated **Open-Video** as a product name).

---

## Appendix B — Where this positioning comes from (sources)

- `README.md` — thesis, three interfaces, "what it is / isn't," why it can win.
- `PLAN.md` — locked positioning (layer on ComfyUI; open answer to Seedance), long-film pipeline, competitive map, phased business, open decisions.
- `ARCHITECTURE.md` — the director components, the quality loop, the honest stitched-vs-native gap.
- `docs/model-comparison.md` — verified H3 numbers + the model-agnostic contract.
- `docs/h3_ecosystem.md` — the community ecosystem OpenVideo integrates (plugin-first, not reinvent).

> **Honesty note:** Arena Elo, VRAM floors, and competitor capabilities move quickly. This document states the *positioning* (durable); for *numbers*, always re-verify against `docs/model-comparison.md` and the upstream model cards before publishing. The positioning is locked; the numbers are tagged "verify" wherever they appear in the docs.
