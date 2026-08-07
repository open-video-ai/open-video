# Library & LoRA Contribution Guide

> Shared **prompts, LoRAs, reference packs, coherence recipes, and showcases** — open and
> remixable. This guide covers layout, how to train/contribute an H3 LoRA, and how loading is
> intended to work. Much of the UX (`lora pull`, gallery) is **planned**; weights stay off-repo.
>
> **Audience:** creators training LoRAs, developers wiring LoRA loading, anyone contributing to
> `library/`. For prompt-only contributions see `CONTRIBUTING.md` + `templates/prompt_recipe.md`.

---

## 1. The library — five directories

`library/` is the shared, versioned asset store. Every asset is a file (or small bundle) +
metadata, PR'd like code:

| Directory | What lives here | Format | Smallest unit |
|---|---|---|---|
| `library/prompts/` | Curated, model-specific prompt recipes that produce good results | `.txt` (3-field for H3) | one prompt → one file |
| `library/loras/` | Community-trained H3 LoRA recipes (metadata + links, not the weights) | `.md` recipe + off-repo weights | one LoRA → one recipe |
| `library/reference_packs/` | Turnaround sheets, lighting boards, identity refs for consistency | `.yaml` + image bundle | one pack → one dir |
| `library/coherence_recipes/` | Pre-built coherence bibles for common film types (trailer, ad, micro-drama…) | `.yaml` | one film type → one file |
| `library/showcase/` | Flagship outputs that prove a recipe works (prompt + LoRA + result + verdict) | `.md` + linked media | one showcase → one file |

**Goal:** good recipes are tested, shown with results when possible, and easy to remix. A public
gallery is Phase 1+ work (`PLAN.md`) — not required to contribute a prompt or LoRA recipe today.

### What goes where (decision tree)

- *I have a prompt that looks great on H3* → `library/prompts/` (copy `templates/prompt_recipe.md`).
- *I trained a LoRA on my character/product/style* → `library/loras/` (copy
  `templates/lora_recipe.md`).
- *I have turnaround sheets that lock a subject's identity across shots* →
  `library/reference_packs/`.
- *I have a reusable storyboard/coherence plan for a film type* → `library/coherence_recipes/`.
- *I made a film with open-video and want to show it off (with the recipe that produced it)* →
  `library/showcase/`.

LoRA **weights are not committed to the repo** (large binary, license-varies). The repo holds the
**recipe** (training method, dataset summary, trigger word, settings, before/after) and a link to
where the weights live (HF / Civitai / your own host). See §6.

---

## 2. LoRA categories

LoRA recipes are tagged with one primary `category` so the gallery, selector, and search can filter
them. The five primary categories:

| Category | Trains for | Typical use | Example trigger |
|---|---|---|---|
| **cinematic** | Look/grade: film stock, lens character, lighting style, color science | Give a whole film a consistent visual treatment | `anamorphic35mm`, `bleach-bypass` |
| **anime** | 2D/illustrated aesthetic on top of H3's photoreal base | Anime/OVA/stylized shots that H3 doesn't do natively | `ghibli-paint`, `90s-cel` |
| **product** | A specific SKU: packaging, material, logo, form factor | Shot-to-shot product consistency in ads (brand fidelity) | `acme-bottle-2026` |
| **character** | A specific person/creature's identity (face, build, wardrobe) | Lock a hero character across a multi-shot film | `lighthouse-keeper` |
| **style** | An artist/studio/motion-design house style (broader than one subject) | "Make it look like X" without naming a single subject | `studio-bauhaus-motion` |

**Multi-category recipes are fine** — list a primary `category` and secondary `tags`. Example: a
LoRA that locks one character *and* their cinematic grade → `category: character`,
`tags: [cinematic, color-grade]`. The selector reads `category` first, `tags` for refinement.

### Naming convention

`library/loras/<category>/<your_name>__<short_slug>.md`, e.g.
`library/loras/character/acme__lighthouse_keeper.md`. Keep slugs lowercase, ASCII, hyphen-free
(use underscores); the slug becomes the LoRA's `id` once registered.

---

## 3. Contributing a community H3 LoRA

H3 shipped with **no official trainer** (the community is filling the gap — see `docs/h3_ecosystem.md`
§"Community finetune pipeline"). open-video documents and supports **two training paths** depending
on what you're trying to lock and what hardware you have. Both produce a `.safetensors` LoRA that
drops into `ComfyUI/models/loras/` and loads through the standard `LoraLoader` node.

### Path A — Static appearance QLoRA (now, ~21 GB on RTX 5090)

**Tool:** Inline Studio (QLoRA on the frozen H3 backbone).
**Trains:** a single static *appearance* — one character's face/wardrobe, one product, one
style — from a small image set, fast, on a single 5090-class GPU.
**Best for:** `character`, `product`, `style`, `anime` categories where the goal is "this exact look
across shots." **Not** for motion/temporal behavior — it locks appearance, not how a subject moves.
**Footprint:** ~21 GB VRAM (5090 confirmed). Fits the same machine you generate on.

When to pick Path A: you want identity/style lock for a short film or ad and you want it today.
This is the default path for community contributors in Phase 1.

### Path B — Full video LoRA (when R2 FP8 lands)

**Tool:** musubi-tuner (the community video-LoRA trainer; the same stack that drove HunyuanVideo /
Wan LoRA training).
**Trains:** temporal/motion behavior on **video** data, not just static images — gait, camera
movement style, motion design idents, physics behavior.
**Best for:** `cinematic` (motion grade), motion-design `style`, behavioral `character` (how someone
moves, not just how they look).
**Blocker:** full-video H3 LoRA training needs the **R2 FP8** build of the backbone to fit a
single-GPU budget. Until that lands, use Path A for appearance and rely on prompts + the judge loop
for motion. We'll update this guide the day R2 FP8 is available.

> **Honest status (2026-08):** Path A is the supported, testable path today. Path B is documented
> so contributors can prep datasets and be ready; the trainer entrypoint will be wired into
> `bench/` + a `tools/train/` helper when R2 FP8 ships. If you have multi-GPU access and want to
> attempt Path B sooner, open a Discussion first — we'll link your experiment.

### Dataset rules (both paths)

- **Consent + license first.** Only train on images/video you have the rights to train on. Real
  people need their consent. Don't contribute a LoRA that reproduces a living, non-consenting
  person's likeness — these are rejected at review. See §7.
- **15–80 reference frames** for a static appearance LoRA is usually enough; video LoRAs want
  20–200 short clips. More isn't better if it's redundant.
- **Caption every frame/clip** with the trigger word you intend to use at inference. The LoRA only
  fires when the trigger is present, so the trigger must be in the training captions.
- **Vary the background/lighting/angle** for `character`/`product` so the LoRA learns the subject,
  not the backdrop.
- **Keep one variable** — train one subject per LoRA. Mixing two characters in one LoRA produces a
  blend neither contributor wanted.

### Contribution flow

1. Train your LoRA (Path A or B).
2. Upload the `.safetensors` to HF / Civitai / your host under a license you can relicense
   (Apache-2.0-compatible preferred; Creative Commons / commercial-restricted is allowed but must
   be tagged `license_restricted: true` in the recipe).
3. `cp templates/lora_recipe.md library/loras/<category>/<your_name>__<slug>.md` and fill it in.
4. Generate a **before/after pair** on H3 with the same seed + prompt (one without the LoRA, one
   with). Drop the trigger word in the "after" prompt. Link both.
5. PR. Review checks: trigger word present, before/after legible, license field set, dataset
   consent line filled in.

---

## 4. How open-video loads LoRAs (the `backend.lora` → `LoraLoader` contract)

LoRAs in open-video flow through the **backend**, not the core — the core is model-agnostic and
doesn't know what a LoRA is. The contract:

```
intent (with optional lora id + strength)
  → core passes lora through ShotRequest.extra["lora"] = {"id": ..., "strength": 0.8}
    → backend.generate() reads it, resolves the id → safetensors path,
      and injects a ComfyUI LoraLoader node into the workflow
      → engine (ComfyUI) applies it at diffusion time
```

### Per-shot, per-LoRA

A LoRA is selected **per shot** (not globally), so a film can use one `character` LoRA for the hero
shots and a different `cinematic` LoRA for the grade shots. The planner reads a coherence bible's
`lora` hints (per-shot) and the selector never overrides a contributor's explicit LoRA choice.

### Strength + stacking

- `strength` (a.k.a. weight) defaults to **0.8** for video LoRAs (lower than the SDXL 1.0 default —
  video LoRAs are usually trained on a frozen backbone and overpower quickly). Tune in 0.05 steps.
- Up to **3 LoRAs can stack** per shot (e.g. `character` + `style` + `cinematic`). Each gets its own
  strength; the backend chains `LoraLoader` → `LoraLoader` → model in the workflow.

### Where the weights live

LoRAs resolve from `ComfyUI/models/loras/`. The recipe's `weights_url` is downloaded once by
`open-video lora pull <id>` (mirrors HF/Civitai into the local loras dir) and referenced by `id`
thereafter. Recipes never hardcode absolute paths.

### Wiring status (honest)

The `lora` field on `ShotRequest.extra`, the `LoraLoader` injection in `backends/h3/backend.py`, and
the `open-video lora pull` helper are the **target contract** described here. The H3 backend today
builds the workflow from `backends/h3/workflows/*.json` and runs the standard model path; LoRA
injection lands alongside the first contributed LoRA. **Contributors can train now** (Path A
produces a standard safetensors that any `LoraLoader` consumes) — the open-video wiring is the
trivial part and tracks the first real LoRA, not the other way around.

If you want to wire the injection yourself, it's a `good first issue`: read the trigger `id` +
`strength` from `req.extra["lora"]` in `H3Backend.generate()`, splice a `LoraLoader` node between
the loader and the sampler in the workflow dict, and PR. See `CONTRIBUTING.md` §"Model backend".

---

## 5. Why community LoRAs matter

Closed video APIs usually ship a fixed model with no user-trained adapters. Open image ecosystems
(e.g. Stable Diffusion + community LoRAs) showed that **permissionless training + sharing** covers
more niches than one vendor catalog: product kits, anime looks, characters (with consent), regional
styles, brand packs.

open-video wants the same pattern **for video on H3**: train a LoRA, publish a recipe + weights
link, others remix. That is a product thesis, not a claim that thousands of LoRAs already exist
here.

Keep contributions **video-focused** and consent-first (§7).

---

## 6. The LoRA recipe template (reference)

Every LoRA contribution is **one recipe file** in `library/loras/`. The template is
`templates/lora_recipe.md` — copy it, fill it in, PR. The fields:

- **Metadata** — `id`, `category`, `tags`, `author`, `license`, `weights_url`, `base_model`.
- **Training** — `method` (Inline Studio QLoRA / musubi-tuner video LoRA), `dataset_summary`,
  `steps`, `gpu`, `vram`, `trigger_word`, `training_repo_url`.
- **Usage** — `recommended_strength`, `stacks_with`, `example_prompt` (H3 3-field, with trigger),
  `tips`.
- **Before/after** — same seed + prompt, one render without the LoRA, one with the trigger. Linked
  media (off-repo). This is the proof the LoRA does something and is the gallery asset.
- **Consent + provenance** — dataset source, consent status, any usage restrictions.

The recipe is the contract between the contributor and every downstream user (the gallery, the
selector, the `lora pull` helper, and the judge loop, which uses the before/after pair as a sanity
check that the LoRA fired). Fill every field; gaps get sent back at review.

See `templates/lora_recipe.md` for the canonical copy-paste-ready version.

---

## 7. Review bar, consent, and what we reject

LoRA PRs are reviewed against four checks:

1. **Consent** — real, identifiable, living people in the training set must have consented. No
   non-consensual likeness LoRAs. No deepfake-of-private-person LoRAs. (Public figures fall under
   the standard "don't be a creep" norm; when in doubt, don't.)
2. **License honesty** — the recipe's `license` field must match what the weights are actually
   released under. Commercially-restricted LoRAs are allowed but tagged `license_restricted: true`
   and excluded from the hosted gallery's "remix freely" filter.
3. **Does what it claims** — the before/after pair must visibly show the effect. A LoRA whose
   before/after are indistinguishable gets sent back.
4. **Trigger word fires** — the example prompt must include the `trigger_word` and the after-render
   must show it activating. LoRAs that silently do nothing waste every downstream user's GPU.

What we **don't** reject: niche aesthetics, rough drafts, duplicate-but-different-take LoRAs,
non-English captions. The bar is consent + honesty + works, not taste.

---

## 8. Quick start

```bash
git clone <open-video> && cd open-video

# 1. Train (Path A today, on your 5090)
#    Inline Studio QLoRA → my_character.safetensors

# 2. Upload weights (HF / Civitai / your host), copy the recipe template
cp templates/lora_recipe.md library/loras/character/acme__my_character.md

# 3. Fill in the recipe (trigger word, dataset summary, before/after links, license)

# 4. Generate your before/after pair on H3 (same seed + prompt, trigger only in "after")
#    open-video "..." --lora acme/my_character@0.8   (once §4 wiring lands)

# 5. PR
git add library/loras/character/acme__my_character.md
git commit -m "lora: add acme__my_character (character, Inline Studio QLoRA)"
git push
```

Thanks for contributing.
