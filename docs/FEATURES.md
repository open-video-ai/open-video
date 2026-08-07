# OpenVideo — features (honest map)

> **Roadmap, not a “ships today” list.** v0.0.1 is local MiniMax H3 + CLI/skill.  
> Aligns with [`PLAN.md`](../PLAN.md) and the README “what works today” table.

## Shipped (v0.0.1)

| Feature | Surface |
|---|---|
| Install / pull / status / run | `open-video` CLI · `scripts/install.sh` · site install host |
| Local MiniMax H3 on ComfyUI | `backends/h3` · `engines/comfyui` |
| Agent skill (official-style prompts) | `skill/h3-video` |
| Product site (install + docs; try mockup) | `open-video-web` → open-video.ai |

## Scaffold / partial (do not market as finished)

| Feature | Status |
|---|---|
| Vision quality loop (judge → refine) | `core/judge.py` scaffold; PASS without `vision_fn` |
| Multi-shot plan + stitch | design + partial core modules |
| Long-film director skill | `skill/open-video` evolving |

## Planned (later)

| Feature | Notes |
|---|---|
| Second model backend | e.g. Wan — plugin path exists, not default |
| Real vision judge wiring | open/local vision preferred |
| Contributor gallery | when library + site ready |
| Hosted generate / desktop app / MCP | only when real — not current surfaces |
| Plugin registry install UX | see `PLUGIN_REGISTRY.md` (**spec only**) |

## Explicit non-claims

- Not a free cloud GPU product today (`/try` is a browser mockup).
- Not a multi-minute Seedance-grade director in v0.0.1.
- Not a marketplace / take-rate product in v0.0.1.

Longer design essays belong in architecture docs with **design** labels — not as shipped features.
