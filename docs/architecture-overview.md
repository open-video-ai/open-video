# Architecture Overview (for non-developers)

> This is the plain-language version of [`ARCHITECTURE.md`](../ARCHITECTURE.md). No code, no
> jargon. If you are a creator, a PM, or just curious about how open-video turns a sentence into a
> finished film, start here.

---

## The one-sentence version

**open-video is an autonomous film director.** You describe the scene; it plans the shots,
shoots them, judges whether each take is good enough, fixes the ones that aren't, and stitches
the good takes into one coherent film.

It does not replace your video model — it *directs* one.

---

## A film-crew analogy

Think of a real film production. There is a **director** who decides what gets shot and whether a
take is good. There is a **camera operator** who actually records. And there is the **film stock
and lens** — the technology that produces the image.

open-video maps onto that exactly:

| Film role | open-video equivalent | What it is, really |
|---|---|---|
| **The director** | `open-video core/` | A piece of software that plans, judges, and decides. |
| **The camera operator** | **ComfyUI** (the engine) | A separate, popular open-source program that runs the actual rendering. open-video gives it instructions; it produces the frames. |
| **The film stock / lens** | The **model** (e.g. MiniMax H3) | The "brain" that knows how to turn text into video. You can swap this without changing the director or the camera. |

The crucial idea: **the director is the valuable part, and the director is what closed products
have and open projects didn't — until now.**

---

## What problem does open-video solve?

Today's open video models (the "film stock") are excellent — MiniMax H3, for example, scores
about as well on public benchmarks as the best closed products from big labs. The raw quality is
no longer the bottleneck.

The bottleneck is **everything around the model**:

- A model gives you a **single short clip** (typically under 15 seconds). It does not give you a
  *film*.
- A model does not **judge its own work**. If it drops a detail you asked for, it ships the broken
  clip anyway.
- A model does not **keep characters and style consistent** from one shot to the next.
- A model does not **stitch clips together** into a multi-minute story with continuous audio.

Closed products (Seedance, Sora, Veo) ship all of this as a polished agent — you type a prompt,
they hand you a finished film. Open models shipped as raw engines, leaving everyone to fiddle with
node-graphs manually.

**open-video is that missing agent layer, built open.** It sits on top of an open model and
behaves like a director: it turns the model's raw capability into a delivered film.

---

## The quality loop: how open-video "directs" itself

This is the heart of the project, and the thing no other open video tool has. It is a simple loop,
repeated until the take is good:

```
        ┌──────────────────────────────────────────┐
        │                                          ▼
   GENERATE  ──→  JUDGE  ──→  (good enough?)  ──→  REFINE
   a take          it               │                  │
                   │                no                 │
                   ▼                │                  │
                keep it ◄───────────┘                  │
                   │                                   │
                   ▼                                   │
              next shot ◄──────────────────────────────┘
```

In plain words:

1. **Generate** — open-video asks the model to render the shot.
2. **Judge** — it pulls frames out of the result and looks at them with a vision model
   (essentially "another AI watching the clip"). It asks: *does this match what the user asked
   for? Does it meet the quality bar? Did anything get dropped?*
3. **Decide** — if the take passes, keep it and move on. If not…
4. **Refine** — diagnose what went wrong (a missing detail? jerky motion? an inconsistent face?),
   write a targeted fix (a tweaked prompt, a different camera instruction, a reference image), and
   regenerate.
5. **Repeat** until the take is good, then move to the next shot.

There is an optional upgrade called **best-of-N**: render a few candidate takes at once and pick
the strongest. It costs more compute but raises the ceiling. open-video defaults to the cheaper
*diagnose-and-refine* approach and treats best-of-N as a knob you can turn on.

This loop is **the** reason open-video exists. It is the technique that closed labs proved works
(Google's VISTA research won ~46% more often with it), and it is what every open video project
has been missing.

---

## How a concept becomes a five-minute film

A model can only produce ~15 seconds at a time. So how do you get a *film*? open-video
**orchestrates** many shots into one continuous piece. The pipeline runs like this:

1. **Plan.** You give open-video a concept ("a 5-minute short about a lighthouse keeper and a
   storm"). It writes a **coherence bible** — a document that pins down the characters, the
   setting, the style, the props, and the story beats across acts and scenes. Then it breaks the
   story into individual shots, each under 15 seconds, each with continuity notes.

2. **Craft the prompt.** For each shot, open-video rewrites your intent into the *specific format
   that model understands best* (different models speak different "prompt grammars"). It also
   checks the prompt against the model's hard rules — maximum length, how many reference images
   are allowed, what aspect ratios work — and refuses to ship anything that breaks them.

3. **Generate.** It asks the model to render the shot. The first shot is generated from scratch;
   **each later shot starts from the last frame of the previous one**, so the camera and the
   characters flow continuously from cut to cut instead of jumping.

4. **Judge and refine.** The quality loop (above) runs on every shot.

5. **Stitch.** Once all shots pass, open-video concatenates them into one file, smooths the audio
   across cuts (keeping the music theme and dialogue language consistent), and optionally upscales
   the whole thing to 2K.

6. **Deliver.** You get one film file, plus a "receipt" for each shot — what was asked, what was
   generated, and what the judge decided. So you can audit the result.

The honest limitation: **stitched** continuity is not *native* continuity. A model that could do
five minutes in one go (some closed products aim for this) would not accumulate any drift between
shots. open-video mitigates this by running the judge at every cut, which catches drift early and
fixes it before it compounds. It is a real, visible gap — and the judge loop is the answer.

---

## Why "model-agnostic" matters (the swap-in design)

open-video's director does not know or care *which* model is rendering the frames. The model is a
pluggable **backend**. Today the default backend is **MiniMax H3** (the strongest open model
right now). Tomorrow it can be **Wan 2.2**, **HunyuanVideo**, **LTX**, or whatever comes next.

Each backend is one folder that translates the director's universal instructions into the
specifics that model needs: its prompt format, its hard limits, its best settings, its generation
modes. **Adding a model does not require changing the director.** You write one backend file and
plug it in.

Why this is a big deal:

- **You survive model churn.** The best open model today will not be the best in six months. A
  single-model wrapper goes stale; open-video just gains a new backend and inherits the new
  champion instantly.
- **You pick the right model per job.** One model is great at audio; another is faster; another
  handles physics better. open-video can route each shot to the model that suits it.
- **The community compounds.** When a contributor adds a backend, every open-video user benefits.
  Closed vendors' model know-how lives inside one company; ours lives in a shared, auditable
  library.

The same swap-in principle applies to the **engine** (today ComfyUI; tomorrow a direct diffusers
adapter) and to the **judge** (today a vision model; tomorrow VideoScore or a human-in-the-loop).

---

## The community library (the part that compounds)

The director gets better the more it has to work with. open-video ships with — and invites the
community to grow — a **library** of reusable know-how:

- **Prompt recipes** — tested prompts that produce reliably good results on a given model.
- **Reference packs** — turnaround sheets and lighting boards that lock a character's identity
  across shots.
- **Coherence recipes** — pre-built story bibles for common film types (a chase, a conversation,
  a nature vignette).
- **Style profiles** — aesthetic presets and style tweaks.

Every recipe in the library is meant to be tested and shown alongside its result, so the library
doubles as living proof that open-video works. This shared, growing body of craft is something
closed vendors structurally cannot match — their know-how is locked inside a company; ours is a
public commons.

---

## TL;DR

- open-video is **the director**, not the camera and not the film stock.
- It sits on top of an **open model** (H3 today) and an **open engine** (ComfyUI) and behaves
  like an autonomous filmmaker.
- Its core IP is the **judge → refine → best-of-N loop**: the only reason open video can match
  closed products' *delivered* quality, not just raw clip quality.
- It is **model-agnostic**: swap the model without rewriting the director.
- It builds **long films** by planning, multi-shotting, chaining continuity, judging each cut, and
  stitching — turning 15-second clips into a five-minute story.

If you want the technical contract behind all of this (classes, interfaces, the file layout), the
canonical reference is [`ARCHITECTURE.md`](../ARCHITECTURE.md).
