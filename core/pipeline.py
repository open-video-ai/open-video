"""open-video long-film orchestrator — the flagship pipeline.

concept → plan shots → craft+validate+generate+judge each (FL2VA chain) → stitch → deliver.
Produces multi-minute films from a ≤15s-per-shot model (H3 baseline). This is what Seedance does
model-natively (180s); open-video does via orchestration + the judge loop.

Architecture: this orchestrator DELEGATES to the other core modules — it owns only the
shot-by-shot loop and the FL2VA chain. Quality assessment goes through core.judge.QualityJudge,
concat / last-frame extraction through core.stitcher.Stitcher, and the generation recipe is
embedded in the output film via core.recipe.embed_recipe. No judge/stitch logic is duplicated here.
"""
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from core.backend import ShotRequest
from core.judge import QualityJudge
from core.stitcher import Stitcher
from core.recipe import embed_recipe


@dataclass
class Shot:
    scene_id: int
    prompt: str
    mode: str = "t2v"           # t2v | i2v | flf2v
    duration_s: float = 10.0
    seed: int = 0
    first_frame: Optional[str] = None
    last_frame: Optional[str] = None
    video_path: Optional[str] = None
    verdict: str = ""           # PASS | REFINE | FAIL
    receipt: dict = field(default_factory=dict)


class LongFilmPipeline:
    """Orchestrates plan → per-shot generate+judge → FL2VA chain → stitch → embed recipe → film.

    Delegates: QualityJudge (assessment), Stitcher (concat + last-frame), embed_recipe (metadata).
    Owns: the per-shot loop, the FL2VA chain, and verdict/receipt bookkeeping on Shot.
    """

    def __init__(self, backend, engine, output_dir: str = "output", vision_fn: Optional[callable] = None):
        self.backend = backend
        self.engine = engine
        self.out = Path(output_dir)
        self.frames = self.out / "frames"
        self.out.mkdir(parents=True, exist_ok=True)
        self.frames.mkdir(parents=True, exist_ok=True)
        # core modules — single source of truth for judge / stitch / recipe logic
        self._judge = QualityJudge(vision_fn=vision_fn)
        self._stitcher = Stitcher(output_dir=str(self.out))

    # --- the judge (delegates to core.judge.QualityJudge) ---
    def judge(self, shot: Shot) -> bool:
        """Assess shot vs prompt intent + quality bar via QualityJudge; write verdict + frames
        back into the shot. Returns False only on FAIL (REFINE/PASS continue the chain)."""
        verdict = self._judge.assess(shot.video_path, shot.prompt,
                                     shot_id=shot.scene_id, frames_dir=str(self.frames))
        shot.verdict = verdict.verdict
        shot.receipt["judge_frames"] = verdict.frames
        shot.receipt["judge_score"] = verdict.score
        if verdict.issues:
            shot.receipt["judge_issues"] = [
                {"type": i.type, "detail": i.detail, "fix": i.fix} for i in verdict.issues
            ]
        return verdict.verdict != "FAIL"

    # --- single-shot generation via backend ---
    def _run_shot(self, shot: Shot) -> bool:
        # use backend's resolution_for if available, else default 1344x768
        try:
            w, h = self.backend.resolution_for("16:9") if self.backend else (1344, 768)
        except Exception:
            w, h = 1344, 768
        req = ShotRequest(prompt=shot.prompt, mode=shot.mode, width=w, height=h,
                          duration_s=shot.duration_s, seed=shot.seed,
                          first_frame=shot.first_frame, last_frame=shot.last_frame,
                          lora=shot.receipt.get("lora"), lora_weight=shot.receipt.get("lora_weight", 0.8),
                          trigger_word=shot.receipt.get("trigger_word"))
        result = self.backend.generate(req, engine=self.engine)  # FIX: pass engine through
        if not result.ok:
            shot.verdict = "FAIL"
            shot.receipt["error"] = result.error
            return False
        shot.video_path = result.video_path
        shot.receipt.update(result.receipt)
        return self.judge(shot)

    # --- recipe assembly for embed_recipe (self-documenting + remixable output) ---
    def _build_recipe(self, plan: list, film_path: str) -> dict:
        valid = [s for s in plan if s.video_path]
        first = valid[0] if valid else None
        engine_id = getattr(self.engine, "id", None) if self.engine else None
        backend_id = getattr(self.backend, "id", None) if self.backend else None
        verdicts = [s.verdict for s in valid if s.verdict]
        worst = ("FAIL" if "FAIL" in verdicts
                 else "REFINE" if "REFINE" in verdicts
                 else "PASS" if verdicts else "")
        first_receipt = (first.receipt if first else {}) or {}
        return {
            "prompt": " | ".join(s.prompt for s in valid) if valid else "",
            "model": str(engine_id or backend_id or "unknown"),
            "width": first_receipt.get("width"),
            "height": first_receipt.get("height"),
            "duration_s": sum(s.duration_s for s in valid),
            "seed": first.seed if first else 0,
            "seeds": ",".join(str(s.seed) for s in valid),
            "shots": len(valid),
            "lora": first_receipt.get("lora"),
            "lora_weight": first_receipt.get("lora_weight"),
            "quality_verdict": worst,
            "film_path": film_path,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

    # --- the full long-film pipeline ---
    def make_film(self, plan: list, out_path: str = "output/film.mp4"):
        """plan = list[Shot]. Orchestrates: generate (FL2VA chain) → judge → stitch → embed recipe → film."""
        print(f"[open-video] long-film pipeline: {len(plan)} shots → {out_path}", flush=True)
        prev_last = None
        for shot in plan:
            # FL2VA chain: previous shot's last frame → this shot's first frame
            if prev_last:
                shot.first_frame = prev_last
                if shot.mode == "t2v":
                    shot.mode = "i2v"  # upgrade to I2V for continuity handoff
            ok = self._run_shot(shot)
            if not ok:
                print(f"[open-video] shot {shot.scene_id} FAILED: {shot.receipt.get('error','?')}", flush=True)
                break
            print(f"[open-video] shot {shot.scene_id} ✓ {shot.video_path} [{shot.verdict}]", flush=True)
            lf = self.out / f"_lf_{shot.scene_id}.png"
            prev_last = self._stitcher.extract_last_frame(shot.video_path, str(lf))

        # stitch via core.stitcher (codec-uniform stream-copy + re-encode fallback)
        valid_paths = [s.video_path for s in plan if s.video_path]
        film = self._stitcher.concat(valid_paths, out_path)

        # embed the generation recipe in the output film (self-documenting + remixable)
        if film and Path(film).exists():
            recipe = self._build_recipe(plan, film)
            try:
                embed_recipe(film, recipe)
            except Exception as e:
                print(f"[open-video] recipe embed skipped: {e}", flush=True)

        print(f"[open-video] FILM: {film}", flush=True)
        return film, plan
