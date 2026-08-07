"""open-video quality judge (generate → judge → refine).

Frame extraction + vision assessment. A real vision model activates via env
(OPEN_VIDEO_VLM_URL / OPEN_VIDEO_VLM_MODEL / OPEN_VIDEO_VLM_KEY — see
judges/openai_compat.py) or an explicit ``vision_fn``. Without either, the
judge is an honest PASS stub.

Usage:
    judge = QualityJudge.from_env()          # env-wired (or PASS stub)
    judge = QualityJudge(vision_fn=my_api)   # explicit
    v = judge.assess(video_path, prompt, shot_id=1)
    if v.verdict == "REFINE": apply(v.issues)  # fix + regenerate
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

    @classmethod
    def from_env(cls, **kwargs) -> "QualityJudge":
        """Judge wired to the env-configured VLM, or the PASS stub when unset."""
        if kwargs.get("vision_fn") is None:
            from open_video.judges.openai_compat import vision_fn_from_env
            kwargs["vision_fn"] = vision_fn_from_env()
        return cls(**kwargs)

    def extract_frames(self, video_path: str, shot_id: int, frames_dir: str = "output/frames") -> list:
        """Extract N evenly-spaced frames from the video for the judge."""
        frames_dir = Path(frames_dir); frames_dir.mkdir(parents=True, exist_ok=True)
        out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                              "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", video_path],
                             capture_output=True, text=True, timeout=15)
        total = int(out.stdout.strip()) if out.stdout.strip().isdigit() else 120
        idxs = sorted({int(i * (total - 1) / max(self.n - 1, 1)) for i in range(self.n)})
        # one decode pass for all frames (was: one full ffmpeg run per frame)
        select = "+".join(f"eq(n\\,{i})" for i in idxs)
        pattern = frames_dir / f"shot{shot_id}_sel%d.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video_path,
                        "-vf", f"select='{select}'", "-vsync", "passthrough",
                        "-frames:v", str(len(idxs)), str(pattern)], check=False)
        paths = []
        for k, idx in enumerate(idxs, start=1):
            src = frames_dir / f"shot{shot_id}_sel{k}.png"
            dst = frames_dir / f"shot{shot_id}_f{idx}.png"
            if src.exists():
                src.replace(dst)
                paths.append(str(dst))
        return paths

    @staticmethod
    def _flag(value) -> bool:
        """VLMs return booleans as strings — treat 'false'/'none'/'no'/'' as False."""
        if isinstance(value, str):
            return value.strip().lower() not in ("", "false", "none", "no", "0")
        return bool(value)

    def diagnose(self, vision_result: dict, prompt: str) -> list:
        """Parse vision-model output into structured issues + fixes."""
        issues = []
        # dropped elements: check prompt-keywords vs vision description
        for elem in vision_result.get("missing_elements", []):
            issues.append(Issue(type="dropped_element", detail=f"'{elem}' from prompt not visible",
                                fix=f"emphasize '{elem}' earlier + more explicitly in the prompt"))
        if self._flag(vision_result.get("artifacts")):
            issues.append(Issue(type="artifact", detail=str(vision_result["artifacts"]),
                                fix="try different seed or add resolution/stability constraint"))
        if vision_result.get("motion_quality") == "poor":
            issues.append(Issue(type="bad_motion", detail="motion is choppy/unnatural",
                                fix="increase steps to 25 or adjust camera amplitude/speed"))
        if self._flag(vision_result.get("incoherence")):
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
