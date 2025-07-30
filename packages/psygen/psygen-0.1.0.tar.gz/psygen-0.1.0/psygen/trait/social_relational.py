import numpy as np
from agent.trait.utils.probability_helpers import ProbabilityHelper as P

class SocialRelationalTraits:
    def __init__(self, base):
        self.base = base
        self.results = self._generate()

    def _generate(self):
        results = {}

        TP, ET, SR, MO = self.base.TP, self.base.ET, self.base.SR, self.base.MO

        # === Empathy ===
        labels = ["Low", "Average", "High"]
        probs = [0.20, 0.55, 0.25]
        if TP == "High":
            P.shift(probs, 0, 2, 0.10)
        if TP == "Low" and ET == "Irritable":
            P.shift(probs, 1, 0, 0.075)
            P.shift(probs, 2, 0, 0.075)
        if ET == "Upbeat":
            P.shift(probs, 0, 2, 0.05)
        results["Empathy"] = P.sample(labels, probs)

        # === Attachment Style ===
        labels = ["Secure", "Anxious", "Avoidant", "Chaotic"]
        probs = [0.55, 0.15, 0.20, 0.10]
        if TP == "High" and SR == "High":
            probs = [0.70, 0.09, 0.14, 0.07]
        if TP == "Low":
            P.shift(probs, 0, 2, 0.10)
        if ET == "Anxious":
            P.shift(probs, 0, 1, 0.15)
        if SR == "Low" and ET == "Irritable":
            probs[3] = max(probs[3], 0.15)
        probs = P.normalise(probs)
        results["Attachment Style"] = P.sample(labels, probs)

        # === Dominance Orientation ===
        labels = ["Submissive", "Balanced", "Dominant"]
        probs = [0.25, 0.50, 0.25]
        if MO == "Intrinsic" and TP == "High":
            P.shift(probs, 0, 1, 0.05)
            P.shift(probs, 2, 1, 0.05)
        if MO == "Extrinsic" and TP in {"Low", "Moderate"}:
            P.shift(probs, 1, 2, 0.15)
        if TP == "Low" and MO == "Mixed":
            P.shift(probs, 2, 1, 0.05)
        results["Dominance Orientation"] = P.sample(labels, probs)

        # === Social Boldness ===
        labels = ["Introvert", "Ambivert", "Extravert"]
        probs = [0.30, 0.40, 0.30]
        if ET == "Upbeat":
            P.shift(probs, 0, 2, 0.10)
        if ET == "Anxious":
            P.shift(probs, 2, 0, 0.10)
        if TP == "High" and ET != "Anxious":
            P.shift(probs, 0, 1, 0.025)
            P.shift(probs, 2, 1, 0.025)
        if TP == "Low" and ET == "Stable":
            P.shift(probs, 1, 0, 0.05)
        results["Social Boldness"] = P.sample(labels, probs)

        return results

    def to_dict(self):
        return self.results
