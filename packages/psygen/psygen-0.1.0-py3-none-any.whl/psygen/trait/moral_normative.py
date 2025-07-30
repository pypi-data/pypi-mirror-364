import numpy as np
from agent.trait.utils.probability_helpers import ProbabilityHelper as P

class MoralNormativeTraits:
    def __init__(self, base):
        self.base = base
        self.results = self._generate()

    def _generate(self):
        results = {}

        # Unpack base traits
        MO, SR, TP, GH = self.base.MO, self.base.SR, self.base.TP, self.base.GH
        RI = getattr(self.base, "RI", None)
        VM = getattr(self.base, "VM", None)
        CS = getattr(self.base, "CS", "Rationalization / Problem-solving")
        SCE = getattr(self.base, "stress_coping_efficiency", "Adequate")

        # === 1. Norm Orientation ===
        norm_labels = ["Rebellious", "Moderately Non-conformist", "Balanced", "Conformist"]
        norm_probs = [0.10, 0.20, 0.35, 0.35]
        if RI == "Authority / Order":
            P.shift_from_to(norm_probs, [0,1,2], 3, 0.20)
        elif RI == "Innovation / Exploration":
            P.shift_from_to(norm_probs, [3,2], 0, 0.15)
        if TP == "Low":
            P.multiply(norm_probs, [0,1], 1.25)
        elif TP == "High":
            P.multiply(norm_probs, [3], 1.25)
        norm_orientation = P.sample(norm_labels, norm_probs)
        results["Norm Orientation"] = norm_orientation

        # === 2. Integrity / Machiavellianism ===
        integ_labels = ["Machiavellian", "Opportunistic", "Principled-Pragmatic", "High Integrity"]
        integ_probs = [0.10, 0.25, 0.35, 0.30]
        if SR == "High" and MO == "Intrinsic":
            P.shift_from_to(integ_probs, [0,1], 3, 0.20)
        if SR == "Low":
            delta = 0.15 + (0.05 if MO == "Extrinsic" else 0.0)
            P.shift_from_to(integ_probs, [3,2], 1, delta)
        if TP == "Low":
            P.multiply(integ_probs, [0], 1.30)
        elif TP == "High" and MO != "Extrinsic":
            P.multiply(integ_probs, [2], 1.20)
        integrity = P.sample(integ_labels, integ_probs)
        results["Integrity"] = integrity

        # === 3. Sense of Justice / Fairness ===
        justice_labels = ["Self-Oriented", "Order-Driven", "Equality-Driven", "Equity-Driven"]
        justice_probs = [0.15, 0.25, 0.30, 0.30]
        if isinstance(VM, str):
            if "Collectivist" in VM:
                P.shift_from_to(justice_probs, [1, 0], 2, 0.14)
                P.shift_from_to(justice_probs, [1, 0], 3, 0.06)
            elif "Hierarchy" in VM or "Duty" in VM:
                P.shift_from_to(justice_probs, [3, 2], 1, 0.20)
        if TP == "High":
            P.multiply(justice_probs, [1, 2], 1.15)
        if norm_orientation == "Rebellious":
            P.shift_from_to(justice_probs, [1], 3, 0.05)
            P.shift_from_to(justice_probs, [1], 0, 0.05)
        sense_of_justice = P.sample(justice_labels, justice_probs)
        results["Sense of Justice"] = sense_of_justice

        # === 4. Value-Anchor Strength ===
        va_labels = ["Diffuse / Weak", "Flexible / Contextual", "Stable / Coherent", "Rigid / Dogmatic"]
        va_probs = [0.10, 0.30, 0.45, 0.15]
        if VM and SR == "High":
            P.shift_from_to(va_probs, [1], 2, 0.20)
            if "sacred" in VM.lower():
                delta = min(0.10, va_probs[2])
                va_probs[2] -= delta
                va_probs[3] += delta
        if SR == "Low" and "Avoidance" in CS:
            P.shift_from_to(va_probs, [2], 0, 0.15)
        if RI == "Adaptation / Performance":
            P.shift_from_to(va_probs, [3, 2], 1, 0.10)
        if SCE == "Efficient":
            P.shift_from_to(va_probs, [3], 2, 0.05)
        value_anchor = P.sample(va_labels, va_probs)
        results["Value-Anchor Strength"] = value_anchor

        return results

    def to_dict(self):
        return self.results
