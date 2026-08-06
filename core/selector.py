"""open-video model selector — picks the best backend for a given task.

The selector reads each backend's capabilities.strengths tags and picks the best match
for the user's request. E.g.:
- "audio + dialogue" → H3 (native stereo audio)
- "physics + fluid" → Wan 2.2 (when available)
- "speed + preview" → LTX-2.3 (when available)
"""
from __future__ import annotations
from typing import Optional
from core.backend import ModelBackend


class Selector:
    """Selects the best backend for a task based on capabilities + strengths."""

    # Strength → weight mapping (higher = stronger preference when that axis is needed)
    STRENGTH_WEIGHTS = {
        "native-stereo-audio": 1.0,
        "prompt-adherence": 0.8,
        "arena-top-open": 0.7,
        "physics": 0.9,
        "motion": 0.8,
        "speed": 0.6,
        "low-vram": 0.5,
    }

    # Task keywords → required strengths
    TASK_KEYWORDS = {
        "audio": ["native-stereo-audio"],
        "dialogue": ["native-stereo-audio", "prompt-adherence"],
        "music": ["native-stereo-audio"],
        "voice": ["native-stereo-audio"],
        "physics": ["physics"],
        "fluid": ["physics"],
        "water": ["physics"],
        "cloth": ["physics"],
        "fast": ["speed"],
        "preview": ["speed"],
        "draft": ["speed", "low-vram"],
        "low": ["low-vram"],
    }

    def __init__(self, backends: dict):
        """backends = {id: ModelBackend} dict."""
        self.backends = backends

    def select(self, prompt: str, mode: str = "t2v",
               prefer_speed: bool = False) -> Optional[ModelBackend]:
        """Pick the best backend for the given prompt + mode.

        Scoring: for each backend, sum the weighted strengths that match the prompt's
        task keywords. Filter by mode capability. Return the highest scorer.
        """
        prompt_lower = prompt.lower()
        candidates = []
        for bid, backend in self.backends.items():
            caps = backend.capabilities
            # check mode capability
            if mode == "t2v" and not caps.t2v: continue
            if mode == "i2v" and not caps.i2v: continue
            if mode == "flf2v" and not caps.flf2v: continue
            if mode == "r2v" and not caps.r2v: continue
            # score based on strengths matching prompt keywords
            score = 0.0
            for keyword, required_strengths in self.TASK_KEYWORDS.items():
                if keyword in prompt_lower:
                    for s in required_strengths:
                        if s in (caps.strengths or ()):
                            score += self.STRENGTH_WEIGHTS.get(s, 0.5)
            if prefer_speed:
                if "speed" in (caps.strengths or ()):
                    score += 1.0
            candidates.append((score, bid, backend))

        if not candidates:
            return list(self.backends.values())[0] if self.backends else None
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][2]

    def list_models(self) -> list:
        """Return a summary of all available backends for display."""
        return [
            {"id": b.id, "name": b.display_name,
             "strengths": b.capabilities.strengths,
             "modes": {"t2v": b.capabilities.t2v, "i2v": b.capabilities.i2v,
                       "flf2v": b.capabilities.flf2v, "r2v": b.capabilities.r2v},
             "audio": b.capabilities.native_audio}
            for b in self.backends.values()
        ]
