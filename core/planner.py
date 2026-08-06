"""open-video coherence-bible planner — concept → shot plan for long films.

The planner is the brain that makes multi-minute films possible. It takes a concept, builds a
coherence bible (5 state groups), breaks it into acts→scenes→shots (each ≤ model's max_duration),
and outputs a plan with per-shot prompts + continuity anchors + state-vector handoffs.

Ported from the woodfantasy methodology (MIT-0) — reimplemented for open models.

v0: template structure (the planner defines the 5-state-group + acts/scenes framework; an LLM
fills the content). v1: LLM-driven planner that generates the full plan from a concept.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from core.pipeline import Shot


@dataclass
class StateGroup:
    """One of the 5 coherence state groups (woodfantasy pattern). Carried across shots."""
    identity: dict = field(default_factory=dict)      # face/hair/age/build/voice
    wardrobe_props: dict = field(default_factory=dict)  # clothing/items/ownership/state
    geography: dict = field(default_factory=dict)     # entries/exits/screen-direction/light/weather
    story_knowledge: dict = field(default_factory=dict)  # who knows what + when it changes
    audio_state: dict = field(default_factory=dict)   # music-theme/ambient/dialogue-language/silence


@dataclass
class Transition:
    """Compact state vector passed between shots (at each cut)."""
    position: str = ""        # where characters are
    momentum: str = ""        # what they're doing / direction of motion
    props: str = ""           # what's in hand / on screen
    weather: str = ""         # ambient conditions
    camera: str = ""          # camera state (angle/motion/lens)
    audio: str = ""           # audio state at the cut point


@dataclass
class FilmPlan:
    concept: str
    bible: StateGroup
    shots: list  # list[Shot]
    transitions: list  # list[Transition] (one between each pair of shots)
    target_duration_s: float
    metadata: dict = field(default_factory=dict)


class Planner:
    """concept → FilmPlan. v0: template-based (LLM fills content). v1: LLM-driven."""

    # Time allocation by act (woodfantasy percentages)
    ACT_ALLOCATIONS = {
        "setup": (0.10, 0.15),
        "development": (0.25, 0.35),
        "turn": (0.10, 0.20),
        "climax": (0.20, 0.30),
        "resolution": (0.10, 0.20),
    }

    def __init__(self, backend=None, llm_fn=None):
        self.backend = backend  # for max_duration_s, resolution, capabilities
        self.llm_fn = llm_fn    # callable(concept, structure) → filled plan (v1)

    def max_shot_duration(self) -> float:
        if self.backend:
            return self.backend.capabilities.max_duration_s
        return 15.0  # H3 default

    def plan_from_concept(self, concept: str, target_duration_s: float = 60.0,
                          aspect: str = "16:9") -> FilmPlan:
        """Turn a concept into a multi-shot film plan.

        v0: returns a STRUCTURED TEMPLATE (acts/scenes/state-vectors) that an LLM fills.
        v1: calls self.llm_fn to generate the full plan automatically.
        """
        max_shot = self.max_shot_duration()
        n_shots = max(1, int(target_duration_s / max_shot) + (1 if target_duration_s % max_shot else 0))

        if self.llm_fn:
            return self.llm_fn(concept, target_duration_s, aspect, n_shots, max_shot)

        # v0 template: structure ready for LLM to fill
        bible = StateGroup(
            identity={"description": "TODO: character identity from concept"},
            wardrobe_props={"description": "TODO: clothing + key props"},
            geography={"description": "TODO: locations + entries/exits + light"},
            story_knowledge={"description": "TODO: who knows what + when it changes"},
            audio_state={"description": "TODO: music theme + ambient + dialogue language"},
        )
        shots = []
        for i in range(n_shots):
            shot_duration = min(max_shot, target_duration_s - i * max_shot)
            if shot_duration <= 0:
                break
            shots.append(Shot(
                scene_id=i + 1,
                prompt=f"TODO: LLM generates the H3 3-field prompt for shot {i+1} based on the coherence bible + this shot's role in the act structure.",
                mode="t2v" if i == 0 else "i2v",  # shot 1 = T2V; rest = I2V (FL2VA chain)
                duration_s=shot_duration,
                seed=42 + i,
            ))
        transitions = [Transition() for _ in range(len(shots) - 1)]
        return FilmPlan(
            concept=concept, bible=bible, shots=shots, transitions=transitions,
            target_duration_s=target_duration_s,
            metadata={"n_shots": len(shots), "max_shot_s": max_shot, "aspect": aspect,
                      "v0_note": "Template plan — LLM fills prompts + state vectors. v1 auto-generates."},
        )

    def plan_from_shots(self, shots_data: list) -> FilmPlan:
        """Build a plan from a pre-defined shot list (each: {prompt, duration, mode?}).
        This is the 'manual plan' path — user/explicitly provides shots."""
        shots = []
        for i, s in enumerate(shots_data):
            shots.append(Shot(
                scene_id=i + 1, prompt=s["prompt"], mode=s.get("mode", "t2v" if i == 0 else "i2v"),
                duration_s=s.get("duration", 10.0), seed=s.get("seed", 42 + i),
            ))
        return FilmPlan(concept="(manual plan)", bible=StateGroup(), shots=shots,
                        transitions=[Transition() for _ in range(len(shots) - 1)],
                        target_duration_s=sum(s.duration_s for s in shots))
