# Agentic Workflow — generate any video with best quality (MiniMax H3, RTX 5090)

The pipeline turns a request into the best-quality local H3 video. Patterns adopted from the
Seedance `woodfantasy/Seedance2.0-ShotDesign-Skills` skill module (see SEEDANCE_COMPARISON.md).
Implemented across `.claude/skills/h3-video/SKILL.md` + `scripts/h3_agent.py` +
`scripts/validate_prompt.py`.

## The loop (request → delivered video)
1. **Intake** — text request; optional images (first/last frame), refs (img/video/audio).
2. **Intent → mode routing** (first step, before anything else):
   - no inputs → **T2V**; 1 image → **I2V**; 2 images → **FL2VA**; identity/style/voice refs → **R2V**.
3. **Prompt crafting** — transform the request into the OFFICIAL 3-field structure
   (`docs/PROMPT_GUIDE.md`): style-first shot with increasing cut times, camera motion as prose
   (type+amplitude+speed), dialogue `<d>[lang] verbatim</d>` with speaker IDs, then
   `overall_soundscape` (1–4 s) + `non_diegetic_music` (1–3 s, no mood words). Every detail visible/audible.
   - For best results use an LLM crafter; the **IT2V system prompt** (`cushycrux/H3_LLM_Instructions`)
     is a drop-in prompt-generator that forces this structure. `h3_agent.py --request` does a basic
     template expansion; pass a hand/LLM-crafted `--prompt` for top quality.
4. **Pre-delivery validation gate** — `scripts/validate_prompt.py` (mode-aware): checks 3 fields,
   duration 4–15 s, image/ref counts per mode, instruction line, timeline cut times strictly
   increasing & within duration, well-formed dialogue tags. **Hard gate** — block on issues.
5. **Reference-pack construction** (R2V/multi-shot) — the #1 consistency lever (AtlasCloud finding):
   build a composite turnaround sheet + lighting board; bind each asset a role/scope/exclusion with
   `<Picture 1>`/`<Video 1>`/`<Audio 1>` tokens. Don't feed scattered multi-angle files.
6. **Best settings** (`docs/BEST_PRACTICES.md`) — **1344×768** (16:9 ~1.0 MP, multiple 32), **20 steps**,
   `res_multistep` + `simple` (R2V → `beta`/`normal`), shift 12/3, duration 5–8 s. CFG-distilled → no neg prompt.
7. **Generate** — `scripts/h3_agent.py` → ComfyUI (`--lowvram --use-sage-attention`, avoids NVFP4/#14157).
8. **Review** — extract frames (`ffmpeg` tile), inspect; for shipping run cross-model visual review
   (cx GPT-5.6 + Opus 4.8 per repo rules).
9. **Refine** — if quality poor, fix prompt (most common), settings, or reference pack; regenerate.
10. **Deliver** — mp4 to `output/`, receipt to `artifacts/verify/agent_<mode>_<ts>.json`.

## Design principles (from Seedance ecosystem)
- **Skill module, not monolith** — knowledge in SKILL.md + lazily-loaded docs; the host agent orchestrates.
- **Mode routing before generation** — pick mode, validate per-mode constraints first.
- **Hard validator as the self-refine loop** — `validate_prompt.py` is a real constraint check, not a soft "retry".
- **Reference pack > model choice** — consistency comes from how refs are packed.
- **Cost = pixels-per-frame × regenerations** — "first-try success" is the measurable goal; regenerations dominate cost.
- **Separate API layer from prompt design** — clean separation (the MCP pattern).

## Customization hooks (see FINETUNING.md)
- **No-FT (today)**: IT2V system prompt (prompt crafting) · Ref2VA identity anchoring · Ultra-Heretic TE (uncensored, private — takedown risk) · official style templates.
- **LoRA on 5090**: Inline Studio 4-bit QLoRA (~21 GB, static-image appearance only) — fits; video/motion LoRA needs musubi R2 (FP8/NVFP4), pending.

## 2K (when needed)
Local caps at 768p. For 2K, run the API chain (H3-Context-IR → Base → H3-Regenerate-2K, $0.13/s); it
won't accept a local 768p render. See OFFICIAL_FEATURES.md.

## Quickstart
```bash
cd /mnt/data/workspace/55-ai-video
# craft prompt → validate → generate → review
./venv/bin/python scripts/h3_agent.py --prompt "$(cat prompts/cinematic_cityspeed.txt)" \
  --width 1344 --height 768 --duration 5 --seed 0
# or all official examples:
bash scripts/run_official_examples.sh
```
