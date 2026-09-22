"""Vision judge plugin — uses a VLM (vision-language model) to assess video frames.

This is the default judge: extracts N frames from the video, sends each to a vision model
(analyze_image / cx GPT-5.6 / Opus 4.8 / any VLM API), and scores vs the prompt intent.
"""
from open_video.core.judge import QualityJudge, Verdict, Issue


class VisionJudge(QualityJudge):
    """VLM-based judge: extracts frames → sends to vision model → scores + diagnoses."""

    id = "vision"
    display_name = "Vision Model Judge"

    def __init__(self, quality_bar=0.7, n_frames=5, vlm_api=None):
        super().__init__(quality_bar, n_frames)
        self.vlm_api = vlm_api  # callable(image_url, prompt) → dict with score/issues

    def assess(self, video_path, prompt, shot_id=0, frames_dir="output/frames"):
        frames = self.extract_frames(video_path, shot_id, frames_dir)
        if not frames:
            return Verdict(verdict="FAIL", score=0.0,
                           issues=[Issue("extraction", "no frames", "check video")])

        if self.vlm_api is None:
            # SKIPPED: no VLM wired — the shot was not judged. Not a PASS.
            return Verdict(verdict="SKIPPED", score=0.0, frames=frames)

        all_issues = []
        scores = []
        for i, frame in enumerate(frames):
            try:
                result = self.vlm_api(
                    frame,
                    f"Assess this frame (frame {i+1}/{len(frames)}) from a video generated "
                    f"for: '{prompt}'. Score 0-1. List any issues (dropped elements, artifacts, "
                    "bad motion, incoherence). Format: {'score': float, 'issues': "
                    "[{'type': str, 'detail': str, 'fix': str}]}")
            except Exception as e:
                # report the exception type only — messages/URLs may carry credentials
                return Verdict(verdict="FAIL", score=0.0, frames=frames,
                               issues=[Issue("judge_error", f"vlm_api raised {type(e).__name__}",
                                             "check VLM endpoint/config")])
            score = self._parse_score(result.get("score") if isinstance(result, dict) else None)
            if score is None:
                return Verdict(verdict="FAIL", score=0.0, frames=frames,
                               issues=[Issue("judge_error", "vlm_api returned unusable score",
                                             "check VLM response format")])
            scores.append(score)
            issues = result.get("issues") or []
            if not isinstance(issues, list) or any(not isinstance(item, dict) for item in issues):
                return Verdict(verdict="FAIL", score=0.0, frames=frames,
                               issues=[Issue("judge_error", "vlm_api returned malformed issues",
                                             "check VLM response format")])
            for issue in issues:
                all_issues.append(Issue(type=issue.get("type", "artifact"),
                                        detail=issue.get("detail", ""),
                                        fix=issue.get("fix", "try different seed")))
        avg_score = sum(scores) / len(scores) if scores else 0.0
        verdict = "PASS" if avg_score >= self.bar and not all_issues else "REFINE"
        return Verdict(verdict=verdict, score=avg_score, issues=all_issues, frames=frames)


# Register
Judge = VisionJudge
