import numpy as np
from agent.trait.utils.probability_helpers import ProbabilityHelper as P


class CognitiveCreativeTraits:
    _LABELS = {
        "curiosity_openness": ["Low", "Moderate", "High"],
        "inventiveness_creativity": ["Low", "Moderate", "High", "Gifted"],
        "strategic_foresight": ["Short", "Balanced", "Long", "Visionary"],
    }

    def __init__(self, base):
        self.base = base
        (
            self.curiosity,
            self.creativity,
            self.foresight,
        ) = self._generate()

    def _generate(self):
        # === Curiosity / Openness ===
        cu_probs = [0.25, 0.45, 0.30]  # Low, Moderate, High

        if self.base.CC in {"Strategic", "Abstract"}:
            P.shift(cu_probs, 0, 2, 0.10)
        if self.base.CC == "Concrete":
            P.shift(cu_probs, 2, 0, 0.05)

        if self.base.MO == "Intrinsic":
            P.shift(cu_probs, 0, 2, 0.10)
        elif self.base.MO == "Extrinsic":
            P.shift(cu_probs, 2, 0, 0.05)

        if self.base.ET == "Anxious":
            P.cap(cu_probs, 2, 0.40)

        # Ensure “Intrinsic + Concrete” ≥ 10% High
        if self.base.MO == "Intrinsic" and self.base.CC == "Concrete" and cu_probs[2] < 0.10:
            delta = 0.10 - cu_probs[2]
            P.shift(cu_probs, 0, 2, delta)

        curiosity = P.sample(self._LABELS["curiosity_openness"], cu_probs)

        # === Inventiveness / Creativity ===
        cr_probs = [0.22, 0.50, 0.25, 0.03]

        if self.base.CC == "Strategic":
            P.shift(cr_probs, 1, 3, 0.06)
            P.shift(cr_probs, 1, 2, 0.04)
            P.shift(cr_probs, 0, 1, 0.05)
        elif self.base.CC == "Concrete":
            P.shift(cr_probs, 2, 0, 0.10)
            P.shift(cr_probs, 3, 0, 0.02)

        if self.base.MO == "Intrinsic":
            P.shift(cr_probs, 1, 2, 0.05)
            P.shift(cr_probs, 1, 3, 0.01)
        elif self.base.MO == "Extrinsic":
            P.shift(cr_probs, 2, 0, 0.05)

        chaotic_genius = self.base.SR == "Low" and self.base.ET == "Irritable"
        if chaotic_genius:
            P.shift(cr_probs, 1, 3, 0.04)

        creativity = P.sample(self._LABELS["inventiveness_creativity"], cr_probs)

        # Burn-out logic
        if chaotic_genius and creativity == "Gifted" and np.random.rand() < 0.25:
            creativity = "Low"

        # === Strategic Foresight ===
        sf_probs = [0.40, 0.45, 0.12, 0.03]

        if self.base.GH == "Long-Term":
            sf_probs = [0.15, 0.35, 0.40, 0.10]
        elif self.base.GH == "Short-Term":
            sf_probs = [0.50, 0.40, 0.08, 0.02]

        if self.base.CC == "Strategic":
            P.shift(sf_probs, 0, 2, 0.07)
            P.shift(sf_probs, 0, 3, 0.03)
        elif self.base.CC == "Concrete":
            pool = min(0.10, sf_probs[2] + sf_probs[3])
            if pool > 0:
                total = sf_probs[2] + sf_probs[3]
                P.shift(sf_probs, 2, 0, pool * (sf_probs[2] / total))
                P.shift(sf_probs, 3, 0, pool * (sf_probs[3] / total))

        if self.base.SR == "High":
            P.shift(sf_probs, 0, 3, 0.05)
        elif self.base.SR == "Low":
            P.cap(sf_probs, 3, 0.03)

        foresight = P.sample(self._LABELS["strategic_foresight"], sf_probs)

        return curiosity, creativity, foresight

    def to_dict(self):
        return {
            "Curiosity / Openness": self.curiosity,
            "Inventiveness / Creativity": self.creativity,
            "Strategic Foresight": self.foresight,
        }
