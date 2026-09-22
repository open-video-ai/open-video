# OpenVideo v0.1.0 — Release Notes

Reliability release on the v0.0.1 thesis: **Ollama for MiniMax H3 + agent skill
harness**. Same CLI, same skill, same backend plugin model — the shipped path
now verifies what it downloads, fails honestly, and cleans up after itself.

## Get it

```bash
git clone --depth 1 --branch v0.1.0 https://github.com/open-video-ai/open-video
cd open-video && bash scripts/install.sh
```

The `curl https://open-video.ai/install` site installer still serves the
previous release until an authorized site cutover — the tag clone above is the
primary v0.1.0 path.

## What changed

- **Recipe-in-render round-trip** — `embed_recipe`/`read_recipe` round-trip
  atomically; stale OpenVideo metadata tags are cleared on re-embed.
- **Integrity-verified weights** — `open-video pull h3` verifies a packaged
  manifest (sizes + checksums), not just file presence.
- **Engine adapter hardening** — correct URL encoding; ComfyUI errors propagate
  as errors instead of silent timeouts.
- **I2V / FLF2V unique staging** — first/last frames are staged under unique
  names via `OPEN_VIDEO_COMFYUI_INPUT`, which must point at a directory that
  belongs to the target ComfyUI server.
- **Honest judge** — with no VLM configured (`OPEN_VIDEO_VLM_URL` +
  `OPEN_VIDEO_VLM_MODEL`, or an explicit `vision_fn`), shot verdicts are
  `SKIPPED` (score 0) instead of a silent PASS. Real VLM callbacks remain
  strictly opt-in.
- **Bounded refine loop** — finite validation/retries
  (`OPEN_VIDEO_JUDGE_RETRIES`); the best take's seed and full take history are
  recorded in the receipt; aborting leaves a partial-film receipt.

## Truth in advertising

- No `open-video inspect` / `remix` / `--lora` CLI flags exist. Recipe read-back:
  `python -c "from open_video.core.recipe import read_recipe; print(read_recipe('out.mp4'))"`.
- Default weights are **INT8 only**. W4 / NF4 are manual, experimental tiers —
  `recommend-quant` may suggest them but nothing auto-installs them.
- The long-film director (`skill/open-video`) stays **experimental**; generation
  requires an NVIDIA GPU runtime.
- No new GPU/Windows/visual acceptance claims in this release.

## Verification status

| Check | Status |
|---|---|
| Unit/integration tests (`pytest`) | pending — run at release cut |
| `python -m open_video list-models --json` | verified on the release branch |
| `python -m open_video "<prompt>" --dry-run --json` | verified on the release branch |
| Real multi-shot demo with VLM judge + receipts | **pending** — next milestone; not claimed as passing |

## Upgrade notes

- From source: `git fetch --tags && git checkout v0.1.0`, then `pip install -e .`.
- I2V/FL2V users: set `OPEN_VIDEO_COMFYUI_INPUT` to the ComfyUI server's own
  `input/` directory before running.
- If you relied on the judge auto-PASSing with no VLM: verdicts now read
  `SKIPPED`. Set `OPEN_VIDEO_VLM_*` to get real scoring.
