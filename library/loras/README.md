# OpenVideo LoRA Library — Community Fine-Tuned H3 Models

> Community-trained LoRAs specialize H3 (cinematic, anime, product, character, style). Anyone can
> train and contribute a **recipe** (weights stay off-repo). Full guide:
> [`docs/library-and-loras.md`](../../docs/library-and-loras.md).

## How LoRAs are intended to work

```
open-video run "a product shot of a luxury watch" --lora product-photography-v2
```

The `--lora` UX and `lora pull` helper are the **target contract** (see library guide §4). Today,
standard H3 `.safetensors` files in ComfyUI’s `models/loras/` can already be used via workflows.

## Categories

| Category | Description | Example use |
|---|---|---|
| `cinematic/` | Film-grade look, lighting, camera | Narrative shorts, trailers |
| `anime/` | Anime / 2D aesthetic | Stylized clips |
| `product/` | Product / studio look | Ads, demos |
| `character/` | Identity lock | Series, mascots |
| `ad-style/` | Commercial aesthetic | Social ads |
| `vfx/` | Effects-oriented looks | Trailers, graphics |

## How to contribute a LoRA

### 1. Train
- **Inline Studio** — QLoRA (~21GB VRAM; static appearance/style)
- **musubi-tuner** — full video LoRA (higher VRAM; R2 FP8 path when available)
- **DiffSynth-Studio** — NF4 alternatives

### 2. Package (recipe in-repo, weights off-repo)

Prefer a single recipe markdown (see `templates/lora_recipe.md`) under
`library/loras/<category>/`, with `weights_url` pointing at HF / Civitai / your host.

If you use a folder layout:

```
library/loras/cinematic/my-cinematic-v1/
  ├── meta.json              # metadata
  ├── example_prompt.txt
  └── before_after links     # media off-repo
```

Do **not** commit large `.safetensors` into git.

### 3. Submit
PR with training notes, before/after, trigger word, license, and consent line.

## meta.json sketch

```json
{
  "name": "product-photography-v2",
  "category": "product",
  "description": "Studio lighting, macro detail, smooth rotation",
  "base_model": "minimax-h3-fl2va-pruned-int8-convrot",
  "trigger_word": "product_photography_style",
  "recommended_weight": 0.8,
  "training_tool": "inline-studio",
  "author": "your-github-username",
  "license": "Apache-2.0",
  "weights_url": "https://huggingface.co/..."
}
```

## Why contribute

Shared adapters let others reproduce looks closed APIs never ship. Consent and license honesty
are mandatory (`docs/library-and-loras.md` §7).
