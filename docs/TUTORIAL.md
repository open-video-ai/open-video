# OpenVideo — Beginner's Tutorial

> **From zero to your first AI-generated film, even if you've never used an AI video tool.**
>
> This tutorial assumes nothing. If you can type a sentence and click a button, you can make a
> video with OpenVideo. No coding required for the main path. Everything is explained in plain
> language first, with the details available when you want them.

---

## Table of contents

1. [What is OpenVideo?](#1-what-is-openvideo)
2. [Install OpenVideo](#2-install-openvideo)
3. [Make your first video](#3-make-your-first-video)
4. [Use presets (cinematic / product / social templates)](#4-use-presets-cinematic--product--social-templates)
5. [Make a multi-shot film](#5-make-a-multi-shot-film)
6. [Use a community LoRA (apply a style)](#6-use-a-community-lora-apply-a-style)
7. [The quality loop, explained simply](#7-the-quality-loop-explained-simply)
8. [Share your work (contribute back)](#8-share-your-work-contribute-back)
9. [Troubleshooting & glossary](#9-troubleshooting--glossary)

---

## 1. What is OpenVideo?

**OpenVideo is a free, open-source tool that turns a written description into a finished video —
including planning the shots, checking its own work, and improving the result before handing it
to you.** You type what you want to see (for example, *"a neon koi swimming through rain"*), and
OpenVideo writes the detailed prompt, generates the clip, judges whether it actually looks good,
fixes it if not, and stitches multiple clips together into a longer film when you want one. Think
of it as a tiny AI film director that lives on your computer or on our website, costs nothing, and
runs on the best open video model available today (MiniMax H3).

> **In one line:** *If you can describe it, OpenVideo makes it.*

<details>
<summary><b>What does "open-source" mean for me?</b> (click to expand)</summary>

It means the software is free to use, free to modify, and free to share (Apache 2.0 license). You
are not locked into a subscription, a cloud account, or a single company. You can run it on your
own computer, use our free website, or pay only if you want our hosted GPUs later. The community
collectively owns the shared library of prompts and styles — including the ones you'll contribute.
</details>

![Screenshot: the OpenVideo concept box, where you type a description and press Generate](screenshots/01-concept-box.png)
*Placeholder — replace with a real screenshot of the concept input box.*

---

## 2. Install OpenVideo

There are **three ways** to use OpenVideo, from easiest to most flexible. Pick the one that
matches you. Most beginners should start with **Option A**.

| Option | Best for | Needs |
|---|---|---|
| **A. Web App** *(easiest)* | Anyone who wants a video in the next 2 minutes | A browser |
| **B. One-click installer** | People who want it on their own PC, offline | A Windows/Mac/Linux PC |
| **C. Manual install (command line)** | Developers and tinkerers | Python + an NVIDIA GPU |

> **Honest status (August 2026):** OpenVideo is **v0 / actively being built**. The command-line
> tool and core engine are working today; the one-click installer and the hosted web app are
> rolling out as part of the launch. Where a feature is still arriving, we say so clearly below.

### Option A — Use the Web App (no install, recommended for beginners)

1. Go to **[open-video.ai/try](https://open-video.ai/try)**.
2. Type your idea in the box. Press **Generate**.
3. Wait a short while. Your video appears on the page. Download it.

That's the whole flow. No software, no settings, no GPU needed — OpenVideo's computers do the
heavy lifting. It is free while the project is young.

![Screenshot: open-video.ai/try with a prompt typed in and a Generate button](screenshots/02-web-app.png)
*Placeholder — replace with a real screenshot of the web generation page.*

> **Tip:** While you're there, browse **[open-video.ai/gallery](https://open-video.ai/gallery)**.
> Every prompt there has already been tested and shows the video it produced — copy any prompt to
> remix it.

### Option B — One-click installer (run it on your own computer)

This is the "Ollama for video" experience: one installer, double-click, done.

1. Download the installer for your system from the **[Releases page](https://github.com/open-video-ai/open-video/releases)**:
   - Windows: `OpenVideo-Setup.exe`
   - macOS: `OpenVideo.dmg`
   - Linux: `OpenVideo.AppImage`
2. Run it. The installer downloads the model the first time (a few gigabytes — grab a coffee).
3. Open the **OpenVideo** app. You'll see the same concept box as the website, but it runs on
   **your** machine. No internet required after the first download, and your videos never leave
   your computer.

> **Status note:** the one-click installer ships with the full launch. If the installer isn't on
> the Releases page yet, use **Option A** (web) or **Option C** (command line) in the meantime.

![Screenshot: the OpenVideo desktop app showing the concept box](screenshots/03-desktop-app.png)
*Placeholder — replace with a real screenshot of the desktop app window.*

### Option C — Manual install (command line, for developers)

If you're comfortable with a terminal and have an **NVIDIA GPU** (about 10 GB VRAM minimum), you
can run OpenVideo straight from source today. The full step-by-step is in
[`docs/getting-started.md`](./getting-started.md); the short version:

```bash
# 1. Get the code
git clone https://github.com/open-video-ai/open-video.git
cd open-video

# 2. Check the orchestrator is healthy (prints a table with the "h3" model)
python cli/open_video.py list-models
```

Then install [ComfyUI](https://github.com/comfyanonymous/ComfyUI) (the engine that renders the
frames), drop the free H3 model weights into its `models/` folders, and start it. All of that is
walked through carefully in `getting-started.md`. Once ComfyUI is running, every example in this
tutorial also works from the command line like this:

```bash
python cli/open_video.py "your idea here" --duration 10 --output output/my_video.mp4
```

> **You don't need to read the rest of this tutorial at a terminal.** The examples below show the
> concept box / desktop app first (what most people use), with the matching command in a folded
> block for command-line users.

---

## 3. Make your first video

This is the moment. You're going to describe something and get a video back.

### Step 1 — Open OpenVideo

Open the **web app** (`open-video.ai/try`) or the **desktop app**. You'll see one big box that
says something like *"Describe your video."*

### Step 2 — Type a description (a "prompt")

Type what you want to see, in normal words. Be visual and specific — mention the subject, the
setting, the lighting, and how the camera moves.

**A good first prompt:**

> *a neon-lit koi fish swimming slowly through falling rain, soft reflections on wet asphalt,
> gentle camera dolly forward, cinematic, moody*

![Screenshot: the prompt typed into the concept box](screenshots/04-first-prompt.png)
*Placeholder — replace with a real screenshot of the prompt entered.*

### Step 3 — Press Generate

OpenVideo now does several things in the background (you'll see a progress indicator):
it expands your sentence into a detailed professional prompt, asks the model to render the clip,
and runs the **quality check** (more on that in section 7). This usually takes a minute or two.

### Step 4 — Watch and download

When it's done, your video plays right there. Like it? Click **Download**. Want a different take?
Press **Generate** again (or change a word in your prompt and regenerate).

![Screenshot: finished video playing with a Download button](screenshots/05-first-video.png)
*Placeholder — replace with a real screenshot of the finished video.*

<details>
<summary><b>Same thing on the command line</b></summary>

```bash
python cli/open_video.py "a neon-lit koi fish swimming slowly through falling rain, soft reflections on wet asphalt, gentle camera dolly forward, cinematic, moody" \
  --duration 8 --output output/koi.mp4
```

The video is saved to `output/koi.mp4`. The `--duration` is in seconds (a single clip is at most
15 seconds; longer than that makes a multi-shot film — see section 5).
</details>

> **Beginner tip — the 4 parts of a great prompt.** If you're stuck, build your sentence from four
> pieces: **Subject** (*a koi fish*) + **Setting** (*in rainy neon streets*) + **Lighting/mood**
> (*cinematic, moody*) + **Camera** (*slow dolly forward*). That structure reliably beats one-word
> prompts like *"a fish"*.

---

## 4. Use presets (cinematic / product / social templates)

A **preset** is a ready-made template for a *type* of video. Instead of describing every detail,
you pick a preset and OpenVideo applies the right look, length, and shot structure for you. It's
like choosing a "Photo Mode" on your phone, but for film.

OpenVideo ships with presets for the most common needs:

| Preset | Use it when | Example |
|---|---|---|
| **Cinematic Short** | A short narrative film, story-like, multi-shot | a 60-second mini story |
| **Product Ad** | Showcasing a product cleanly | a perfume bottle reveal |
| **Brand Ad** | A branded commercial look | a 30-second brand spot |
| **Social Clip** | Vertical short for TikTok / Reels / Shorts | a 9:16 attention-grabber |
| **UGC Ad** | "User-generated" native-feeling ad | a casual phone-style ad |
| **Micro Drama** | A punchy vertical micro-drama | a 30-second dramatic beat |
| **Trailer** | An exciting teaser cut | a movie-style trailer |
| **Music Video** | Visuals cut to a music vibe | an abstract music piece |
| **Explainer** | Clear, simple, illustrative | a 45-second explainer |

### How to use a preset

1. In the app, find the **Preset** selector (a dropdown above the concept box).
2. Pick one — say, **Product Ad**.
3. Type a short description of *your* subject: *"a glass perfume bottle with gold cap, rotating
   slowly on silk."*
4. Press **Generate**. OpenVideo applies the preset's length, aspect ratio, shot structure, and
   look automatically.

![Screenshot: preset dropdown open, "Product Ad" highlighted](screenshots/06-presets.png)
*Placeholder — replace with a real screenshot of the preset selector.*

> **What a preset actually changes:** the number and length of shots, the aspect ratio (16:9 for
> YouTube, 9:16 for social), the camera/style language added to each prompt, and the quality bar
> the judge enforces. You can always override any of it.

<details>
<summary><b>Browse presets on the command line</b></summary>

```bash
# List the preset library (these live in library/coherence_recipes/)
python cli/open_video.py list-presets
```

The preset files themselves are plain, readable YAML in
[`library/coherence_recipes/`](../library/coherence_recipes/) — open one (e.g.
`cinematic_short.yaml`) to see exactly which shots, durations, and settings it defines. You can
copy one and tweak it to make your own preset, then share it (see section 8).
</details>

---

## 5. Make a multi-shot film

A single clip is at most **15 seconds** long (that's a hard limit of today's video models). But
you often want a longer piece — a 1-minute story, a 90-second ad, a multi-scene short. OpenVideo
solves this by **planning a multi-shot film, generating each shot, and stitching them together**
into one coherent video.

### The idea

You give OpenVideo a longer concept. Behind the scenes it:

1. **Plans** — breaks your concept into scenes/shots (each ≤15s) and writes a "coherence bible" so
   the characters, style, and setting stay consistent from shot to shot.
2. **Generates** each shot, chaining them so the end of one shot flows into the start of the next
   (continuous motion).
3. **Judges + refines** each shot (the quality loop, section 7).
4. **Stitches** them together with smooth audio — and can optionally upscale to 2K.
5. **Delivers** one finished film.

### Try it

1. Open the app and switch the mode to **Film / Multi-shot** (or just type a long duration).
2. Type a richer concept, for example:

   > *A 90-second chase across a stormy harbour at dusk: a runner dashes past crates, a pursuit
   > through narrow alleys, ending on a rain-soaked pier looking back at the city.*

3. Set the length (e.g. **90 seconds**).
4. Press **Generate**. Go get a tea — multi-shot films take longer because each shot is rendered
   and quality-checked individually.

![Screenshot: multi-shot storyboard preview showing several planned shots](screenshots/07-multishot.png)
*Placeholder — replace with a real screenshot of the storyboard / multi-shot view.*

> **Honest v0 note:** the multi-shot *planner* is at its best when paired with a language model
> that writes each shot's prompt. OpenVideo falls back to template-based per-shot prompts when no
> planner LLM is configured, so the most polished long films come from the hosted app (where the
> planner is wired up). The stitching, chaining, and quality loop already work end-to-end.

<details>
<summary><b>Same thing on the command line</b></summary>

Any duration **above 15 seconds** automatically triggers a multi-shot plan:

```bash
python cli/open_video.py "a 90-second chase across a stormy harbour at dusk" \
  --duration 90 --output output/chase.mp4
```

Want to preview the plan without spending GPU? Add `--dry-run`:

```bash
python cli/open_video.py "..." --duration 90 --dry-run
```

That validates the prompt, builds the plan, checks that the engine is reachable, and exits — no
rendering.
</details>

---

## 6. Use a community LoRA (apply a style)

A **LoRA** (say *"low-rah"*) is a small, downloadable "style pack" that changes the look of the
video. Think of it like a filter or a lens: one LoRA might make everything look like a
hand-drawn anime; another might lock in a particular film-stock color grade; another might make a
specific product or character appear consistently across every shot.

The community builds and shares LoRAs, so there are styles for almost any taste — and you can
make your own (section 8). LoRAs in OpenVideo fall into five categories:

| Category | What it does | Example |
|---|---|---|
| **cinematic** | A film look/grade (film stock, lens, color) | "anamorphic 35mm" |
| **anime** | A 2D / illustrated aesthetic | "Studio Ghibli paint" |
| **product** | A specific product's exact look (for ads) | "Acme bottle 2026" |
| **character** | A specific person/creature's identity | "the lighthouse keeper" |
| **style** | An artist or studio's overall style | "Bauhaus motion design" |

### How to apply a LoRA (the easy way)

1. Browse the **LoRA gallery** (in the app, or on `open-video.ai/gallery`).
2. Find a style you like — e.g. an *anamorphic 35mm* cinematic LoRA.
3. Click **Use this style**. It gets attached to your next generation.
4. Type your prompt and press **Generate**. The style is applied automatically.

You can even **stack** up to three LoRAs on one video — for example, a *character* LoRA plus a
*cinematic* LoRA — to lock both the hero's identity and the film's color grade.

![Screenshot: LoRA gallery with a "Use this style" button on a style card](screenshots/08-loras.png)
*Placeholder — replace with a real screenshot of the LoRA/style gallery.*

> **Honest status note:** LoRA *selection* in the app and the `--lora` flag are landing alongside
> the first community-contributed LoRAs (the wiring is tracked in
> [`docs/library-and-loras.md`](./library-and-loras.md)). Today, any standard H3 LoRA
> `.safetensors` file you drop into `ComfyUI/models/loras/` already works with the underlying
> engine — OpenVideo's one-click UX is the convenience layer on top.

<details>
<summary><b>Same thing on the command line</b></summary>

The easy UX (once wired) is a single flag — `name@strength`, where strength defaults to 0.8:

```bash
python cli/open_video.py "a detective walking through neon rain" \
  --lora acme/anamorphic35mm@0.8 --output output/noir.mp4
```

Pull a LoRA from the gallery to your local machine first:

```bash
python cli/open_video.py lora pull acme/anamorphic35mm
```

The recipe (what the LoRA is, how it was trained, its trigger word, and a before/after pair)
lives in [`library/loras/`](../library/loras/). See [`library-and-loras.md`](./library-and-loras.md)
for the full LoRA contribution guide.
</details>

---

## 7. The quality loop, explained simply

This is the thing that makes OpenVideo different from a plain "type prompt, get video" tool:
**OpenVideo checks its own work and improves it before showing you the result.** We call this the
**quality loop**.

Here's the plain-language version of what happens after you press Generate:

1. **Make a first attempt.** OpenVideo generates a shot from your prompt.
2. **Watch it back.** It extracts frames from the video and a *vision judge* (an AI that can
   "see") looks at them and asks: *Does this match what the user asked for? Does it look good?
   Did anything drop out — a missing character, a broken motion, a wrong color?*
3. **Diagnose.** If something's off, the judge says specifically what — e.g. *"the rain
   disappeared in the second half"* or *"the camera moved the wrong way."*
4. **Fix and try again.** OpenVideo tweaks the prompt or settings based on that diagnosis and
   regenerates the shot.
5. **Repeat until it passes** the quality bar (or until it has tried a sensible number of times),
   then keep that version.

![Screenshot: the quality loop panel showing judge verdict and refine steps](screenshots/09-quality-loop.png)
*Placeholder — replace with a real screenshot of the judge/refine panel.*

**Why this matters to you:** you don't have to keep pressing Generate and hoping. OpenVideo does
that iterative "try, judge, fix" work itself, so the video you receive has already been
self-screened for quality. On average this means fewer broken, off-prompt, or glitchy clips —
and more clips that actually look like what you described.

> **Optional power-up — "best-of-N":** for the highest quality on a single important shot, you can
> ask OpenVideo to render a few different takes and keep the best one (a tournament). It uses more
> compute, so it's off by default and available per-shot when you want the absolute best result.

<details>
<summary><b>Under the hood (for the curious)</b></summary>

The loop is `generate → extract frames → judge(frames, prompt intent, quality bar)`. If the
verdict is **PASS**, the shot is kept. If **REFINE**, the judge returns specific issues, which
feed a targeted fix (a prompt tweak, more steps, a different mode, or a reference pack) and the
shot regenerates. This pattern is proven by Google's VISTA research (a +46% win rate via
best-of-N tournament + refine) and the VideoWeaver agent-as-judge approach. OpenVideo is the
first *open* video project to ship it. Full details: [`ARCHITECTURE.md`](../ARCHITECTURE.md).
</details>

---

## 8. Share your work (contribute back)

OpenVideo gets better for everyone when the community shares what works. The good news: the
easiest contributions take **under five minutes and no coding**.

### Easiest: share a prompt

Made a prompt that produced a great video? Share it so others can remix it.

1. In the app, on a result you like, click **Share prompt** (or copy the prompt text).
2. Fill in a title and a short note on what it's good for.
3. Submit. It goes into the public prompt library at `library/prompts/` and may appear on the
   gallery for others to copy.

That's it. A single good prompt is a real contribution.

### Share a LoRA (a style)

If you trained a LoRA for your character, product, or favorite look, share the *recipe* (the
how-to and a link to the weights). The full guide is in
[`docs/library-and-loras.md`](./library-and-loras.md); the short version:

1. Train your LoRA (the guide walks through the supported path).
2. Upload the weights to a host of your choice (Hugging Face, Civitai, your own site).
3. Copy the [`templates/lora_recipe.md`](../templates/lora_recipe.md) file, fill it in (trigger
   word, dataset summary, a before/after pair, license), and open a Pull Request.

> **Consent first:** only train on images/video you have the rights to, and get consent from any
> real, identifiable people. Non-consensual likeness LoRAs are rejected. See the review bar in
> [`library-and-loras.md`](./library-and-loras.md) §7.

### Other easy contributions

- **Reference pack** — turnaround sheets or lighting boards that help consistency across shots.
- **Showcase** — a film you made with OpenVideo, shared with the recipe that produced it (great
  for the gallery and for inspiring others).
- **Benchmark profile** — if you run OpenVideo on your GPU, share your settings and timings so
  others with the same card get good defaults.

<details>
<summary><b>Contribute via Pull Request (command line)</b></summary>

```bash
git clone https://github.com/open-video-ai/open-video.git && cd open-video

# Easiest: add a prompt recipe
cp templates/prompt_recipe.md library/prompts/my_idea.txt
# ... fill it in ...

git commit -m "prompt: add my_idea"
git push   # then open a PR on GitHub
```

The contribution guide with all options (prompt, LoRA, reference pack, model backend, judge
plugin, engine adapter) is in [`CONTRIBUTING.md`](../CONTRIBUTING.md).
</details>

![Screenshot: the community gallery page full of shared prompts and videos](screenshots/10-gallery.png)
*Placeholder — replace with a real screenshot of the gallery.*

---

## 9. Troubleshooting & glossary

### Common questions

| Problem | What to do |
|---|---|
| **My video looks nothing like my prompt.** | Add more visual detail (subject + setting + lighting + camera). Try a preset. If a key element is missing, name it explicitly. |
| **The result is glitchy / corrupted.** | Regenerate (the quality loop usually catches these, but a bad draw can slip through). Try a different seed. |
| **A character's face changes between shots.** | Use a *character* LoRA + reference pack for identity lock across shots. Keep framing tight on faces. |
| **Generation is slow.** | A single 8–10s clip takes a minute or two; multi-shot films take proportionally longer. On your own GPU, lower-end cards can use a smaller model quant (see `getting-started.md`). |
| **I don't have a GPU.** | Use the web app at `open-video.ai/try` — it runs on our GPUs. |
| **Web app says "generating…" for a long time.** | During busy periods there may be a queue. Wait, or try again shortly. |

### Plain-English glossary

- **Prompt** — the sentence(s) you type describing the video you want.
- **Clip / shot** — one continuous piece of video, at most 15 seconds long with current models.
- **Film** — a longer video made of multiple shots stitched together.
- **Preset** — a ready-made template for a type of video (ad, trailer, social clip…).
- **LoRA** — a small downloadable "style pack" that changes the look (a style, a character, a product).
- **Judge** — the AI that "watches" a generated clip and scores whether it matches your prompt and looks good.
- **Quality loop** — the make → judge → fix → remake cycle that polishes your video automatically.
- **Stitching** — joining multiple shots into one continuous video with smooth audio.
- **ComfyUI** — the open-source rendering engine OpenVideo drives behind the scenes (you don't need to touch it unless you want to).
- **H3 (MiniMax H3)** — the open video model OpenVideo uses by default; the #1 open model today.

---

### Where to go next

- **Browse the gallery:** [open-video.ai/gallery](https://open-video.ai/gallery)
- **Go deeper (plain-language architecture):** [`docs/architecture-overview.md`](./architecture-overview.md)
- **Set up locally (developers):** [`docs/getting-started.md`](./getting-started.md)
- **Compare open models:** [`docs/model-comparison.md`](./model-comparison.md)
- **Contribute:** [`CONTRIBUTING.md`](../CONTRIBUTING.md) · [`docs/library-and-loras.md`](./library-and-loras.md)

Welcome to OpenVideo. Go make something.
