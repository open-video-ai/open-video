# open-video — Public plan (v0.1.0)

> Short product plan for contributors.

## What shipped (v0.1.0)

- Local **MiniMax H3** via ComfyUI (`open-video pull` / `status` / `run`), INT8 weights verified against a packaged manifest
- Agent skill harness: `skill/h3-video`
- Recipe-in-render metadata (atomic embed; read via `open_video.core.recipe.read_recipe`)
- Opt-in VLM judge → bounded refine loop; honest `SKIPPED` verdict when no VLM is configured
- Reliability: unique I2V/FL2V staging via `OPEN_VIDEO_COMFYUI_INPUT`, real engine-error propagation
- Install path + product site (install/docs; `/try` is a UI mockup, not free cloud GPU)
- Scaffolding under `core/` for planner/stitcher (not a finished multi-minute director)

## Design direction (honest labels)

| Area | Status |
|---|---|
| Single-shot H3 generate | **Shipped** |
| Agent prompt skill | **Shipped** |
| Vision judge → refine loop | **Shipped (opt-in)** — real `vision_fn` via `OPEN_VIDEO_VLM_*`; `SKIPPED` honestly when unset |
| Multi-shot plan + stitch | **Experimental / partial** |
| 2nd model backend | **Planned** |
| Hosted generate / desktop app | **Not shipped** |
| Marketplace / take rate | **Not a product claim** — do not document as current |

## Architecture seam (unchanged intent)

- **`core/`** — model-agnostic helpers (planner, judge, stitcher as they land)
- **`backends/<model>/`** — model plugins (H3 first)
- **`engines/<engine>/`** — runtime adapters (ComfyUI first)
- **`skill/` + CLI** — interfaces that work today

## Success for the next milestone

A coherent multi-shot open demo with a **real** vision review, run end-to-end and documented
with receipts — **not yet verified**; do not claim it as passing until the run exists.

## Open decisions (engineering)

1. Judge strategy: single-generate + diagnose-refine vs optional best-of-N
2. Engine path: ComfyUI-first (current), other runners later
3. When to open external PRs / gallery once the tree is public

License: **Apache-2.0** (decided).
