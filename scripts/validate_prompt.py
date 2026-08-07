#!/usr/bin/env python3
"""Mode-aware MiniMax H3 prompt validator — the agent's pre-delivery gate.
Inspired by woodfantasy/Seedance validate_prompt.py: hard constraint checks (not soft retry).
Checks: 3 required fields, duration 4-15s, mode-specific image/ref counts + instruction line,
timeline cut times strictly increasing & within duration, well-formed <d>[lang]…</d> dialogue.
Exit 0 if clean (warnings allowed); exit 1 on issues (or with --strict, on warnings too)."""
import argparse, re, sys

FIELDS = ["integrated_multimodal_description", "overall_soundscape", "non_diegetic_music"]

def detect_mode(prompt, n_images=0, n_videos=0, n_audios=0):
    p = prompt.lstrip()
    if p.startswith("How the reference pictures align"):
        return "fl2v" if (n_images >= 2 or "Picture 2" in prompt) else "l2va"
    if p.startswith("For the target video"):
        return "i2v"
    if n_videos or n_audios:
        return "r2v"
    if n_images >= 2:
        return "fl2v"
    if n_images == 1:
        return "i2v"
    return "t2v"

def validate(prompt, mode=None, duration=5.0, n_images=0, n_videos=0, n_audios=0):
    issues, warns = [], []
    if mode is None:
        mode = detect_mode(prompt, n_images, n_videos, n_audios)
    for f in FIELDS:
        if f"{f}:" not in prompt:
            issues.append(f"missing required field: {f}")
    if not (4 <= duration <= 15):
        issues.append(f"duration {duration}s outside 4-15s")
    if mode in ("i2v", "fl2v", "l2va") and not re.search(r"(For the target video|How the reference pictures align)", prompt):
        warns.append(f"{mode}: image mode but no instruction (Picture alignment) line")
    if mode == "fl2v" and n_images < 2:
        warns.append("fl2v: fewer than 2 images (first-last-frame needs 2)")
    if mode in ("i2v", "l2va") and n_images < 1:
        warns.append(f"{mode}: no input image")
    if mode == "r2v":
        if n_images > 9: issues.append(f"R2V images {n_images} > 9")
        if n_videos > 3: issues.append(f"R2V videos {n_videos} > 3")
        if n_audios > 3: issues.append(f"R2V audios {n_audios} > 3")
        if n_images + n_videos + n_audios > 12: issues.append("R2V total files > 12")
        if n_audios and not (n_images or n_videos): issues.append("R2V: audio cannot be the sole input")
    cuts = re.findall(r"At (\d{2}:\d{2}\.\d{3})", prompt)
    prev = 0.0
    for c in cuts:
        t = int(c[0:2]) * 60 + float(c[3:])
        if t <= prev: warns.append(f"cut time {c} not strictly increasing")
        if t > duration + 0.01: warns.append(f"cut time {c} beyond duration {duration}s")
        prev = t
    if re.search(r"<d>(?!\s*\[)", prompt):
        warns.append("dialogue <d> tag missing [language] prefix")
    if "<d>" in prompt and "</d>" not in prompt:
        issues.append("dialogue <d> tag not closed")
    return mode, issues, warns

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt-file"); ap.add_argument("--mode")
    ap.add_argument("--duration", type=float, default=5.0)
    ap.add_argument("--images", type=int, default=0)
    ap.add_argument("--videos", type=int, default=0)
    ap.add_argument("--audios", type=int, default=0)
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    prompt = open(a.prompt_file).read() if a.prompt_file else sys.stdin.read()
    mode, issues, warns = validate(prompt, a.mode, a.duration, a.images, a.videos, a.audios)
    print(f"mode={mode}  issues={len(issues)}  warnings={len(warns)}")
    for x in issues: print("  ISSUE :", x)
    for x in warns: print("  warn  :", x)
    sys.exit(1 if (issues or (a.strict and warns)) else 0)
