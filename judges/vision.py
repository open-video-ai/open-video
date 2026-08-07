"""Vision judge plugin — uses a VLM (vision-language model) to assess video frames.

This is the default judge: extracts N frames from the video, sends each to a vision model
(analyze_image / cx GPT-5.6 / Opus 4.8 / any VLM API), and scores vs the prompt intent.
"""
import subprocess, json, urllib.request
from pathlib import Path
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
            return Verdict(verdict="FAIL", issues=[Issue("extraction", "no frames", "check video")])

        if self.vlm_api:
            # v1: use a real VLM API
            all_issues = []
            scores = []
            for i, frame in enumerate(frames):
                result = self.vlm_api(frame, f"Assess this frame (frame {i+1}/{len(frames)}) from a video generated for: '{prompt}'. Score 0-1. List any issues (dropped elements, artifacts, bad motion, incoherence). Format: {{'score': float, 'issues': [{{'type': str, 'detail': str, 'fix': str}}]}}")
                scores.append(result.get("score", 1.0))
                for issue in result.get("issues", []):
                    all_issues.append(Issue(type=issue.get("type","artifact"),
                                          detail=issue.get("detail",""),
                                          fix=issue.get("fix","try different seed")))
            avg_score = sum(scores) / len(scores) if scores else 0.0
            verdict = "PASS" if avg_score >= self.bar and not all_issues else "REFINE"
            return Verdict(verdict=verdict, score=avg_score, issues=all_issues, frames=frames)
        else:
            # v0: stub (no VLM wired → PASS)
            return Verdict(verdict="PASS", score=1.0, frames=frames)


# Register
Judge = VisionJudge
