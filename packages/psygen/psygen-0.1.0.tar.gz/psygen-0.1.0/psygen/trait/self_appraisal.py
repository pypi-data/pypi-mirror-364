import numpy as np
from agent.trait.utils.probability_helpers import ProbabilityHelper as P

class SelfAppraisalTraits:
    def __init__(self, base):
        self.base = base
        self.results = self._generate()

    def _generate(self):
        results = {}

        # Base inputs
        MO, SR, GH = self.base.MO, self.base.SR, self.base.GH
        CS = getattr(self.base, "CS", "Rationalization / Problem-solving")
        SCE = getattr(self.base, "stress_coping_efficiency", "Adequate")

        # Trait: Competence Confidence
        labels = [
            "Low Self-Efficacy",
            "Doubtful",
            "Adequate",
            "High / Over-confident",
        ]
        probs = [0.15, 0.30, 0.35, 0.20]  # Low, Doubtful, Adequate, High

        # Condition 1: SR = High & CS = Rationalization
        if SR == "High" and "Problem-solving" in CS:
            P.shift_equal(probs, 2, [1], 0.20)
            P.cap(probs, 2, 0.60)

        # Condition 2: MO = Intrinsic & GH = Long-Term
        if MO == "Intrinsic" and GH == "Long-Term":
            P.multiply(probs, [2], 1.25)

        # Condition 3: SR = Low or CS = Avoidance
        avoid = "Avoidance" in CS
        if SR == "Low" or avoid:
            P.shift_equal(probs, 1, [2], 0.15)
            if avoid:
                P.shift_equal(probs, 0, [2], 0.05)

        probs = P.normalise(probs)
        results["Competence Confidence"] = P.sample(labels, probs)

        return results

    def to_dict(self):
        return self.results
