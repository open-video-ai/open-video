# open-video — Plan

> The autonomous director layer on ComfyUI + open models. Seedance-grade long films, open.
> Baseline: MiniMax H3 (#1 open, Arena parity with closed). Domain: open-video.ai.

## Positioning (locked)
- **Layer ON ComfyUI** (engine incumbent, 124k★/$500M) — drive it via API, don't replace it.
- **Open answer to Seedance's closed agentic long-video pipeline.** Seedance (closed) already does
  long film agentically; open-video does it open + local + model-agnostic + community.
- **Differentiator = the brain ComfyUI lacks**: planner/coherence-bible + judge→refine loop +
  multi-shot stitcher + reference-pack builder. ComfyUI = manual node-graph; open-video = autonomous director.

## The long-film pipeline (how a concept → 5-min film) — the core IP
1. **Plan** — given a concept, the planner writes a **coherence bible** (logline → acts → sequences
   → shots), each shot ≤15s (H3 ceiling), with continuity anchors (characters/style/props/lighting).
2. **Craft + validate** — each shot → H3 3-field prompt (style-first, bracketed, camera prose,
   dialogue tags); mode-aware **validator** hard-gates (duration/ref-counts/timeline/dialogue).
3. **Generate** — shot 1 (T2V or FL2VA from seed image); shot N+1 = **FL2VA with first_frame =
   previous shot's last frame** (continuous handoff); optional reference-packs for identity lock.
4. **Judge** — extract frames; a **vision judge** scores each shot vs intent + a quality bar
   (the loop we prototyped in the H3 verify — productized).
5. **Refine** — below bar → diagnose (dropped element? bad motion? inconsistency?) → targeted fix
   (prompt tweak / more steps / different mode / ref-pack) → regenerate. (Optional best-of-N.)
6. **Stitch** — concat shots; cross-shot audio continuity; **2K upscale via API** optional.
7. **Deliver** — one coherent multi-minute film + per-shot receipts.

This is exactly the capability Seedance ships closed; open-video ships it open, on H3 (+future
backends), with community-contributed coherence recipes.

## Architecture seam (model + engine agnostic)
- **core/** (model-agnostic): planner, crafter, validator, judge-loop, stitcher, ref-pack, selector.
- **backends/&lt;model&gt;/** (plugin): capabilities, prompt_grammar, modes→workflow, constraints,
  settings, quant_opts. H3 = plugin #1.
- **engines/&lt;engine&gt;/** (adapter): open-video talks to the engine API. ComfyUI = adapter #1.
→ Add a model = write a backend plugin (core unchanged). Add an engine = write an adapter.

## Phases
- **Phase 0 — thesis proof (now)**: H3 backend + ComfyUI adapter + core loop (planner/crafter/
  validator/judge/stitcher). **Success = a real ~1–5 min open film, vision-judged coherent**, that
  holds up next to a Seedance short on the same concept. Buy/confirm domain, pick license.
- **Phase 1 — open + community**: open-source core (license), `library/` (prompts/ref-packs/
  coherence-recipes) as the flywheel, Discord, partner with ComfyUI/H3 ecosystems, add a 2nd
  backend (Wan3 / FLUX3-Dev when open) to prove model-agnostic.
- **Phase 2 — hosted**: managed open-video SaaS/API (bring-your-key or our GPUs) + enterprise
  license (AGPL dual). Unit-economics hinge on an efficient judge loop (refine-few, not best-of-many).
- **Phase 3 — marketplace**: premium coherence-recipes / style LoRAs / reference-packs; take rate.

## Competitive map
| | what | open? | relation to open-video |
|---|---|---|---|
| **ComfyUI** | engine (node-graph), 124k★/$500M, marketplace | yes (GPL) | **partner** — open-video drives it |
| **Seedance 2.x** | closed top; **has agentic long-video pipeline** | no (API) | **the target to match/beat open** |
| **Sora/Veo/Kling** | closed top | no | quality ceiling reference |
| **MiniMax H3** | #1 open model, Arena parity w/ closed | yes | **baseline backend** |
| **Wan 2.2 / Hunyuan 1.5 / LTX-2.3** | weaker open (no/less audio, lower Elo) | yes | future backends / speed tier |
| **Open-Sora / Mochi** | open but lower quality/community | yes | distant cousins |
| **woodfantasy Seedance skill** | agentic skill, but closed-model only | skill open | pattern reference (port to open) |

## Open decisions (need your call)
1. **License**: AGPL (open-core, anti-white-label) vs Apache (max adoption). Lean: **AGPL core + commercial license** (you're explicitly fighting closed vendors).
2. **Judge loop strategy**: single-generate + diagnose-refine (cheap) vs best-of-N (quality, GPU×K). Lean: **refine-primary** (H3 quality is already at parity; loop fixes adherence/length, not raw quality) — best-of-N as optional.
3. **Engine-first vs standalone**: build on ComfyUI (engine adapter) from day 1, or also a standalone runner? Lean: **ComfyUI-first** (where the users are), standalone later.
4. **Phase-0 scope**: prove the loop on a **1-min** film first (cheaper) then scale to 5-min? Lean: **1-min first** as the milestone, 5-min as the stretch demo.

## Success metric (make-or-break)
**An open-video-generated open film, vision-judged (cx GPT-5.6 + Opus 4.8) as coherent and at least
on-par with a Seedance-generated short on the same concept.** That single result proves the thesis
(open + agent ≥ closed) and is the project's reason to exist + its best community/marketing asset.
