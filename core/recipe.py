"""Recipe-in-render: embed + read generation metadata in output videos.

Like ComfyUI embeds the workflow in PNG
metadata, OpenVideo embeds the full generation recipe (prompt + model + settings + seed +
LoRA + quality verdict) in the output MP4 metadata. This makes every OpenVideo video:
- SELF-DOCUMENTING (the recipe is in the file — no external receipt needed)
- REMIXABLE (`open-video remix film.mp4` → recreate or tweak the generation)
- A VIRAL ENTRY POINT (drag any OpenVideo video back → instant remix → every shared video
  is a potential OpenVideo adoption)

No other agentic video platform has this. This is OpenVideo's "ComfyUI PNG drag-drop" moment.
"""
import json, subprocess
from pathlib import Path
from typing import Optional


# Metadata key prefix (avoids collisions with standard ffmpeg keys)
PREFIX = "openvideo_"
MAX_RECIPE_METADATA_BYTES = 32000


def embed_recipe(video_path: str, recipe: dict, output_path: Optional[str] = None) -> str:
    """Embed the generation recipe into an MP4's metadata via ffmpeg.

    recipe = {prompt, model, width, height, duration_s, seed, steps, sampler,
              scheduler, lora, lora_weight, quality_verdict, timestamp, ...}

    Uses ffmpeg -metadata flags (stored in the MP4 container's moov/udta atom).
    """
    output = output_path or video_path
    recipe_json = json.dumps(recipe)
    embed_json = len(recipe_json.encode("utf-8")) <= MAX_RECIPE_METADATA_BYTES
    if not embed_json:
        print(
            f"[open-video] warning: recipe exceeds {MAX_RECIPE_METADATA_BYTES} "
            f"bytes; skipping {PREFIX}recipe_json tag (per-key tags still embedded)",
            flush=True,
        )

    cmd = ["ffmpeg", "-y", "-v", "error", "-i", video_path]
    for key, val in recipe.items():
        if val is not None:
            cmd.extend(["-metadata", f"{PREFIX}{key}={val}"])
    if embed_json:
        cmd.extend(["-metadata", f"{PREFIX}recipe_json={recipe_json}"])
    cmd.extend(["-c", "copy", output])  # stream-copy (no re-encode)
    r = subprocess.run(cmd, capture_output=True, timeout=60)
    if r.returncode != 0:
        # fallback: re-encode with metadata
        cmd_re = ["ffmpeg", "-y", "-v", "error", "-i", video_path]
        for key, val in recipe.items():
            if val is not None:
                cmd_re.extend(["-metadata", f"{PREFIX}{key}={val}"])
        if embed_json:
            cmd_re.extend(["-metadata", f"{PREFIX}recipe_json={recipe_json}"])
        cmd_re.extend(["-c:v", "libx264", "-crf", "18", "-c:a", "aac", output])
        r = subprocess.run(cmd_re, capture_output=True, timeout=300)
        if r.returncode != 0:
            raise RuntimeError(
                f"ffmpeg metadata embedding failed: {r.stderr.decode(errors='replace')}"
            )

    expected = json.loads(recipe_json)  # JSON round-trip normalizes types
    written = read_recipe(output)
    if embed_json:
        ok = written == expected
    else:
        # full JSON blob omitted; verify the per-key tags that were written
        expected_tags = {k: str(v) for k, v in recipe.items() if v is not None}
        ok = written is not None and all(
            written.get(k) == v for k, v in expected_tags.items()
        )
    if not ok:
        raise RuntimeError("embedded recipe metadata verification failed")
    return output


def read_recipe(video_path: str) -> Optional[dict]:
    """Read the embedded generation recipe from an MP4's metadata.

    Returns the recipe dict, or None if no OpenVideo metadata found.
    """
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-of", "json", video_path],
        capture_output=True, text=True, timeout=15)
    if r.returncode != 0:
        return None
    try:
        fmt = json.loads(r.stdout).get("format", {})
        tags = fmt.get("tags", {})
        # try the JSON blob first (most complete)
        recipe_json = tags.get(f"{PREFIX}recipe_json") or tags.get(f"{PREFIX.upper()}recipe_json".upper())
        if recipe_json:
            return json.loads(recipe_json)
        # fallback: reconstruct from individual keys
        recipe = {}
        for key, val in tags.items():
            if key.lower().startswith(PREFIX) and key.lower() != f"{PREFIX}recipe_json":
                clean_key = key.lower()[len(PREFIX):]
                recipe[clean_key] = val
        return recipe if recipe else None
    except (json.JSONDecodeError, KeyError):
        return None


def recipe_to_receipt(recipe: dict) -> str:
    """Format a recipe dict as a human-readable receipt string."""
    lines = ["OpenVideo Generation Receipt", "=" * 40]
    for key in ["prompt", "model", "width", "height", "duration_s", "seed",
                "steps", "sampler", "scheduler", "lora", "lora_weight",
                "quality_verdict", "timestamp"]:
        val = recipe.get(key, "—")
        if key == "prompt" and val and len(str(val)) > 80:
            val = str(val)[:77] + "..."
        lines.append(f"  {key}: {val}")
    return "\n".join(lines)
