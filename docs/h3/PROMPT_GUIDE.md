# Prompt Guide — MiniMax H3 (official `VIDEO_PROMPT_WRITING_GUIDE_base_en.md`, condensed)

H3 rewards **highly structured, timeline-based** prompts. Every prompt = optional instruction
line + **three required core fields**, in this exact order.

## Structure

```
[<instruction line>     # only for I2V/FL2VA/L2VA — first line, then blank line]

integrated_multimodal_description: [Shot 1] <style>, <composition/subjects/scene>. <camera motion + action>. [Shot 2] At 00:0X.XXX, the camera cuts to <next beat>.
overall_soundscape: <1–4 sentences: ambient / physical / non-verbal human sound>
non_diegetic_music: <1–3 sentences: instrumentation, tempo, rhythm, dynamics — no mood words>
```

- **T2VA**: no instruction line; begin directly with the three fields.
- **I2VA**: `"For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced."`
- **FL2VA**: `"How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark …; Picture 2 aligns with the final timestamp."`
- **L2VA**: same, but Picture 1 references the **last** frame at the final timestamp.

## Rules (verbatim gist)

- **Every detail must correspond to something visible or audible.** No abstract mood/emotion words.
- State overall **style first** in Shot 1 — e.g. Cinematic / live-action / 2D-animated / 3D CG / claymation / watercolor / vintage film.
- Don't timestamp Shot 1. Later shots begin with **strictly increasing cut time** within the duration.
- Keep character identity, clothing, colors, objects, spatial relations **consistent** across shots.
- **Camera motion** = natural prose combining *type + amplitude + speed*:
  `"The camera pushes in with small amplitude at slow speed toward the folded letter."`
  Types: Push In / Pull Out / Pan / Truck / Tilt / Arc / Tracking / Static / POV / Roll. Omit amplitude/speed when medium/normal.
- **Dialogue**: stable speaker IDs `(S1)`, `(S2)`; first appearance gives identity (age/gender/on-screen/pitch/timbre/rate/accent). Verbatim content inside `<d>[language] actual words</d>` — preserve every word/punctuation, no translation. Voiceover: use `"says in an off-screen voiceover"` then note the on-screen character's lips stay closed.
- **On-screen text**: English double quotes, verbatim, untranslated.
- Cuts: `"the camera cuts to"` / `"the shot transitions to"`. Use dissolves/fades/wipes **only if explicitly requested**. A cut should add new info (subject/space/state/viewpoint/time); for mere distance/angle change, prefer camera motion over a cut.
- FL2VA favors a **single shot** for continuous interpolation; don't repeat two static image descriptions — describe the **motion path** connecting them.

## Field-specific

- **overall_soundscape** (1–4 sent): wind, rain, traffic, footsteps, fabric, impacts, breathing, laughter. Dialogue/singing/diegetic music belong in the multimodal field — don't duplicate here. `N/A` only for explicit total silence.
- **non_diegetic_music** (1–3 sent): instrumentation, speed, rhythm, dynamic changes. **No abstract mood words**, don't explain emotional function. Diegetic music (audible to characters) goes in the multimodal field instead.

## Examples

**T2VA (multi-shot, dialogue + music):**
```
integrated_multimodal_description: [Shot 1] Live-action, cinematic, a medium-wide shot frames a baker opening the shutters of a small street bakery before sunrise. The camera pushes in with small amplitude at slow speed as the middle-aged baker with a calm, slightly raspy voice (S1) places a fresh loaf on the wooden counter and says: <d>[English] First batch of the morning.</d> [Shot 2] At 00:05.000, the camera cuts to a close-up of steam rising from the sliced bread while the baker's final words carry over from the previous shot.

overall_soundscape: Wooden shutters scrape open over a quiet street as trays clink softly inside the bakery. The doorbell rings once, followed by light footsteps and the crisp sound of bread being sliced.

non_diegetic_music: A soft acoustic-guitar pattern at a moderate tempo, joined by sparse upright-bass notes and a gentle fade at the end.
```

**FL2VA (8 s, single shot, no music):**
```
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 8.00-second mark of the target video.

integrated_multimodal_description: [Shot 1] Live-action, cinematic, a rain-soaked cyclist begins in the position and framing established by Picture 1, holding a closed black umbrella beside a silver bicycle. The camera pulls out with small amplitude at slow speed as she releases the bicycle handle, raises the umbrella above her shoulder, and presses the runner upward until the canopy opens. Water rolls from the expanding fabric while she steps beneath it, rotates the handle into the final angle, and settles into the pose, spacing, and composition established by Picture 2 at the end of the shot.

overall_soundscape: Rain falls steadily on the pavement, followed by the metallic click of the umbrella runner and the soft snap of the canopy opening. Water drips from the bicycle frame as distant traffic passes.

non_diegetic_music: N/A
```

## R2V extras (see `VIDEO_PROMPT_WRITING_GUIDE_ref_en.md`)
- Tag refs in connection order: `<Picture 1>`, `<Video 1>`, `<Audio 1>`.
- Explicitly assign each ref to a role (identity / style / motion / camera / voice) — works much better than implicit.
- For voice refs, the audio "cannot be sent alone; must travel with an image or video."
