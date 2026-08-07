# Agents — OpenVideo product repo

You are inside the **product** git repo: [`open-video-ai/open-video`](https://github.com/open-video-ai/open-video).

## Read first

| Doc | Why |
|---|---|
| [`README.md`](README.md) | What v0.0.1 ships vs design-only |
| [`docs/QUICKSTART.md`](docs/QUICKSTART.md) | Install / pull / run |
| [`skill/h3-video/SKILL.md`](skill/h3-video/SKILL.md) | Agent generate path |
| [`docs/LAB.md`](docs/LAB.md) | ComfyUI + weights outside git |

## Rules (public-safe)

1. **Brand:** OpenVideo. Do not rename the product to “H3 app” or “ComfyUI wrapper.”
2. **Honesty:** Do not claim live vision judge, free cloud GPU, desktop installers, or marketplace as shipped in v0.0.1.
3. **Secrets:** Never commit `.env`, tokens, private keys, or host credential paths.
4. **Weights:** Never commit `*.safetensors` / ComfyUI / `lab/`.
5. **Strategy:** No GTM, star-count north stars, or competitive war docs in this repo.
6. **Visibility:** Do **not** flip the repo public unless the owner explicitly says go.

## Env (before GPU work)

```bash
export OPEN_VIDEO_ROOT="$(pwd)"
export OPEN_VIDEO_LAB="${OPEN_VIDEO_LAB:-$OPEN_VIDEO_ROOT/../lab}"
export OPEN_VIDEO_MODELS="${OPEN_VIDEO_MODELS:-$OPEN_VIDEO_LAB/h3_models}"
export OPEN_VIDEO_COMFYUI="${OPEN_VIDEO_COMFYUI:-http://127.0.0.1:8188}"
```
