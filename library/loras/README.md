# OpenVideo LoRA Library — Community Fine-Tuned H3 Models

> **The Stable Diffusion LoRA explosion, for video.** Community-trained LoRAs make H3 better in specific domains (cinematic, anime, product, character, ad style). Anyone can train + contribute. This is the flywheel that closed platforms CAN'T match — they gate models; we welcome community-trained ones.

## How LoRAs work in OpenVideo
```
open-video gen "a product shot of a luxury watch" --lora product-photography-v2
```
The `--lora` flag loads a community-trained LoRA on top of the H3 base model, applying a domain-specific style/quality boost. The LoRA file is stored in `library/loras/<category>/<name>/`.

## Categories
| Category | Description | Example Use Cases |
|---|---|---|
| `cinematic/` | Film-grade color grading, lighting, camera work | Narrative shorts, trailers, mood pieces |
| `anime/` | Anime/2D animation style | Music videos, fan content, explainers |
| `product/` | Product photography quality (lighting, detail, rotation) | E-commerce, ads, demos |
| `character/` | Character consistency (face, clothing, motion) | Series, brand mascots, storytelling |
| `ad-style/` | Commercial/ad aesthetic (bold, clean, branded) | Social ads, brand campaigns |
| `vfx/` | Visual effects enhancement (particles, transitions) | Trailers, motion graphics |

## How to contribute a LoRA

### 1. Train
Use one of these tools (from our finetune research, Aug 2026):
- **musubi-tuner** (kohya-ss) — BF16 video LoRA (~65GB VRAM; R2 FP8 coming for consumer GPUs)
- **Inline Studio** — 4-bit QLoRA (~21GB VRAM, fits RTX 5090; static appearance/style only)
- **DiffSynth-Studio** — NF4 alternative

### 2. Package
Create a folder in `library/loras/<category>/<your-lora-name>/`:
```
library/loras/cinematic/my-cinematic-v1/
  ├── lora.safetensors       # the trained LoRA weights
  ├── meta.json              # metadata (see template below)
  ├── example_prompt.txt     # a prompt that showcases this LoRA
  └── before_after.mp4       # optional: base vs LoRA comparison
```

### 3. Submit
PR to this repo with your LoRA folder. Include:
- Training details (base model, dataset size, epochs, tool used)
- Before/after comparison (base H3 vs H3+LoRA on the same prompt)
- Trigger word (if needed)

See `templates/lora_recipe.md` for the contribution template.

## meta.json format
```json
{
  "name": "product-photography-v2",
  "category": "product",
  "description": "Enhanced product shot quality — studio lighting, macro detail, smooth rotation",
  "base_model": "minimax-h3-fl2va-pruned-int8-convrot",
  "trigger_word": "product_photography_style",
  "recommended_weight": 0.8,
  "training_tool": "musubi-tuner",
  "training_dataset": "10K product images + 500 product videos",
  "author": "your-github-username",
  "license": "Apache-2.0",
  "example_prompt": "A luxury wristwatch on a marble surface, studio lighting, macro detail, slow rotation"
}
```

## Why community LoRAs are our moat
Closed platforms (Runway, Seedance, Sora) **gate which models you use** — you get what they serve. OpenVideo **welcomes community-trained LoRAs** — anyone can train a domain-specific style enhancer and share it. This is what made Stable Diffusion explode (millions of community LoRAs on Civitai). OpenVideo brings the same pattern to video.

**The flywheel**: more LoRAs → more capabilities → more users → more LoRA contributors → more capabilities → #1.
