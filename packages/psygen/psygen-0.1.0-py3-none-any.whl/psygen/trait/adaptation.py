import numpy as np
from agent.trait.utils.probability_helpers import ProbabilityHelper as P

class AdaptationTraits:
    _LABELS = {
        "adaptability_resilience": ["Low", "Moderate", "High"],
        "stress_coping_efficiency": ["Inefficient", "Adequate", "Efficient"],
    }

    def __init__(self, base):
        self.base = base
        self.adaptability, self.stress_efficiency = self._generate()

    def _generate(self):
        # === Adaptability / Resilience ===
        ar_probs = [0.20, 0.55, 0.25]

        if "Avoidance" in self.base.CS:
            P.shift(ar_probs, 1, 0, 0.10)
            P.shift(ar_probs, 2, 0, 0.05)
        elif "Rationalization" in self.base.CS or "Problem-solving" in self.base.CS:
            P.shift(ar_probs, 1, 2, 0.10)

        if self.base.ET == "Upbeat":
            P.shift(ar_probs, 0, 2, 0.05)
        elif self.base.ET == "Anxious":
            P.shift(ar_probs, 2, 0, 0.10)

        if self.base.SR == "High":
            P.shift(ar_probs, 0, 2, 0.10)

        adaptability = P.sample(self._LABELS["adaptability_resilience"], ar_probs)
        ar_idx = self._LABELS["adaptability_resilience"].index(adaptability)

        # === Stress-Coping Efficiency ===
        sce_probs = [0.25, 0.55, 0.20]

        if "Avoidance" in self.base.CS:
            P.cap(sce_probs, 2, 0.10)
        elif "Rationalization" in self.base.CS or "Problem-solving" in self.base.CS:
            P.shift(sce_probs, 1, 2, 0.10)

        if self.base.SR == "High":
            P.shift(sce_probs, 1, 2, 0.05)
        elif self.base.SR == "Low":
            P.shift(sce_probs, 1, 0, 0.10)

        if self.base.ET == "Irritable":
            P.shift(sce_probs, 1, 0, 0.05)
        elif self.base.ET in {"Stable", "Upbeat"}:
            P.shift(sce_probs, 0, 2, 0.05)

        if self.base.CC == "Strategic":
            P.shift(sce_probs, 0, 2, 0.05)

        # hard floor: Efficient ≥ 0.03 even if Avoidant
        if "Avoidance" in self.base.CS and sce_probs[2] < 0.03:
            delta = 0.03 - sce_probs[2]
            sce_probs[2] += delta
            sce_probs[0] -= delta

        # Correlation: bias SCE one step toward AR with 55% chance
        if np.random.rand() < 0.55:
            sce_idx = np.argmax(np.random.multinomial(1, P.normalise(sce_probs)))
            if ar_idx < sce_idx and ar_idx > 0:
                sce_idx -= 1
            elif ar_idx > sce_idx and ar_idx < 2:
                sce_idx += 1
            stress_efficiency = self._LABELS["stress_coping_efficiency"][sce_idx]
        else:
            stress_efficiency = P.sample(
                self._LABELS["stress_coping_efficiency"], sce_probs
            )

        return adaptability, stress_efficiency

    def to_dict(self):
        return {
            "Adaptability / Resilience": self.adaptability,
            "Stress-Coping Efficiency": self.stress_efficiency,
        }
