import numpy as np
from agent.trait.utils.probability_helpers import ProbabilityHelper as P


class EmotionalStabilityTraits:
    _LABELS = {
        "tonic_volatility": ["Low", "Moderate", "High"],
        "emotional_reactivity": ["Low", "Moderate", "High", "Crisis"],
    }

    def __init__(self, base):
        self.base = base
        self.tonic_volatility, self.emotional_reactivity = self._generate()

    def _generate(self):
        # === Tonic Volatility ===
        tv_probs = [0.45, 0.40, 0.15]  # Low, Moderate, High

        if self.base.ET in {"Anxious", "Irritable"}:
            tv_probs[2] += 0.20
            tv_probs[0] -= 0.10
            tv_probs[1] -= 0.10

        if self.base.ET == "Upbeat":
            move = min(0.10, tv_probs[2])
            tv_probs[2] -= move
            tv_probs[0] += move

        if self.base.SR == "High":
            reduction = tv_probs[2] * 0.5
            tv_probs[2] -= reduction
            tv_probs[0] += reduction
        elif self.base.SR == "Low":
            tv_probs[2] *= 1.5

        tonic_volatility = P.sample(self._LABELS["tonic_volatility"], tv_probs)

        # === Emotional Reactivity ===
        er_probs = [0.25, 0.50, 0.20, 0.05]  # Low, Moderate, High, Crisis

        if self.base.CS.startswith("Avoidance"):
            move = min(0.10, er_probs[0])
            er_probs[0] -= move
            er_probs[2] += move

        if self.base.ET == "Anxious":
            er_probs[3] = min(er_probs[3] * 1.5, 0.10)

        if self.base.ET == "Upbeat" and self.base.SR == "High":
            er_probs[3] = max(er_probs[3], 0.01)

        if self.base.SR == "Low" and self.base.ET == "Irritable":
            er_probs[3] = max(er_probs[3], 0.08)

        emotional_reactivity = P.sample(self._LABELS["emotional_reactivity"], er_probs)

        return tonic_volatility, emotional_reactivity

    def to_dict(self):
        return {
            "Tonic Volatility": self.tonic_volatility,
            "Emotional Reactivity": self.emotional_reactivity,
        }
