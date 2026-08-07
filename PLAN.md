# open-video — Public plan (v0.0.1)

> Short product plan for contributors. Competitive war-room, valuation, and GTM live in the
> **private** ops repo — not here.

## What shipped (v0.0.1)

- Local **MiniMax H3** via ComfyUI (`open-video pull` / `status` / `run`)
- Agent skill harness: `skill/h3-video`
- Install path + product site (install/docs; `/try` is a UI mockup, not free cloud GPU)
- Scaffolding under `core/` for planner/judge/stitcher (not a finished multi-minute director)

## Design direction (honest labels)

| Area | Status |
|---|---|
| Single-shot H3 generate | **Shipped** |
| Agent prompt skill | **Shipped** |
| Vision judge → refine loop | **Scaffold** — needs a real `vision_fn` |
| Multi-shot plan + stitch | **Designed / partial** |
| 2nd model backend | **Planned** |
| Hosted generate / desktop app | **Not shipped** |
| Marketplace / take rate | **Not a product claim** — do not document as current |

## Architecture seam (unchanged intent)

- **`core/`** — model-agnostic helpers (planner, judge, stitcher as they land)
- **`backends/<model>/`** — model plugins (H3 first)
- **`engines/<engine>/`** — runtime adapters (ComfyUI first)
- **`skill/` + CLI** — interfaces that work today

## Success for the next milestone

A coherent multi-shot open demo with a **real** vision review (not the PASS stub), documented
with receipts — not star-count goals on the README.

## Open decisions (engineering)

1. Judge strategy: single-generate + diagnose-refine vs optional best-of-N
2. Engine path: ComfyUI-first (current), other runners later
3. When to open external PRs / gallery once the tree is public

License: **Apache-2.0** (decided).
