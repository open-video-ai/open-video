# Hugging Face packaging (v0.0.1)

| Target | Type | Purpose |
|---|---|---|
| `open-video-ai/open-video` | model | Software / integration card (**not** H3 weights) |
| `open-video-ai/open-video-prompts` | dataset | Seed prompt recipes |

## Publish (maintainers)

Requires a Hugging Face token with **write** on org `open-video-ai`.

```bash
hf auth login   # org write
./packaging/huggingface/publish.sh
```

Cards under `packaging/huggingface/open-video/` and `…/open-video-prompts/`.  
Upstream H3 weights stay on MiniMax / Comfy-Org — never re-upload full weights via this script.
