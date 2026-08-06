"""open-video prompt crafter — turns intent into model-specific prompts.

Calls the backend's craft_prompt() / prompt_guide() to generate the model-specific
3-field prompt (H3) or style-led prompt (Wan/LTX). The crafter is the quality lever:
better prompts → better outputs. Can be overridden by an LLM for richer prompts.
"""
from __future__ import annotations
from typing import Optional, Callable
from core.backend import ModelBackend


class Crafter:
    """intent → model-specific prompt. Uses backend.craft_prompt by default; LLM-callable."""

    def __init__(self, backend: ModelBackend, llm_fn: Optional[Callable] = None):
        self.backend = backend
        self.llm_fn = llm_fn  # callable(intent_dict, model_prompt_guide) → str (richer prompt)

    def craft(self, intent: dict, mode: str) -> str:
        """Turn a structured intent into a model-specific prompt string.

        intent = {subject, action, camera, environment, soundscape, music, dialogue[], ...}
        mode = t2v | i2v | flf2v | r2v
        """
        if self.llm_fn:
            guide = self.backend.prompt_guide()
            return self.llm_fn(intent, guide, mode)
        return self.backend.craft_prompt(intent, mode)

    def craft_multishot(self, concept: str, n_shots: int, mode_sequence: list = None) -> list:
        """Craft prompts for a multi-shot film from a concept.

        Returns a list of (mode, prompt) tuples, one per shot.
        mode_sequence defaults to [t2v] + [i2v]*(n-1) for FL2VA chaining.
        """
        if mode_sequence is None:
            mode_sequence = ["t2v"] + ["i2v"] * (n_shots - 1)
        prompts = []
        for i, mode in enumerate(mode_sequence):
            intent = {
                "subject": f"shot {i+1} of: {concept}",
                "action": "the scene unfolds with natural, continuous motion",
                "camera": "The camera pushes in with small amplitude at slow speed",
                "soundscape": "ambient environmental sounds appropriate to the scene",
                "music": "a soft minimal ambient score at a slow tempo",
            }
            prompts.append((mode, self.craft(intent, mode)))
        return prompts
