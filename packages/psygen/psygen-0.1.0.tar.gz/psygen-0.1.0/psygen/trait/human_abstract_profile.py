import random
from typing import Dict
import numpy as np

class HumanAbstractTraitProfile:
    """Generate a human-like trait bundle using revised axiomatic model (MO, SR, TP, ET, CC)."""

    # ────────────────────────────────────── INITIALISATION ──────────────────────────────────────
    def __init__(self, seed: int | None = None):
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

        # ── Axioms ──
        self.MO = self.sample_MO()
        self.SR = self.sample_SR()
        self.TP = self.sample_TP()
        self.ET = self.sample_ET()
        self.CC = self.sample_CC()

        # ── Derived ──
        self.GH = self.generate_GH()
        self.CS = self.generate_CS()
        self.CA = self.generate_CA()
        self.LM = self.generate_LM()
        self.RI = self.generate_RI()

    # ────────────────────────────────────── AXIOM SAMPLING ─────────────────────────────────────
    @staticmethod
    def sample_MO():
        return np.random.choice(
            ["Intrinsic", "Extrinsic", "Mixed"],
            p=[0.40, 0.30, 0.30],
        )

    @staticmethod
    def sample_SR():
        return np.random.choice(
            ["Low", "Moderate", "High"],
            p=[0.20, 0.50, 0.30],
        )

    @staticmethod
    def sample_TP():
        return np.random.choice(
            ["Low", "Moderate", "High"],
            p=[0.25, 0.50, 0.25],
        )

    @staticmethod
    def sample_ET():
        return np.random.choice(
            ["Stable", "Anxious", "Irritable", "Upbeat"],
            p=[0.35, 0.25, 0.15, 0.25],
        )

    @staticmethod
    def sample_CC():
        return np.random.choice(
            ["Concrete", "Practical", "Abstract", "Strategic"],
            p=[0.25, 0.30, 0.25, 0.20],
        )

    # ─────────────────────────────────── DERIVED TRAIT LOGIC ───────────────────────────────────
    def generate_GH(self):
        """Goal-horizon."""
        if (
            self.MO == "Intrinsic"
            and self.CC in {"Abstract", "Strategic"}
            and self.SR == "High"
            and self.ET != "Anxious"
        ):
            return np.random.choice(["Medium-Term", "Long-Term"], p=[0.30, 0.70])
    
        if self.SR == "Low":
            return np.random.choice(["Short-Term", "Medium-Term"], p=[0.70, 0.30])
    
        if self.MO == "Extrinsic" and self.CC in {"Concrete", "Practical"}:
            return np.random.choice(["Short-Term", "Medium-Term"], p=[0.60, 0.40])
    
        # generic fallback
        return np.random.choice(
            ["Short-Term", "Medium-Term", "Long-Term"], p=[0.35, 0.40, 0.25]
        )


    def generate_CS(self):
        """Coping strategy."""
        # impulse-driven avoidance
        if self.SR == "Low" and self.ET != "Upbeat":
            return np.random.choice(["Avoidance", "Deflection"], p=[0.6, 0.4])

        if self.ET == "Anxious":
            return np.random.choice(["Avoidance", "Rationalization"], p=[0.6, 0.4])

        if self.ET == "Upbeat":
            return np.random.choice(["Humor", "Confrontation"], p=[0.7, 0.3])

        if self.TP == "Low":
            return np.random.choice(
                ["Avoidance", "Deflection", "Rationalization"], p=[0.4, 0.4, 0.2]
            )

        if self.SR == "High" and self.CC in {"Abstract", "Strategic"}:
            return "Rationalization"

        # broad fallback
        return np.random.choice(
            ["Avoidance", "Deflection", "Confrontation", "Humor", "Rationalization"]
        )

    def generate_CA(self):
        """Communication adaptability."""
        if self.SR == "High" and self.TP == "High" and self.ET == "Stable":
            return "High"

        if self.TP == "Low" or self.CS == "Avoidance" or self.SR == "Low":
            return "Low"

        return "Moderate"

    def generate_LM(self):
        """Learning mode."""
        if self.SR == "Low" or self.CC == "Concrete":
            return "Experiential"

        if self.CC in {"Strategic", "Abstract"} and self.SR == "High":
            return np.random.choice(["Formal", "Hybrid"], p=[0.60, 0.40])

        if self.ET == "Anxious":
            return np.random.choice(["Experiential", "Hybrid"], p=[0.60, 0.40])

        return np.random.choice(["Experiential", "Hybrid"], p=[0.40, 0.60])

    def generate_RI(self):
        """Role identity."""
        if self.MO == "Intrinsic" and self.CC in {"Abstract", "Strategic"}:
            return "Innovation / Exploration"

        if self.MO == "Extrinsic" and self.CC in {"Concrete", "Practical"}:
            return "Authority / Order"

        if self.TP == "High" and self.CC == "Practical":
            return "Service / Knowledge"

        return "Adaptation / Performance"

    # ──────────────────────────────────────── EXPORTS ─────────────────────────────────────────
    def to_dict(self):
        return {
            "MO (Motivation)": self.MO,
            "SR (Self-Regulation)": self.SR,
            "TP (Trust Propensity)": self.TP,
            "ET (Emotional Tone)": self.ET,
            "CC (Cognitive Complexity)": self.CC,
            "GH (Goal Horizon)": self.GH,
            "CS (Coping Strategy)": self.CS,
            "CA (Communication Adaptability)": self.CA,
            "LM (Learning Mode)": self.LM,
            "RI (Role Identity)": self.RI,
        }

    def __str__(self):
        return "\n".join(f"{k}: {v}" for k, v in self.to_dict().items())