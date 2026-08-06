# Open Video Model Comparison

> A comparison of the open video models open-video targets, **from open-video's integration
> perspective**: which one is wired up today, what each is good at, and which you should reach for.
>
> **Scope and honesty:** MiniMax H3 numbers and capabilities are quoted from this repo (it is the
> integrated backend, so they are verified against the code). Wan 2.2, HunyuanVideo, and LTX are
> **planned backends, not yet integrated** — their cells reflect how open-video positions them and
> what the open-video planning docs say. Open model specs move fast (licenses, audio variants,
> VRAM optimizations change month to month). **Always confirm exact specs on the model card
> before relying on them.**

---

## At a glance

| Model | open-video status | License | Native audio? | Quality tier (Arena Elo) | VRAM floor | open-video role |
|---|---|---|---|---|---|---|
| **MiniMax H3** | **Integrated** (default backend) | Open weights *(verify on [model card](https://huggingface.co/MiniMaxAI/MiniMax-H3))* | **Yes** — 32 kHz stereo | **#1 open** (T2V #2 / I2V #3 overall, Elo ~1238/1189) | **~8 GB** (NF4) → ~21 GB (INT8 default) | Baseline: **audio + prompt adherence** |
| **Wan 2.2** | Planned | **Apache-2.0** (clean license — per `PLAN.md`) | Limited / add-on *(verify)* | Below H3 *(see Arena)* | *(verify on card)* | **Physics / motion realism** anchor |
| **HunyuanVideo** | Planned | Tencent — community license *(verify clauses on card)* | None in base *(verify)* | Below H3 *(see Arena)* | High at full precision *(verify)* | General T2V/I2V quality tier |
| **LTX (Video)** | Planned | Open *(verify on card)* | None in base *(verify)* | Below H3 *(see Arena)* | Low *(verify)* — real-time target | **Speed tier** (drafts / previews) |

> Cells marked *(verify)* mean: open-video's docs characterize the model this way, but the exact
> number/clause should be confirmed on the upstream model card before you depend on it. Audio in
> particular is a fast-moving target — open models ship audio-capable variants over time.

---

## MiniMax H3 — the baseline (integrated today)

- **What it is:** MiniMax's open video model (also marketed as Hailuo 3.0). Text-to-video,
  image-to-video, first-last-frame interpolation, and reference-video, all with **native stereo
  audio** baked in.
- **Why it is the default:** On the Artificial Analysis Arena it is the **#1 open** model and sits
  at **T2V #2 / I2V #3 overall** (Elo ~1238/1189) — within benchmark noise of the closed #1
  (Gemini Omni Flash ~1244 / Seedance ~1197). The raw quality is already there.
- **Capabilities open-video uses:** 3-field prompt grammar, FL2VA/T2V/R2V workflows, 4–15 s per
  shot, 768 px short edge, six aspect ratios, 24 fps with a 17k+5 frame grid.
- **VRAM tiers** (verified in [`h3_ecosystem.md`](./h3_ecosystem.md)): NF4 from ~8 GB, W4 ConvRot
  ~10 GB, INT8 ConvRot ~21 GB (open-video's default, proven on RTX 5090), BF16 ~62 GB.
- **Role in open-video:** the model that handles **audio and prompt adherence** — the things a
  director cares most about when assembling a film with dialogue and a soundscape.
- **Honest caveats:** ~15 s per shot (so long films must be stitched); wide shots can corrupt
  faces (Comfy-Org #30); avoid NVFP4 on RTX 5090 (ComfyUI #14157). All documented in
  [`h3_ecosystem.md`](./h3_ecosystem.md).

---

## Wan 2.2 — the clean-license physics anchor (planned)

- **What it is:** Wan-AI's open video model family. Historically ships a small and a large
  variant; the large is a serious open contender.
- **Why open-video wants it:** a **clean Apache-2.0 license** with no community-use ambiguity,
  which matters for commercial and enterprise deployments that H3's licensing may complicate.
  `PLAN.md` calls Wan 2.2 the "Apache-2.0 clean-license global anchor."
- **Role in open-video:** the model routed to when the shot needs **plausible physics and motion
  realism** (per `ARCHITECTURE.md`'s selector). Where H3 does audio + adherence, Wan is the
  motion/physics specialist.
- **Gap vs. H3:** weaker prompt adherence and (in current open variants) less native audio
  (`PLAN.md` characterizes the non-H3 open models as "no/less audio, lower Elo").
- **Verify before using:** exact variant list, audio support, and VRAM on the Wan-AI model card.

---

## HunyuanVideo — the general-quality tier (planned)

- **What it is:** Tencent's open video DiT. A large, capable text-to-video / image-to-video model
  from a major lab.
- **Why open-video wants it:** a strong general-purpose open baseline, useful as a second opinion
  in best-of-N routing or for shots where its particular strengths win.
- **Role in open-video:** planned backend — a quality-tier option alongside H3 and Wan.
- **Watch-outs:** Tencent ships under a **community license** that has historically included
  commercial-use clauses and a scale threshold. **Confirm the current terms on the model card**
  before any commercial use; this is the main reason open-video treats it as optional rather than
  a clean-license anchor.
- **Gap vs. H3:** no native audio in the base model and below-H3 benchmark numbers per open-video's
  current characterization.
- **Verify before using:** license clauses, VRAM at the quant you intend to run, and the latest
  audio-capable variant (if any).

---

## LTX (Video) — the speed tier (planned)

- **What it is:** Lightricks' open video model, designed for **real-time / near-real-time
  generation** at low VRAM.
- **Why open-video wants it:** not every shot needs the heaviest model. LTX is the **draft and
  preview** tier — fast iterations on framing and timing before committing GPU budget to H3 for
  the final take. `ARCHITECTURE.md` assigns LTX the **"speed"** role in the per-request selector.
- **Role in open-video:** the model routed to when throughput matters more than peak fidelity
  (storyboard previews, rapid prompt iteration, low-end hardware).
- **Gap vs. H3:** lower fidelity and no native audio in the base model. It is a complement to H3,
  not a replacement.
- **Verify before using:** exact license, current VRAM floor, and supported modes on the LTX
  model card.

---

## How open-video stays neutral (the model-agnostic contract)

The reason this comparison is not a death match is that **open-video does not pick a winner**. Its
core director is **model-agnostic**: every model is a pluggable backend that implements the same
contract (capabilities, prompt grammar, constraints, settings, generate). Adding a model is one
folder; the director does not change.

That means:

- **Today** the director drives H3 because it is the strongest open model right now.
- **Tomorrow**, when a stronger open model ships, the community writes a backend for it and
  open-video inherits it instantly.
- **Per shot**, the selector can route to whichever model fits that shot best — H3 for a dialogue
  beat, Wan for a physics-heavy action beat, LTX for a quick storyboard pass.

This is the structural advantage over single-model wrappers and over closed products whose model
is a fixed black box. The director survives model churn; the community library of recipes and
reference packs compounds across every backend.

See [`ARCHITECTURE.md`](../ARCHITECTURE.md) for the backend contract (`ModelBackend` /
`Capabilities` / `ShotRequest`) and [`CONTRIBUTING.md`](../CONTRIBUTING.md) for how to add a new
model backend.

---

## Which model should I use?

| If you want… | Reach for… |
|---|---|
| The best open quality today, with sound | **MiniMax H3** (the default) |
| A clean Apache-2.0 license for commercial use | **Wan 2.2** (when integrated) |
| A second quality option / best-of-N diversity | **HunyuanVideo** (mind the license clauses) |
| Fast drafts, previews, or low-VRAM generation | **LTX** (the speed tier) |

If you only install one model today, make it **H3** — it is the only integrated backend and the
one the getting-started flow targets. See [`getting-started.md`](./getting-started.md).

---

## Keeping this table honest

Open video models evolve quickly. If a number above is stale or you have run a model that open-video
does not yet list, the most useful contribution is a **backend plugin** (see
[`CONTRIBUTING.md`](../CONTRIBUTING.md)) or an updated benchmark profile in `bench/`. The
canonical H3 ecosystem reference — quants, samplers, speedups, known issues — lives in
[`h3_ecosystem.md`](./h3_ecosystem.md).
