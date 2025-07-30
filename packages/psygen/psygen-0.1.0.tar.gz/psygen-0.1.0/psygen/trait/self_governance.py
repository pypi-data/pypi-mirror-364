import numpy as np
from typing import Tuple
from agent.trait.utils.probability_helpers import ProbabilityHelper as P

class SelfGovernanceTraits:
    _ENC = {
        "MO": {"Intrinsic": +1, "Mixed": 0, "Extrinsic": -1},
        "SR": {"High": +1, "Moderate": 0, "Low": -1},
        "TP": {"High": +1, "Moderate": 0, "Low": -1},
        "ET": {"Upbeat": +1, "Stable": +0.5, "Irritable": -0.5, "Anxious": -1},
        "CC": {"Strategic": +1, "Abstract": +0.5, "Practical": -0.5, "Concrete": -1},
        "GH": {"Long-Term": +1, "Medium-Term": 0, "Short-Term": -1},
    }

    _WEIGHTS = {
        "decision_making_tempo": {"SR": 0.50, "CC": 0.30, "ET": -0.20},
        "agency_locus_control":  {"SR": 0.45, "MO": 0.35, "TP": 0.20},
        "drive_ambition":        {"MO": 0.40, "SR": 0.35, "GH": 0.25},
        "risk_appetite":         {"MO": 0.35, "ET": 0.35, "TP": -0.30},
        "impulse_expression":    {"SR": -0.60, "ET": 0.40},
    }

    _LABELS = {
        "decision_making_tempo": [
            "Impulsive", "Hasty", "Balanced", "Deliberative", "Ultra-Deliberative",
        ],
        "agency_locus_control": [
            "Strongly External", "Mostly External", "Balanced", "Mostly Internal", "Strongly Internal",
        ],
        "drive_ambition": [
            "Apathetic", "Under-Motivated", "Typical", "Driven", "Relentlessly Driven",
        ],
        "risk_appetite": [
            "Hyper-Cautious", "Cautious", "Balanced", "Adventurous", "Thrill-Seeking",
        ],
        "impulse_expression": [
            "Uninhibited", "Spontaneous", "Managed", "Restrained", "Over-Controlled",
        ],
    }

    _CUTS = (-1.5, -0.5, 0.5, 1.5)
    _NOISE_SD = 0.35

    def __init__(self, base):
        self.base = base
        self.results = self._generate()

    def _encode(self, key: str, value: str) -> float:
        return self._ENC[key][value]

    def _latent_score(self, weights: dict) -> float:
        z = 0.0
        for ax, w in weights.items():
            if ax == "GH":
                z += w * self._encode("GH", self.base.GH)
            else:
                z += w * self._encode(ax, getattr(self.base, ax))
        z += np.random.normal(0, self._NOISE_SD)
        return z

    def _categorise(self, z: float, labels: Tuple[str]) -> str:
        c1, c2, c3, c4 = self._CUTS
        if z <= c1:
            return labels[0]
        elif z <= c2:
            return labels[1]
        elif z <= c3:
            return labels[2]
        elif z <= c4:
            return labels[3]
        return labels[4]

    def _generate(self) -> Tuple[str, str, str, str, str]:
        results = []
        for key in self._WEIGHTS:
            z = self._latent_score(self._WEIGHTS[key])
            label = self._categorise(z, self._LABELS[key])
            results.append(label)
        return tuple(results)

    def to_dict(self):
        keys = [
            "Decision-Making Tempo",
            "Agency / Locus of Control",
            "Drive / Ambition",
            "Risk Appetite",
            "Impulse Expression",
        ]
        return dict(zip(keys, self.results))
