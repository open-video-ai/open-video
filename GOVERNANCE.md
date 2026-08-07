# open-video — Governance & Quality Doctrine

Adopted (as principles, reimplemented — not copied) from the best of the open agentic-video
ecosystem (OpenMontage's honest governance + woodfantasy's validation discipline).

## Quality-first doctrine
**open-video's product IS quality.** Unlike pipelines that cap revisions and ship-with-warnings
("perfectionism kills pipelines"), open-video's identity is: **the quality loop (judge → best-of-N
→ refine) runs until the output meets the bar — or the user is honestly told it can't.**
This is the differentiation vs OpenMontage (advisory 2-round reviewer, no VLM judge) and ViMax
(closed-API, creative-loop not quality-loop).

## Hard prohibitions (non-negotiable — silent violation = critical bug)
1. **Silent quality downgrade is forbidden.** Never quietly reduce resolution, swap to a weaker
   model, skip the judge, or fall back to a lower-quality mode without logging + user notification.
2. **Still-image fallback is forbidden.** Never convert a video generation job into a Ken Burns /
   animatic / slideshow without explicit disclosure. Motion-led video stays motion-led.
3. **Silent model swap is forbidden.** If the selector routes to a different model than requested
   (e.g. H3 → Wan for capability reasons), log it + show it in the UI.
4. **Prompt-metadata leakage must be disclosed.** If the prompt text is embedded in the output file
   metadata (H3 does this), tell the user (feature or privacy concern — their call).
5. **Judge bypass is forbidden in quality-gated mode.** If the user requested quality-gated
   generation, the judge MUST run. "Skip judge for speed" is a user opt-in, never a silent default.

## Disclosure obligations (always)
- **What model generated each shot** (model name + quant + settings — in the receipt).
- **What the judge scored** (score + issues + verdict — visible to the user).
- **What was stitched** (shot boundaries + transition type — in the receipt).
- **Cost** (GPU time / API cost — transparent).

## Reproducibility
Every generated shot records: `seed`, `model`, `settings`, `prompt`, `judge_score`, `timestamp`.
Any open-video output can be reproduced from its receipt.

## Community governance
- **Early stage:** BDFL (founder sets vision, fast decisions).
- **Growing:** community council + RFC process for architecture changes.
- **License:** **Apache-2.0** — contributors retain copyright; **no CLA** required for standard PRs.
- **Code of conduct:** see `CODE_OF_CONDUCT.md`.
- **Security:** see `SECURITY.md` (private disclosure for vulns).
