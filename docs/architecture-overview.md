# Architecture Overview (for non-developers)

> Plain-language companion to [`ARCHITECTURE.md`](../ARCHITECTURE.md).
>
> **Thesis / roadmap** — not a claim that every piece below already works end-to-end.  
> **v0.0.1 ships:** local MiniMax H3 generate + CLI / agent skill. Judge loop and multi-minute
> film are the design direction with early scaffolding.

---

## The one-sentence version

**open-video aims to be an autonomous film director on open models.** You describe the scene;
the stack plans shots, drives a render engine, (eventually) judges takes, and stitches good ones
into a longer film.

Today, the reliable path is: **craft a strong H3 prompt → generate a short clip on your GPU.**

It does not replace your video model — it *directs* one (when the full loop is wired).

---

## A film-crew analogy

| Film role | open-video equivalent | What it is, really |
|---|---|---|
| **The director** | `core/` | Software that plans, validates, and (later) judges. |
| **The camera operator** | **ComfyUI** (the engine) | Popular open program that runs the actual rendering. |
| **The film stock / lens** | The **model** (e.g. MiniMax H3) | Turns text/refs into video. Swappable via backends. |

Closed products bundle director + cloud model. Open stacks often ship only the model + a node
graph. open-video’s thesis is the missing **open director layer**.

---

## What problem does open-video solve?

Open models like MiniMax H3 already produce strong short clips. Gaps around the model:

- A model gives a **short clip** (often ≤15s), not a finished multi-scene film.
- A model does not **judge its own work** unless something sits on top.
- Consistency across shots and **stitching** need orchestration.

**Roadmap:** open-video sits on an open model + ComfyUI and behaves more like a director over time.
**Today:** use it as Ollama-style local H3 + quality prompt harness.

---

## The quality loop (design target)

```
        ┌──────────────────────────────────────────┐
        │                                          ▼
   GENERATE  ──→  JUDGE  ──→  (good enough?)  ──→  REFINE
   a take          it               │                  │
                   │                no                 │
                   ▼                │                  │
                keep it ◄───────────┘                  │
```

1. **Generate** a take.
2. **Judge** frames vs the prompt (needs a real vision backend).
3. **Refine** or keep.
4. Optional **best-of-N**.

**v0 honesty:** `core/judge.py` is a scaffold; without `vision_fn` it may auto-PASS. Research
(e.g. VISTA-style loops) motivates the design — we do not claim a finished live critic today.

---

## How a longer film *would* be built (orchestration)

1. **Plan** — coherence bible + shot list.
2. **Craft** — model-specific prompts + hard validation.
3. **Generate** — chain last frame → next first frame when possible.
4. **Judge / refine** — when wired.
5. **Stitch** — ffmpeg concat + audio continuity.
6. **Deliver** — film + receipts.

**Limitation:** stitched continuity is weaker than one native long generation. That gap is real.

---

## Why model-agnostic backends matter

The director core should not hardcode one model forever. **H3** is the working backend today;
Wan / LTX and others are future plugins under `backends/`. Engines (ComfyUI first) and judges are
similarly swappable.

---

## The community library

Shared recipes compound usefulness:

- Prompt recipes, coherence recipes, reference packs, LoRA recipes (weights off-repo).

This is a **commons**, not a marketing “moat” slogan. Contribute via PRs when the tree is open to
you (`CONTRIBUTING.md`).

---

## TL;DR

- **Thesis:** open-video is the **director**, not the model and not ComfyUI itself.
- **Shipped now:** local H3 + skill/CLI quality path.
- **Building toward:** judge → refine, multi-shot stitch, more backends.
- **Read next:** [`ARCHITECTURE.md`](../ARCHITECTURE.md), [`PLAN.md`](../PLAN.md),
  [`TUTORIAL.md`](./TUTORIAL.md).
