# Reddit Launch Posts — OpenVideo

> Tailored posts for each subreddit (different angles for different communities). All include the demo film + GitHub link + "100% open-source" hook.

## r/StableDiffusion (978K subs — the biggest open AI community)

**Title:** [OC] I built an open-source video generation platform that matches Runway quality — 100% free, on your GPU

**Body:**
> OpenVideo is an open-source autonomous video director for video generation. It uses MiniMax H3 (the #1 open video model, now at Arena parity with closed models like Seedance and Veo) + a quality loop (generate → judge → refine → best-of-N) that NO open video tool has.
>
> **Demo:** [18-second lighthouse film, generated 100% open-source](https://open-video.ai) — 2 shots, FL2VA chain, 1344×768, native stereo audio, on a single RTX 5090.
>
> Think of it as: **Ollama for video** — one command to run video models locally, plus a quality judge that checks its own work.
>
> **What it does:**
> - Text-to-video + image-to-video + multi-shot stitching (beyond the 15s model ceiling)
> - Quality loop: generates → vision-judges → refines until good (the VISTA/VideoWeaver pattern, productized)
> - Community LoRAs (the Stable Diffusion LoRA explosion, for video)
> - Plugin system (add any model/judge/engine)
>
> **Built on:** ComfyUI (engine) + H3 (model) + VideoScore (judge) + woodfantasy (methodology). We integrate, not reinvent.
>
> Apache 2.0. ★ GitHub: https://github.com/open-video-ai/open-video
> Discord: [link]
>
> Looking for: model backend contributors (Wan 2.2, LTX), prompt recipe contributors, LoRA trainers. Star + try + contribute!

---

## r/LocalLLaMA (787K subs — local-first enthusiasts)

**Title:** OpenVideo: run video models locally — "Ollama for video" — with a quality judge loop

**Body:**
> Just like Ollama made running LLMs locally dead-simple, OpenVideo makes running video models locally dead-simple — plus a quality loop that judges and refines its own output.
>
> **One command:** `curl -fsSL open-video.ai/install | bash` → downloads H3 weights (54GB) + sets up ComfyUI + runs your first video generation.
>
> H3 = 33B video model with native stereo audio. Runs on RTX 5090 32GB (int8_convrot quant). Arena Elo 1238 — **statistically tied with closed #1** (Gemini Omni Flash 1244).
>
> **The quality loop** is the differentiator: generate → extract frames → vision-judge vs prompt intent → if below bar, diagnose (dropped element? bad motion?) → fix prompt → regenerate. Proven by Google VISTA (+46.3% win rate). No open video tool has this.
>
> Apache 2.0. Works on your GPU. No API key. No subscription. No censorship.
>
> ★ GitHub | Discord | Website: open-video.ai

---

## r/aivideo (365K subs — model-agnostic AI video)

**Title:** Open-source video gen finally matches closed quality — here's an 18-second film made 100% locally

**Body:**
> [Demo film embedded]
>
> This was generated 100% open-source. No API. No subscription. Single RTX 5090. MiniMax H3 + OpenVideo (the quality loop director layer).
>
> H3's Arena Elo (1238) is within noise of Gemini Omni Flash (1244) and Seedance (1197) — **open has caught up to closed**. OpenVideo's quality loop (judge→refine→best-of-N) is what delivers that parity in practice.
>
> Open-source. Apache 2.0. Free. Local-first. Community-driven.
>
> GitHub ★ | open-video.ai | Discord

---

## r/comfyui (178K subs — ComfyUI ecosystem)

**Title:** OpenVideo: the autonomous director layer on top of ComfyUI — quality loop + multi-shot stitching + LoRAs

**Body:**
> We love ComfyUI. It's the best video engine. OpenVideo is the **agent brain** on top of it — the autonomous director that ComfyUI lacks.
>
> **What OpenVideo adds to ComfyUI:**
> - **Quality loop**: generate → vision-judge → refine → best-of-N (no more guessing if your output is good)
> - **Multi-shot stitching**: plan a 5-min film → generate ≤15s shots with FL2VA chaining → stitch into one film
> - **Community LoRAs**: the SD LoRA pattern for video (anyone can train + share)
> - **Plugin system**: add models/judges/engines as plugins
>
> OpenVideo drives ComfyUI via its HTTP API — no replacement, pure augmentation.
>
> Built on ComfyUI + H3 + VideoScore + woodfantasy methodology.
>
> Apache 2.0. GitHub ★ | open-video.ai

---

## r/SideProject or r/SideProjectDevs (builders community)

**Title:** I built the open-source Runway — video generation that's 100% free, local-first, with a quality AI judge

**Body:**
> Spent the last few days building OpenVideo — an open-source autonomous video generation platform. Think "Ollama for video": one command to run video models locally, plus an AI quality judge that checks and refines its own output.
>
> Key insight: open video models (MiniMax H3) have reached statistical parity with closed models (Seedance/Veo) on Arena benchmarks. The gap isn't the model — it's the agent layer. OpenVideo IS that layer.
>
> Tech: ComfyUI (engine) + H3 (model) + quality loop (judge→refine→best-of-N) + multi-shot stitching + LoRA marketplace.
>
> Apache 2.0. Built in Python. 100+ files. Working demo film (18s, GOOD verdict from vision judge).
>
> Looking for contributors + feedback. ★ GitHub | open-video.ai
