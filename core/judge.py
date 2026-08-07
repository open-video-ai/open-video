"""open-video quality judge scaffold (generate → judge → refine design).

v0.0.1: frame extraction + PASS stub unless a real vision_fn is provided.
Not a shipped multi-minute film product — wire a vision model for real scores.

Usage:
    judge = QualityJudge(vision_fn=my_vision_api)
    v = judge.assess(video_path, prompt, shot_id=1)
    if v.verdict == "REFINE": apply(v.issues)  # fix + regenerate

v0: frame extraction + PASS stub (ready for vision wiring).
v1: vision model → score + diagnose (planned).
"""
import subprocess, json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Callable


@dataclass
class Issue:
    type: str       # "dropped_element" | "bad_motion" | "artifact" | "incoherence" | "low_quality"
    detail: str
    fix: str        # suggested prompt/mode/setting change


@dataclass
class Verdict:
    verdict: str = "PASS"          # PASS | REFINE | FAIL
    score: float = 1.0             # 0.0–1.0 quality score
    issues: list = field(default_factory=list)   # list[Issue]
    frames: list = field(default_factory=list)   # assessed frame paths
    raw: dict = field(default_factory=dict)      # raw vision-model output


class QualityJudge:
    """Extracts frames → vision-assesses vs prompt intent + quality bar → verdict + diagnosis."""

    def __init__(self, quality_bar: float = 0.7, n_frames: int = 5,
                 vision_fn: Optional[Callable] = None):
        self.bar = quality_bar
        self.n = n_frames
        self.vision_fn = vision_fn   # callable(frames: list[str], prompt: str) → dict

    def extract_frames(self, video_path: str, shot_id: int, frames_dir: str = "output/frames") -> list:
        """Extract N evenly-spaced frames from the video for the judge."""
        frames_dir = Path(frames_dir); frames_dir.mkdir(parents=True, exist_ok=True)
        out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                              "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", video_path],
                             capture_output=True, text=True, timeout=15)
        total = int(out.stdout.strip()) if out.stdout.strip().isdigit() else 120
        idxs = [int(i * (total - 1) / max(self.n - 1, 1)) for i in range(self.n)]
        paths = []
        for idx in idxs:
            p = frames_dir / f"shot{shot_id}_f{idx}.png"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video_path,
                            "-vf", f"select=eq(n\\,{idx})", "-frames:v", "1", str(p)], check=False)
            if p.exists():
                paths.append(str(p))
        return paths

    def diagnose(self, vision_result: dict, prompt: str) -> list:
        """Parse vision-model output into structured issues + fixes."""
        issues = []
        # dropped elements: check prompt-keywords vs vision description
        for elem in vision_result.get("missing_elements", []):
            issues.append(Issue(type="dropped_element", detail=f"'{elem}' from prompt not visible",
                                fix=f"emphasize '{elem}' earlier + more explicitly in the prompt"))
        if vision_result.get("artifacts"):
            issues.append(Issue(type="artifact", detail=vision_result["artifacts"],
                                fix="try different seed or add resolution/stability constraint"))
        if vision_result.get("motion_quality") == "poor":
            issues.append(Issue(type="bad_motion", detail="motion is choppy/unnatural",
                                fix="increase steps to 25 or adjust camera amplitude/speed"))
        if vision_result.get("incoherence"):
            issues.append(Issue(type="incoherence", detail="frames don't flow coherently",
                                fix="simplify the shot to single-action; reduce cut count"))
        return issues

    def assess(self, video_path: str, prompt: str, shot_id: int = 0,
               frames_dir: str = "output/frames") -> Verdict:
        """Full assessment: extract frames → vision-judge → verdict + diagnosis."""
        frames = self.extract_frames(video_path, shot_id, frames_dir)
        if not frames:
            return Verdict(verdict="FAIL", issues=[Issue("extraction", "no frames extracted", "check video")])

        if self.vision_fn:
            raw = self.vision_fn(frames, prompt)
            score = raw.get("score", 1.0)
            issues = self.diagnose(raw, prompt)
            verdict = "PASS" if score >= self.bar and not issues else "REFINE"
            return Verdict(verdict=verdict, score=score, issues=issues, frames=frames, raw=raw)
        else:
            # v0: no vision model wired → PASS (the hook is ready; wire vision_fn for v1)
            return Verdict(verdict="PASS", score=1.0, frames=frames)
