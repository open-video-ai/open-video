# Hugging Face packaging (v0.0.1)

| Target | Type | Purpose |
|---|---|---|
| `open-video-ai/open-video` | model | Software / integration card (not H3 weights) |
| `open-video-ai/open-video-prompts` | dataset | Seed prompt recipes |

## Publish to org

Requires a token with **write** on org `open-video-ai` (HF → org settings → members / fine-grained token).

```bash
# after: hf auth login  (org write)
./packaging/huggingface/publish.sh
```

## Bootstrap (2026-08-07)

Org create returned **403** for the lab token (membership without write). Content was published under:

- https://huggingface.co/fei567/open-video  
- https://huggingface.co/datasets/fei567/open-video-prompts  

**Owner action:** HF UI → Settings → Transfer repository → `open-video-ai`, or re-run `publish.sh` with an org-write token.
