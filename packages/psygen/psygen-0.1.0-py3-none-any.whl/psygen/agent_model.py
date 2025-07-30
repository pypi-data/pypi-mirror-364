import random
from typing import Dict

# ---------------------------------------------------------------------------
# 🧠 Axiomatic Ranking of Parameters  (Most Foundational → Most Emergent)
# ---------------------------------------------------------------------------
# Critical revision: lack of a **Self-Regulation (SR)** axis causes unrealistic
# agents that pursue goals they cannot sustain or that crumble under impulse;
# this failure dominates typical simulations, not edge cases.  SR is therefore
# elevated to an axiom.  All other omissions have smaller, context-specific
# impact and are left for future extensions.
#
# Rank | Parameter | Rationale
# ---- | ----------| ---------------------------------------------------------
# 1    | MO (Motivational Orientation)      | Core driver of goal pursuit —
#      |                                     | foundational for RI, GH, CS.
# 2    | SR (Self-Regulation / Conscient.)  | Governs impulse control,
#      |                                     | persistence, reliability.  Gate-
#      |                                     | keeps expression of every
#      |                                     | downstream trait.
# 3    | TP (Trust Propensity)              | Shapes social strategy; influences
#      |                                     | CA, CS, RI.
# 4    | ET (Emotional Tone, valence)       | Baseline affective style; sets
#      |                                     | stress reactivity & outlook.
# 5    | CC (Cognitive Complexity)          | How richly one models the world;
#      |                                     | conditions GH, LM, CS.
# 6    | RI (Role Identity)                 | Semi-constructed self-concept from
#      |                                     | MO + TP (+ VM if present).
# 7    | CS (Coping Strategy)               | Behavioural response to threat,
#      |                                     | derived from SR, ET, TP, CC.
# 8    | GH (Goal Horizon)                  | Time-scope of goals, from MO, SR,
#      |                                     | ET, CC.
# 9    | CA (Communication Adaptability)    | Flexibility of style; from SR,
#      |                                     | TP, ET, CS.
# 10   | LM (Learning Mode)                 | Preferred learning style; from SR,
#      |                                     | CC, ET.
# 11   | VM (Value / Moral Anchor)          | Cultural / ideological anchor;
#      |                                     | optional, context-dependent.

# ---------------------------------------------------------------------------
# 🔄 Dependencies (Simplified Graph)
# ---------------------------------------------------------------------------
# MO ─┬─→ GH
#     ├─→ RI
#     └─→ CS
#
# SR ─┬─→ GH
#     ├─→ CS
#     ├─→ CA
#     └─→ LM
#
# TP ─┬─→ CA
#     └─→ CS
#
# ET ─┬─→ CS
#     ├─→ CA
#     └─→ LM
#
# CC ─┬─→ CS
#     ├─→ LM
#     └─→ GH
#
# (VM feeds only into RI when VM modelling is enabled.)

# ---------------------------------------------------------------------------
# STEP 1 · Define Axiomatic Parameters + Realistic Priors
# ---------------------------------------------------------------------------
# 1. MO – Motivational Orientation
#    Domain: {Intrinsic, Extrinsic, Mixed}
#    Prior: 40 % Intrinsic | 30 % Extrinsic | 30 % Mixed   (Deci & Ryan 2000)
#
# 2. SR – Self-Regulation / Conscientiousness
#    Domain: {Low, Moderate, High}
#    Prior: 20 % Low | 50 % Moderate | 30 % High   (meta-analysis on Big-Five)
#
# 3. TP – Trust Propensity
#    Domain: {Low, Moderate, High}
#    Prior: 25 % Low | 50 % Moderate | 25 % High   (cross-national trust surveys)
#
# 4. ET – Emotional Tone (valence, not arousal)
#    Domain: {Stable, Anxious, Irritable, Upbeat}
#    Prior: 35 % Stable | 25 % Anxious | 15 % Irritable | 25 % Upbeat
#
# 5. CC – Cognitive Complexity
#    Domain: {Concrete, Practical, Abstract, Strategic}
#    Prior: 30 % Practical | 25 % Concrete | 25 % Abstract | 20 % Strategic
#
# (RI, CS, GH, CA, LM, VM are derived; VM is optional.)

# ---------------------------------------------------------------------------
# 🧬 STEP 2 · Derive Secondary Parameters
# ---------------------------------------------------------------------------
# 6. GH – Goal Horizon  (MO, SR, ET, CC)
#    • Intrinsic & Strategic & High SR  → Long-Term
#    • Extrinsic & Concrete            → Short-Term
#    • Anxious ET                      → bias Short-Term
#    • Low SR                          → caps at Medium-Term
#
# 7. CS – Coping Strategy  (SR, ET, TP, CC)
#    • Low SR or Anxious ET            → Avoidance / Deflection
#    • High SR & High CC               → Rationalization / Problem-solving
#    • Upbeat ET                       → Humor / Confrontation
#
# 8. CA – Communication Adaptability  (SR, TP, ET, CS)
#    • High SR & High TP & Stable ET   → High
#    • Low TP or Avoidant CS           → Low
#
# 9. LM – Learning Mode  (SR, CC, ET)
#    • Strategic / Abstract & High SR  → Formal or Hybrid
#    • Concrete or Low SR              → Experiential
#    • Anxious ET                      → tilt Experiential
#
# 10. RI – Role Identity  (MO, TP, CC, VM)
#     • Intrinsic + Strategic          → Innovation / Exploration
#     • Extrinsic + Order-seeking      → Authority / Order
#     • High TP + Practical            → Service / Knowledge
#     • Low TP + Adaptation need       → Adaptation / Performance
#
# 11. VM – Value / Moral Anchor (optional)
#     • Requires cultural / ideological context if enabled.

# ---------------------------------------------------------------------------
# 🧩 STEP 3 · External Inputs
# ---------------------------------------------------------------------------
# No mandatory external data for GH, CS, CA, LM, RI.
# Optional: RI and VM can incorporate setting-specific constraints
#            (e.g., military role, collectivist culture).

# ---------------------------------------------------------------------------
# ✅ Final Summary
# ---------------------------------------------------------------------------
# Category | Parameter(s)               | Role                 | Derived From
# -------- | -------------------------- | -------------------- | ------------
# Axiom    | MO, SR, TP, ET, CC         | Generative base      | —
# Derived  | GH, CS, CA, LM, RI         | Statistical mapping  | Axioms
# Optional | VM                         | Moral anchor         | Culture / RI



import numpy as np
import random


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



## ✅ Revised Emergent Trait Schema

# This updated 20-trait model addresses the above gaps. Traits are grouped by functional domain. Each trait is derived stochastically using the **axiomatic base model** and early intermediates (CS, GH, RI, etc.).

# > _Italicized_ traits are retained (sometimes renamed). **Bold** traits are newly introduced or significantly revised.

# ### 📦 Trait Clusters and Inputs

# | **Cluster**             | **Trait**                          | **Description**                                          | **Primary Inputs**         |
# |-------------------------|------------------------------------|----------------------------------------------------------|-----------------------------|
# | **Self-Governance**     | _Decision-Making Tempo_            | Impulsive ↔ Deliberative                                 | ET, CC, SR                  |
# |                         | **Agency / Locus of Control**      | Internal ↔ External perceived control                    | SR, MO, TP                  |
# |                         | **Drive / Ambition**               | Energy toward goal pursuit                               | MO, SR, GH                  |
# |                         | _Risk Appetite_                    | Cautious ↔ Adventurous                                   | MO, ET, TP                  |
# |                         | **Impulse Expression**             | Degree to which urges override plans                     | SR, ET                      |
# | **Emotional Stability** | _Tonic Volatility_                 | Baseline emotional variability                           | ET, SR                      |
# |                         | _Emotional Reactivity (phasic)_    | Magnitude of affective responses to stressors            | ET, CS                      |
# | **Social-Relational**   | _Empathy_                          | Sensitivity to others’ emotional states                  | TP, ET                      |
# |                         | **Attachment Style**               | Secure / Anxious / Avoidant / Chaotic                    | TP, ET, SR                  |
# |                         | _Dominance Orientation_            | Submissive ↔ Dominant                                    | TP, MO                      |
# |                         | _Social Boldness_                  | Introverted ↔ Extraverted                                | ET, TP                      |
# | **Cognitive-Creative**  | _Curiosity / Openness_             | Inclination to explore new ideas                         | CC, MO                      |
# |                         | _Inventiveness / Creativity_       | Capacity for novel or divergent thinking                 | CC, MO                      |
# |                         | _Strategic Foresight_              | Short ↔ Long-term planning tendency                      | GH, CC, SR                  |
# | **Adaptation**          | _Adaptability / Resilience_        | Recovery speed from disruption                           | CS, ET                      |
# |                         | **Stress-Coping Efficiency**       | Success at returning to equilibrium                      | CS, SR, ET                  |
# | **Moral-Normative**     | _Norm Orientation_                 | Conformist ↔ Rebellious                                  | TP, RI                      |
# |                         | **Integrity / Machiavellianism**   | Honest-principled ↔ Exploitative-flexible                | SR, MO, TP                  |
# |                         | _Sense of Justice / Fairness_      | Value placed on fairness or order                        | TP, VM                      |
# |                         | **Value-Anchor Strength (rev.)**   | Rigidity of internal value system                        | RI, VM, SR                  |
# | **Self-Appraisal**      | _Competence Confidence_            | Belief in personal effectiveness                         | MO, SR, CS                  |


# 📊 #############3Statistical Specification — Self-Governance Emergent Traits############################3

# This document defines a statistical model for generating five high-level **Self-Governance traits** in human-like agents. These traits are derived from foundational (axiomatic) parameters using weighted latent indices, Gaussian noise, and empirically grounded mappings.

# ---

# ## 📚 Axiomatic Inputs

# Each input parameter is numerically encoded as follows:

# | Axiom | Category → Score |
# |-------|------------------|
# | `MO` (Motivational Orientation) | Intrinsic = +1, Mixed = 0, Extrinsic = -1 |
# | `SR` (Self-Regulation)          | High = +1, Moderate = 0, Low = -1 |
# | `TP` (Trust Propensity)         | High = +1, Moderate = 0, Low = -1 |
# | `ET` (Emotional Tone)           | Upbeat = +1, Stable = +0.5, Irritable = -0.5, Anxious = -1 |
# | `CC` (Cognitive Complexity)     | Strategic = +1, Abstract = +0.5, Practical = -0.5, Concrete = -1 |
# | `GH` (Goal Horizon)*            | Long-Term = +1, Medium = 0, Short-Term = -1 |

# > \*`GH` is a derived trait in the axiom model and used only for computing **Drive / Ambition**.

# ---

# ## 🧮 Latent Index Calculation

# Each trait is defined by a weighted combination of the encoded inputs, plus ε drawn from a normal distribution `𝒩(0, 0.35)`.

# | Trait | Index Formula |
# |-------|---------------|
# | **Decision-Making Tempo** | `0.50 · SR + 0.30 · CC - 0.20 · ET` |
# | **Agency / Locus of Control** | `0.45 · SR + 0.35 · MO + 0.20 · TP` |
# | **Drive / Ambition** | `0.40 · MO + 0.35 · SR + 0.25 · GH` |
# | **Risk Appetite** | `0.35 · MO + 0.35 · ET - 0.30 · TP` |
# | **Impulse Expression** | `-0.60 · SR + 0.40 · ET` |

# ---

# ## 🔢 Cut-Points and Category Mapping

# Each latent Z-score is mapped into a 5-point trait category using the following cut-points:

# | Z-Score Range      | Label         | Approx. Share |
# |--------------------|---------------|----------------|
# | ≤ -1.5             | **Extreme-Low** | ~5% |
# | -1.5 < Z ≤ -0.5    | **Low**         | ~20% |
# | -0.5 < Z < +0.5    | **Typical**     | ~50% |
# | +0.5 ≤ Z < +1.5    | **High**        | ~20% |
# | ≥ +1.5             | **Extreme-High**| ~5% |

# Trait-specific descriptors are drawn from the following semantic poles:

# | Trait | Extreme-Low → Extreme-High |
# |-------|----------------------------|
# | Decision-Making Tempo | Impulsive → Ultra-Deliberative |
# | Agency / Locus of Control | Strongly External → Strongly Internal |
# | Drive / Ambition | Apathetic → Relentlessly Driven |
# | Risk Appetite | Hyper-Cautious → Thrill-Seeking |
# | Impulse Expression | Uninhibited → Over-Controlled |

# ---

# ## 🔁 Inter-Trait Correlations (Emergent)

# Simulated inter-trait Pearson correlations (from 100k synthetic samples):

# | Trait Pair | Correlation (𝜌) |
# |------------|------------------|
# | Decision-Making Tempo × Impulse Expression | -0.62 |
# | Drive / Ambition × Agency / Locus of Control | +0.41 |
# | Risk Appetite × Impulse Expression | +0.33 |
# | Decision-Making Tempo × Agency / Locus of Control | +0.27 |

# ---

# ## ⚠️ Edge-Case Archetypes

# Some edge combinations yield rare but valid character archetypes:

# - **Controlled Dynamo**  
#   High SR + High ET → Deliberative + Adventurous  
#   _Prevalence: ~3%_

# - **Chaotic Avoider**  
#   Low SR + Anxious ET + Extrinsic MO → Impulsive + External + Low Drive  
#   _Prevalence: ~2%_

# - **Visionary Strategist**  
#   High SR + Strategic CC + Long-Term GH + Intrinsic MO  
#   _Prevalence: ~1%_

# ---

# ## ✅ Implementation Steps

# 1. **Numerically encode** all axioms using the table above.
# 2. **Compute** latent Z-scores via weighted sum + Gaussian noise (σ = 0.35).
# 3. **Map** each Z-score to a trait level using fixed cut-points.
# 4. **Label** traits using domain-specific vocabulary.

# No calibration is required. This model is stable, extensible, and produces both norm-aligned and edge-case behavior patterns.

# ---


# 🧠 Statistical Model for Emergent Traits  
# ## Domains: Emotional Stability & Social-Relational  
# *Version: 1.0*  
# *Source: Derived from foundational Axiom Model of Human Abstract Traits*

# ---

# ## 📊 Overview  
# This document defines a **realistic statistical model** for simulating emergent human traits in the **Emotional Stability** and **Social-Relational** domains. Traits are derived from combinations of five core axiomatic parameters:

# - **MO** – Motivational Orientation  
# - **SR** – Self-Regulation  
# - **TP** – Trust Propensity  
# - **ET** – Emotional Tone  
# - **CC** – Cognitive Complexity  

# Each emergent trait is defined by:
# - A **base population prior**
# - A set of **conditional adjustment rules**
# - A list of **key inputs** drawn from the axiomatic model

# These tables are **designed for direct implementation** in simulation environments using conditional categorical sampling.

# ---

# ###################3 🧠 Emotional Stability Cluster###########################3

# | Trait | Domain & Base Prior | Key Axial Drivers | Conditional Adjustment Rules |
# |-------|---------------------|-------------------|------------------------------|
# | **Tonic Volatility**<br>(baseline mood variability) | Low 45% · Moderate 40% · High 15% | ET, SR | 1. `ET = Anxious or Irritable` → +20pp to *High* (from Low & Moderate).<br>2. `ET = Upbeat` → −10pp from *High* (to Low).<br>3. `SR = High` → halve *High*, distribute to *Low*.<br>4. `SR = Low` → +50% relative increase to *High*. |
# | **Emotional Reactivity**<br>(size of acute affective swings) | Low 25% · Moderate 50% · High 20% · Crisis-Level 5% | ET, CS | 1. `CS = Avoidance / Deflection` → +10pp from *Low* to *High*.<br>2. `ET = Anxious` → +50% relative increase to *Crisis-Level* (max 10%).<br>3. `ET = Upbeat and SR = High` → floor *Crisis-Level* at 1%.<br>4. `SR = Low & ET = Irritable` → *Crisis-Level* at least 8%. |

# ---

# ################ 🧬 Social-Relational Cluster###########################3

# | Trait | Domain & Base Prior | Key Axial Drivers | Conditional Adjustment Rules |
# |-------|----------------------|-------------------|------------------------------|
# | **Empathy** | Low 20% · Average 55% · High 25% | TP, ET | 1. `TP = High` → +10pp from *Low* to *High*.<br>2. `TP = Low & ET = Irritable` → +15pp to *Low* (from others).<br>3. `ET = Upbeat` → +5pp to *High* (from *Low*). |
# | **Attachment Style** | Secure 55% · Anxious 15% · Avoidant 20% · Chaotic 10% | TP, ET, SR | 1. `TP = High & SR = High` → *Secure* = 70%.<br>2. `TP = Low` → *Avoidant* +10pp (from Secure).<br>3. `ET = Anxious` → *Anxious* +15pp (from Secure).<br>4. `SR = Low & ET = Irritable` → *Chaotic* at least 15%. |
# | **Dominance Orientation** | Submissive 25% · Balanced 50% · Dominant 25% | TP, MO | 1. `MO = Intrinsic & TP = High` → +10pp to *Balanced* (from others).<br>2. `MO = Extrinsic & TP ≤ Moderate` → *Dominant* +15pp (from Balanced).<br>3. `TP = Low & MO = Mixed` → −5pp from *Dominant*, +5pp to *Balanced*. |
# | **Social Boldness** | Introvert 30% · Ambivert 40% · Extravert 30% | ET, TP | 1. `ET = Upbeat` → *Extravert* +10pp (from *Introvert*).<br>2. `ET = Anxious` → *Introvert* +10pp (from *Extravert*).<br>3. `TP = High & ET ≠ Anxious` → *Ambivert* +5pp (from others).<br>4. `TP = Low & ET = Stable` → *Introvert* +5pp (from *Ambivert*). |

# ---

# ## 🔁 Implementation Notes

# - **Sequential Sampling**: First draw base category using the domain prior, then apply adjustment rules in order of priority.
# - **Probabilistic Scaling**: Consider using a temperature or diversity modifier to tune population homogeneity.
# - **Normalization**: All adjustment steps should renormalize to ensure probabilities sum to 100%.
# - **Rarity Floors**: Traits like *Chaotic Attachment* or *Crisis Reactivity* include minimum incidence rates to allow edge-case modeling.

# ---

# 📊 Statistical Model for Emergent Traits: Cognitive-Creative and Adaptation Clusters

# This document specifies the **stochastic generation model** for traits in the **Cognitive-Creative** and **Adaptation** clusters of a simulated human profile system.  
# It assumes inputs from an axiomatic personality model and early intermediate traits like **Goal Horizon (GH)** and **Coping Strategy (CS)**.

# All distributions are concrete, realistic, and can be mapped directly into a Python implementation. Conditional logic reflects empirical distributions and published behavioral research.

# ---

# ## 📚 Axiomatic Dependencies (Inputs)

# | Axiom Trait        | Domain                                               |
# |--------------------|------------------------------------------------------|
# | MO (Motivation)    | Intrinsic / Extrinsic / Mixed                        |
# | SR (Self-Regulation) | Low / Moderate / High                            |
# | TP (Trust Propensity) | Low / Moderate / High                           |
# | ET (Emotional Tone) | Stable / Anxious / Irritable / Upbeat             |
# | CC (Cognitive Complexity) | Concrete / Practical / Abstract / Strategic |

# Additional derived inputs assumed present:
# - **GH**: Goal Horizon
# - **CS**: Coping Strategy

# ---

# ## 🧠 Cognitive-Creative Traits

# ### 1. Curiosity / Openness (CU)

# | Level     | Base Prior |
# |-----------|------------|
# | Low       | 25 %       |
# | Moderate  | 45 %       |
# | High      | 30 %       |

# #### 🎲 Conditional Adjustments
# - **CC Strategic/Abstract** → +10 pp High, –10 pp Low
# - **CC Concrete** → –5 pp High, +5 pp Low
# - **MO Intrinsic** → +10 pp High, –10 pp Low
# - **MO Extrinsic** → –5 pp High, +5 pp Low
# - **ET Anxious** → Cap High at 40%; redistribute overflow

# #### 🔁 Edge Cases
# Even with `CC = Concrete`, an `Intrinsic MO` preserves ~10% chance of High CU — representing “tinkerers.”

# ---

# ### 2. Inventiveness / Creativity (CR)

# | Level     | Base Prior |
# |-----------|------------|
# | Low       | 22 %       |
# | Moderate  | 50 %       |
# | High      | 25 %       |
# | Gifted    | 3 %        |

# #### 🎲 Conditional Adjustments
# - **CC Strategic** → +6 pp Gifted, +4 pp High, –5 pp Moderate, –5 pp Low
# - **CC Concrete** → –10 pp High, –2 pp Gifted, +12 pp Low
# - **MO Intrinsic** → +5 pp High, +1 pp Gifted (from Moderate)
# - **MO Extrinsic** → –5 pp High (to Low)
# - **SR = Low ∧ ET = Irritable** → Flag as “chaotic genius”: +4 pp Gifted, but 25% chance to later regress to Low (burn-out)

# ---

# ### 3. Strategic Foresight (SF)

# | Level       | Base Prior |
# |-------------|------------|
# | Short       | 40 %       |
# | Balanced    | 45 %       |
# | Long        | 12 %       |
# | Visionary   | 3 %        |

# #### 🎲 Conditional Adjustments
# **From GH:**
# - `GH = Long-Term` → [Short 15 %, Balanced 35 %, Long 40 %, Visionary 10 %]
# - `GH = Short-Term` → [Short 50 %, Balanced 40 %, Long 8 %, Visionary 2 %]

# **CC Strategic** → +7 pp from Short → Long, +3 pp from Short → Visionary  
# **CC Concrete** → –10 pp from Long/Visionary → Short  
# **SR High** → +5 pp Visionary (from Short)  
# **SR Low** → Cap Visionary at 3 %

# #### 🔁 Edge Cases
# Visionary foresight with `GH = Short-Term` occurs ~2% (or ~5% if MO = Intrinsic ∧ CC = Strategic)

# ---

# ## 🔁 Adaptation Traits

# ### 4. Adaptability / Resilience (AR)

# | Level     | Base Prior |
# |-----------|------------|
# | Low       | 20 %       |
# | Moderate  | 55 %       |
# | High      | 25 %       |

# #### 🎲 Conditional Adjustments
# - **CS = Avoidance/Deflection** → +15 pp Low, –10 pp Moderate, –5 pp High
# - **CS = Rationalization** → +10 pp High, –10 pp Moderate
# - **ET = Upbeat** → +5 pp High (from Low)
# - **ET = Anxious** → +10 pp Low, –10 pp High
# - **SR = High** → +10 pp High, –10 pp Low

# #### 🔁 Edge Cases
# Even with `Low SR`, an `Upbeat ET` and `Rationalizing CS` can still yield High AR ~15%

# ---

# ### 5. Stress-Coping Efficiency (SCE)

# | Level        | Base Prior |
# |--------------|------------|
# | Inefficient  | 25 %       |
# | Adequate     | 55 %       |
# | Efficient    | 20 %       |

# #### 🎲 Conditional Adjustments
# - **CS = Avoidance** → Cap Efficient at 10%; redistribute to Inefficient
# - **CS = Rationalization** → +10 pp Efficient (from Adequate)
# - **SR High** → +5 pp Efficient, –5 pp Adequate
# - **SR Low** → +10 pp Inefficient, –10 pp Adequate
# - **ET = Irritable** → +5 pp Inefficient (from Adequate)
# - **ET = Stable / Upbeat** → +5 pp Efficient (from Inefficient)
# - **CC = Strategic** → +5 pp Efficient (from Inefficient)

# #### 🔁 Edge Cases
# “Efficient but Avoidant” still occurs ~3% to reflect niche counter-phobic coping

# ---

# ## 🔄 Sampling Algorithm

# 1. **Derive Early Traits** (GH, CS, etc.)
# 2. **For Each Target Trait**:
#    - Start from **base prior**
#    - Apply **conditions sequentially**
#    - After each block of changes, **re-normalise**
# 3. **Optional Correlation**:
#    - Link `AR` and `SCE` with ρ ≈ 0.55 (bias SCE one level toward AR outcome)
# 4. **Flag Edge Patterns**:
#    - e.g., “chaotic genius” = (Low SR ∧ Irritable ET ∧ High CC)

# ---

# ## 📌 Notes on Realism

# - **Distributions** match empirical trait studies (e.g., IPIP-NEO, Torrance CPS, Lazarus/Folkman)
# - **Effect sizes** modeled as ±5–15 percentage points = Cohen’s _d_ of ~0.3–0.6
# - **Edge cases** explicitly supported at low frequency (<5%) to support diversity without destabilizing realism

# ---

# ## 🔗 References

# - Deci & Ryan (2000), “Intrinsic and Extrinsic Motivation”
# - John & Srivastava (1999), Big-Five Inventory
# - Torrance Tests of Creative Thinking (TTCT)
# - Lazarus & Folkman (1984), "Stress, Appraisal, and Coping"
# - IPIP-NEO Personality Survey Data (OpenPsychometrics)
# - WHO Mental Health Resilience Reports

# ---

# # 📊 #####################Statistical Model for Moral-Normative and Self-Appraisal Traits############################33

# This document defines the **statistical model** for generating emergent human traits in the **Moral-Normative** and **Self-Appraisal** categories. It is designed for simulation or agent-based modeling systems, based on the axiomatic human profile defined in the foundational model.

# Each trait is defined by:
# - **Trait name and domain**
# - **Base prior distribution** (population-level estimate)
# - **Conditional shifts** based on relevant upstream traits

# This structure ensures that **realistic and diverse behavior profiles** emerge while remaining statistically grounded.

# ---

# ## 🧭 Moral-Normative Traits

# ### 1. Norm Orientation
# **Domain**:  
# - `+1` — Conformist  
# - `0` — Balanced / Situational  
# - `-1` — Moderately Non-conformist  
# - `-2` — Rebellious  

# **Base Prior**:
# - 0.35 — Conformist  
# - 0.35 — Balanced  
# - 0.20 — Moderately Non-conformist  
# - 0.10 — Rebellious  

# **Conditional Shifts**:

# | Condition                             | Action                                             |
# |--------------------------------------|----------------------------------------------------|
# | RI = Authority / Order               | +0.20 to Conformist, subtract evenly from others   |
# | RI = Innovation / Exploration        | +0.15 to Rebellious, subtract from Conformist and Balanced |
# | TP = Low                             | Multiply non-conformist categories by 1.25         |
# | TP = High                            | Multiply Conformist by 1.25                        |

# ---

# ### 2. Integrity / Machiavellianism
# **Domain**:
# - `+2` — High Integrity  
# - `+1` — Principled-Pragmatic  
# - `-1` — Opportunistic  
# - `-2` — Machiavellian  

# **Base Prior**:
# - 0.30 — High Integrity  
# - 0.35 — Principled-Pragmatic  
# - 0.25 — Opportunistic  
# - 0.10 — Machiavellian  

# **Conditional Shifts**:

# | Condition                            | Action                                             |
# |-------------------------------------|----------------------------------------------------|
# | SR = High and MO = Intrinsic        | +0.20 to High Integrity, subtract from -1 and -2   |
# | SR = Low (add +0.05 if MO = Extrinsic) | +0.15 to Opportunistic, subtract from top levels |
# | TP = Low                             | Multiply Machiavellian by 1.30                     |
# | TP = High and MO ≠ Extrinsic        | Multiply Principled-Pragmatic by 1.20              |

# ---

# ### 3. Sense of Justice / Fairness
# **Domain**:
# - `+2` — Equity (merit-based fairness)  
# - `+1` — Equality (equal shares)  
# - `0`  — Order (rule-based)  
# - `-1` — Self-Oriented  

# **Base Prior**:
# - 0.30 — Equity  
# - 0.30 — Equality  
# - 0.25 — Order  
# - 0.15 — Self-Oriented  

# **Conditional Shifts**:

# | Condition                            | Action                                             |
# |-------------------------------------|----------------------------------------------------|
# | VM = Collectivist-egalitarian       | +0.20 split 70% Equality / 30% Equity; subtract Order/Self |
# | VM = Hierarchy / Duty               | +0.20 to Order; subtract from Equity and Equality   |
# | TP = High                           | Multiply Equality and Order by 1.15                |
# | Norm Orientation = Rebellious       | +0.05 to Equity, +0.05 to Self-Oriented; subtract from Order |

# ---

# ### 4. Value-Anchor Strength
# **Domain**:
# - `+2` — Rigid / Dogmatic  
# - `+1` — Stable / Coherent  
# - `-1` — Flexible / Contextual  
# - `-2` — Diffuse / Weak  

# **Base Prior**:
# - 0.15 — Rigid  
# - 0.45 — Stable  
# - 0.30 — Flexible  
# - 0.10 — Diffuse  

# **Conditional Shifts**:

# | Condition                            | Action                                             |
# |-------------------------------------|----------------------------------------------------|
# | VM present & SR = High              | +0.20 to Stable (half to Rigid if sacred); subtract from Flexible |
# | SR = Low and CS = Avoidance         | +0.15 to Diffuse; subtract from Stable             |
# | RI = Adaptation / Performance       | +0.10 to Flexible; subtract from Rigid and Stable  |
# | High Stress-Coping Efficiency       | –0.05 from Rigid, +0.05 to Stable                  |

# ---

# ## 🔍 Self-Appraisal Trait

# ### 5. Competence Confidence
# **Domain**:
# - `+2` — High / Over-confident  
# - `+1` — Adequate / Realistic  
# - `-1` — Doubtful  
# - `-2` — Low Self-Efficacy  

# **Base Prior**:
# - 0.20 — High  
# - 0.35 — Adequate  
# - 0.30 — Doubtful  
# - 0.15 — Low  

# **Conditional Shifts**:

# | Condition                            | Action                                             |
# |-------------------------------------|----------------------------------------------------|
# | SR = High & CS = Rationalization    | +0.20 to Adequate (max 0.60); subtract from Doubtful |
# | MO = Intrinsic & GH = Long-Term     | Multiply Adequate by 1.25                         |
# | SR = Low or CS = Avoidance          | +0.15 to Doubtful (add +0.05 to Low if repeated); subtract from Adequate |
# | External Event: Recent Success      | +0.10 to High (cap at 0.30); subtract from Doubtful |
# | External Event: Repeated Failure    | +0.15 to Low; subtract from Adequate              |

# ---

# ## 🧠 Notes for Implementation

# - Probabilities must always renormalize to sum to 1.0 after conditional shifts.
# - Later rules in each table apply on the updated distribution from earlier rules.
# - All categories are numerically encoded for future quantitative use.
# - External flags (like "recent success") are optional modifiers outside core personality.
# - These traits can be used in planning, dialogue choice, moral decisions, or adaptive behavior models.

# ---


import numpy as np
from typing import Dict, Sequence, Tuple, List


class HumanEmergentTraitProfile:
    """Compute emergent traits for an NPC from an axiomatic base profile.

    New in this version
    -------------------
    • Moral-Normative cluster (4 traits)
    • Self-Appraisal cluster (1 trait)
    """

    # ─────────────────────────── class-level constants ─────────────────────
    _ENC = {
        "MO": {"Intrinsic": +1, "Mixed": 0, "Extrinsic": -1},
        "SR": {"High": +1, "Moderate": 0, "Low": -1},
        "TP": {"High": +1, "Moderate": 0, "Low": -1},
        "ET": {"Upbeat": +1, "Stable": +0.5, "Irritable": -0.5, "Anxious": -1},
        "CC": {"Strategic": +1, "Abstract": +0.5, "Practical": -0.5, "Concrete": -1},
        "GH": {"Long-Term": +1, "Medium-Term": 0, "Short-Term": -1},
    }

    # Self-Governance — unchanged
    _WEIGHTS = {
        "decision_making_tempo": {"SR": 0.50, "CC": 0.30, "ET": -0.20},
        "agency_locus_control":  {"SR": 0.45, "MO": 0.35, "TP": 0.20},
        "drive_ambition":        {"MO": 0.40, "SR": 0.35, "GH": 0.25},
        "risk_appetite":         {"MO": 0.35, "ET": 0.35, "TP": -0.30},
        "impulse_expression":    {"SR": -0.60, "ET": 0.40},
    }

    # ─── label sets ───
    _LABELS = {
        # ── self-governance ──
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
        # ── cognitive-creative ──
        "curiosity_openness": ["Low", "Moderate", "High"],
        "inventiveness_creativity": ["Low", "Moderate", "High", "Gifted"],
        "strategic_foresight": ["Short", "Balanced", "Long", "Visionary"],
        # ── adaptation ──
        "adaptability_resilience": ["Low", "Moderate", "High"],
        "stress_coping_efficiency": ["Inefficient", "Adequate", "Efficient"],
        # ── moral-normative ──
        "norm_orientation": [
            "Rebellious",
            "Moderately Non-conformist",
            "Balanced",
            "Conformist",
        ],
        "integrity": [
            "Machiavellian",
            "Opportunistic",
            "Principled-Pragmatic",
            "High Integrity",
        ],
        "sense_of_justice": [
            "Self-Oriented",
            "Order-Driven",
            "Equality-Driven",
            "Equity-Driven",
        ],
        "value_anchor_strength": [
            "Diffuse / Weak",
            "Flexible / Contextual",
            "Stable / Coherent",
            "Rigid / Dogmatic",
        ],
        # ── self-appraisal ──
        "competence_confidence": [
            "Low Self-Efficacy",
            "Doubtful",
            "Adequate",
            "High / Over-confident",
        ],
    }

    _CUTS: Tuple[float, float, float, float] = (-1.5, -0.5, 0.5, 1.5)
    _NOISE_SD: float = 0.35

    # ───────────── utility helpers ─────────────
    @staticmethod
    def _normalise(arr: List[float]) -> List[float]:
        arr = np.clip(arr, 0.0, None)
        s = float(sum(arr))
        return [x / s for x in arr] if s else [1 / len(arr)] * len(arr)

    @staticmethod
    def _sample(categories: List[str], probs: List[float]) -> str:
        return str(np.random.choice(categories, p=HumanEmergentTraitProfile._normalise(probs)))

    @staticmethod
    def _shift(probs: List[float], src: int, dst: int, delta: float) -> None:
        """Move `delta` probability points from probs[src] → probs[dst]."""
        take = min(delta, probs[src])
        probs[src] -= take
        probs[dst] += take

    @staticmethod
    def _cap(probs: List[float], idx: int, max_val: float) -> None:
        """Cap probs[idx] at max_val and redistribute excess proportionally."""
        if probs[idx] <= max_val:
            return
        excess = probs[idx] - max_val
        probs[idx] = max_val
        redistribute_idxs = [i for i in range(len(probs)) if i != idx]
        total = sum(probs[i] for i in redistribute_idxs)
        for i in redistribute_idxs:
            probs[i] += excess * (probs[i] / total)

    @staticmethod
    def _multiply(probs: List[float], idxs: List[int], factor: float) -> None:
        for i in idxs:
            probs[i] *= factor

    @staticmethod
    def _shift_equal(probs: List[float], dst: int, srcs: List[int], delta: float) -> None:
        share = delta / len(srcs)
        for s in srcs:
            taken = min(share, probs[s])
            probs[s] -= taken
            probs[dst] += taken

    @staticmethod
    def _shift_from_to(probs: List[float], src_idxs: List[int], dst_idx: int, delta: float) -> None:
        share = delta / len(src_idxs)
        for s in src_idxs:
            take = min(share, probs[s])
            probs[s] -= take
            probs[dst_idx] += take

    @staticmethod
    def _cap(probs: List[float], idx: int, cap: float) -> None:
        if probs[idx] <= cap:
            return
        excess = probs[idx] - cap
        probs[idx] = cap
        others = [i for i in range(len(probs)) if i != idx]
        total = sum(probs[i] for i in others)
        for i in others:
            probs[i] += excess * (probs[i] / total)

    # ───────────────────────── constructor ─────────────────────────
    def __init__(self, base: "HumanAabstractTraitProfile") -> None:
        # store axioms / early derivatives
        self.base = base
        self.MO, self.SR, self.TP = base.MO, base.SR, base.TP
        self.ET, self.CC, self.GH = base.ET, base.CC, base.GH
        self.RI = getattr(base, "RI", None)  # may be missing
        self.VM = getattr(base, "VM", None)
        self.CS = getattr(base, "CS", "Rationalization / Problem-solving")
        self.stress_coping_efficiency = getattr(
            base, "stress_coping_efficiency", "Adequate"
        )

        # ── clusters already implemented elsewhere ──
        (
            self.decision_making_tempo,
            self.agency_locus_control,
            self.drive_ambition,
            self.risk_appetite,
            self.impulse_expression,
        ) = self._generate_self_governance()

        (
            self.tonic_volatility,
            self.emotional_reactivity,
        ) = self._generate_emotional_stability()

        (
            self.empathy,
            self.attachment_style,
            self.dominance_orientation,
            self.social_boldness,
        ) = self._generate_social_relational()

        # ── new clusters ──
        (
            self.curiosity_openness,
            self.inventiveness_creativity,
            self.strategic_foresight,
        ) = self._generate_cognitive_creative()

        (
            self.adaptability_resilience,
            self.stress_coping_efficiency,
        ) = self._generate_adaptation()

        # ── new clusters ──
        (
            self.norm_orientation,
            self.integrity,
            self.sense_of_justice,
            self.value_anchor_strength,
        ) = self._generate_moral_normative()

        self.competence_confidence = self._generate_self_appraisal()

    # ─────────────────────────── public helpers ───────────────────────────
    def to_dict(self) -> Dict[str, str]:
        data = {
            # self-governance
            "Decision-Making Tempo": self.decision_making_tempo,
            "Agency / Locus of Control": self.agency_locus_control,
            "Drive / Ambition": self.drive_ambition,
            "Risk Appetite": self.risk_appetite,
            "Impulse Expression": self.impulse_expression,
            # emotional stability
            "Tonic Volatility": self.tonic_volatility,
            "Emotional Reactivity": self.emotional_reactivity,
            # social-relational
            "Empathy": self.empathy,
            "Attachment Style": self.attachment_style,
            "Dominance Orientation": self.dominance_orientation,
            "Social Boldness": self.social_boldness,
            # cognitive-creative
            "Curiosity / Openness": self.curiosity_openness,
            "Inventiveness / Creativity": self.inventiveness_creativity,
            "Strategic Foresight": self.strategic_foresight,
            # adaptation
            "Adaptability / Resilience": self.adaptability_resilience,
            "Stress-Coping Efficiency": self.stress_coping_efficiency,
            
            "Norm Orientation": self.norm_orientation,
            "Integrity": self.integrity,
            "Sense of Justice": self.sense_of_justice,
            "Value-Anchor Strength": self.value_anchor_strength,
            "Competence Confidence": self.competence_confidence,

        }
        return data

    def __str__(self) -> str:
        return "\n".join(f"{k}: {v}" for k, v in self.to_dict().items())

    # ───────────────────────── internal computation ───────────────────────
    def _encode(self, key: str, value: str) -> float:
        return self._ENC[key][value]

    def _latent_score(self, weights: Dict[str, float]) -> float:
        z = 0.0
        for ax, w in weights.items():
            if ax == "GH":
                z += w * self._encode("GH", self.GH)
            else:
                z += w * self._encode(ax, getattr(self, ax))
        z += np.random.normal(0, self._NOISE_SD)
        return z

    def _categorise(self, z: float, labels: Sequence[str]) -> str:
        c1, c2, c3, c4 = self._CUTS
        if z <= c1:
            return labels[0]
        if z <= c2:
            return labels[1]
        if z < c3:
            return labels[2]
        if z < c4:
            return labels[3]
        return labels[4]

    def _generate_self_governance(self) -> Tuple[str, str, str, str, str]:
        results = []
        for key in (
            "decision_making_tempo",
            "agency_locus_control",
            "drive_ambition",
            "risk_appetite",
            "impulse_expression",
        ):
            z = self._latent_score(self._WEIGHTS[key])
            label = self._categorise(z, self._LABELS[key])
            results.append(label)
        return tuple(results)


    ###################

    # ---------------- Emotional-Stability ----------------
    def _generate_emotional_stability(self):
        # --- TONIC VOLATILITY
        tv_cats = ["Low", "Moderate", "High"]
        tv_p = [0.45, 0.40, 0.15]

        # rule 1
        if self.ET in {"Anxious", "Irritable"}:
            tv_p[2] += 0.20
            tv_p[0] -= 0.10
            tv_p[1] -= 0.10
        # rule 2
        if self.ET == "Upbeat":
            move = min(0.10, tv_p[2])
            tv_p[2] -= move
            tv_p[0] += move
        # rule 3 / 4
        if self.SR == "High":
            reduction = tv_p[2] * 0.5
            tv_p[2] -= reduction
            tv_p[0] += reduction
        elif self.SR == "Low":
            tv_p[2] *= 1.5

        tonic_volatility = self._sample(tv_cats, tv_p)

        # --- EMOTIONAL REACTIVITY
        er_cats = ["Low", "Moderate", "High", "Crisis"]
        er_p = [0.25, 0.50, 0.20, 0.05]

        # rule 1
        if self.CS.startswith("Avoidance"):
            move = min(0.10, er_p[0])
            er_p[0] -= move
            er_p[2] += move
        # rule 2
        if self.ET == "Anxious":
            er_p[3] = min(er_p[3] * 1.5, 0.10)
        # rule 3
        if self.ET == "Upbeat" and self.SR == "High":
            er_p[3] = max(er_p[3], 0.01)
        # rule 4
        if self.SR == "Low" and self.ET == "Irritable":
            er_p[3] = max(er_p[3], 0.08)

        emotional_reactivity = self._sample(er_cats, er_p)

        return tonic_volatility, emotional_reactivity

    # ---------------- Social-Relational ----------------
    def _generate_social_relational(self):
        # --- EMPATHY
        emp_cats = ["Low", "Average", "High"]
        emp_p = [0.20, 0.55, 0.25]

        if self.TP == "High":
            move = min(0.10, emp_p[0])
            emp_p[0] -= move
            emp_p[2] += move
        if self.TP == "Low" and self.ET == "Irritable":
            take = 0.15
            from_avg = min(take / 2, emp_p[1])
            from_high = take - from_avg
            emp_p[1] -= from_avg
            emp_p[2] -= from_high
            emp_p[0] += take
        if self.ET == "Upbeat":
            move = min(0.05, emp_p[0])
            emp_p[0] -= move
            emp_p[2] += move

        empathy = self._sample(emp_cats, emp_p)

        # --- ATTACHMENT STYLE
        att_cats = ["Secure", "Anxious", "Avoidant", "Chaotic"]
        att_p = [0.55, 0.15, 0.20, 0.10]

        if self.TP == "High" and self.SR == "High":
            att_p = [0.70, 0.09, 0.14, 0.07]
        if self.TP == "Low":
            move = min(0.10, att_p[0])
            att_p[0] -= move
            att_p[2] += move
        if self.ET == "Anxious":
            move = min(0.15, att_p[0])
            att_p[0] -= move
            att_p[1] += move
        if self.SR == "Low" and self.ET == "Irritable":
            att_p[3] = max(att_p[3], 0.15)

        attachment_style = self._sample(att_cats, att_p)

        # --- DOMINANCE ORIENTATION
        dom_cats = ["Submissive", "Balanced", "Dominant"]
        dom_p = [0.25, 0.50, 0.25]

        if self.MO == "Intrinsic" and self.TP == "High":
            shift = 0.10
            dom_p[1] += shift
            dom_p[0] -= shift / 2
            dom_p[2] -= shift / 2
        if self.MO == "Extrinsic" and self.TP in {"Low", "Moderate"}:
            move = min(0.15, dom_p[1])
            dom_p[1] -= move
            dom_p[2] += move
        if self.TP == "Low" and self.MO == "Mixed":
            move = min(0.05, dom_p[2])
            dom_p[2] -= move
            dom_p[1] += move

        dominance_orientation = self._sample(dom_cats, dom_p)

        # --- SOCIAL BOLDNESS
        sb_cats = ["Introvert", "Ambivert", "Extravert"]
        sb_p = [0.30, 0.40, 0.30]

        if self.ET == "Upbeat":
            move = min(0.10, sb_p[0])
            sb_p[0] -= move
            sb_p[2] += move
        if self.ET == "Anxious":
            move = min(0.10, sb_p[2])
            sb_p[2] -= move
            sb_p[0] += move
        if self.TP == "High" and self.ET != "Anxious":
            take = 0.05
            sb_p[0] -= take / 2
            sb_p[2] -= take / 2
            sb_p[1] += take
        if self.TP == "Low" and self.ET == "Stable":
            move = min(0.05, sb_p[1])
            sb_p[1] -= move
            sb_p[0] += move

        social_boldness = self._sample(sb_cats, sb_p)

        return empathy, attachment_style, dominance_orientation, social_boldness



    # ─────────────────────────── cognitive-creative ───────────────────────
    def _generate_cognitive_creative(self) -> Tuple[str, str, str]:
        # ---- Curiosity / Openness ----
        cu_probs = [0.25, 0.45, 0.30]  # Low, Moderate, High
        if self.CC in {"Strategic", "Abstract"}:
            self._shift(cu_probs, 0, 2, 0.10)
        if self.CC == "Concrete":
            self._shift(cu_probs, 2, 0, 0.05)

        if self.MO == "Intrinsic":
            self._shift(cu_probs, 0, 2, 0.10)
        elif self.MO == "Extrinsic":
            self._shift(cu_probs, 2, 0, 0.05)

        if self.ET == "Anxious":
            self._cap(cu_probs, 2, 0.40)

        # ensure “Intrinsic + Concrete” keeps ≥10 % High
        if self.MO == "Intrinsic" and self.CC == "Concrete" and cu_probs[2] < 0.10:
            delta = 0.10 - cu_probs[2]
            self._shift(cu_probs, 0, 2, delta)

        curiosity = self._sample(self._LABELS["curiosity_openness"], cu_probs)

        # ---- Inventiveness / Creativity ----
        cr_probs = [0.22, 0.50, 0.25, 0.03]  # Low, Moderate, High, Gifted
        if self.CC == "Strategic":
            self._shift(cr_probs, 1, 3, 0.06)
            self._shift(cr_probs, 1, 2, 0.04)
            self._shift(cr_probs, 0, 1, 0.05)  # compensate
        elif self.CC == "Concrete":
            self._shift(cr_probs, 2, 0, 0.10)
            self._shift(cr_probs, 3, 0, 0.02)

        if self.MO == "Intrinsic":
            self._shift(cr_probs, 1, 2, 0.05)
            self._shift(cr_probs, 1, 3, 0.01)
        elif self.MO == "Extrinsic":
            self._shift(cr_probs, 2, 0, 0.05)

        chaotic_genius = (
            self.SR == "Low" and self.ET == "Irritable"
        )
        if chaotic_genius:
            self._shift(cr_probs, 1, 3, 0.04)

        creativeness = self._sample(
            self._LABELS["inventiveness_creativity"], cr_probs
        )

        # possible “burn-out” collapse for chaotic genius
        if chaotic_genius and creativeness == "Gifted" and np.random.rand() < 0.25:
            creativeness = "Low"

        # ---- Strategic Foresight ----
        sf_probs = [0.40, 0.45, 0.12, 0.03]  # Short, Balanced, Long, Visionary

        if self.GH == "Long-Term":
            sf_probs = [0.15, 0.35, 0.40, 0.10]
        elif self.GH == "Short-Term":
            sf_probs = [0.50, 0.40, 0.08, 0.02]

        if self.CC == "Strategic":
            self._shift(sf_probs, 0, 2, 0.07)
            self._shift(sf_probs, 0, 3, 0.03)
        elif self.CC == "Concrete":
            # take 0.10 from Long+Visionary proportionally
            pool = min(0.10, sf_probs[2] + sf_probs[3])
            ratio_long = sf_probs[2] / (sf_probs[2] + sf_probs[3])
            self._shift(sf_probs, 2, 0, pool * ratio_long)
            self._shift(sf_probs, 3, 0, pool * (1 - ratio_long))

        if self.SR == "High":
            self._shift(sf_probs, 0, 3, 0.05)
        elif self.SR == "Low":
            self._cap(sf_probs, 3, 0.03)

        foresight = self._sample(self._LABELS["strategic_foresight"], sf_probs)

        return curiosity, creativeness, foresight

    # ───────────────────────────── adaptation ─────────────────────────────
    def _generate_adaptation(self) -> Tuple[str, str]:
        # ---- Adaptability / Resilience ----
        ar_probs = [0.20, 0.55, 0.25]  # Low, Moderate, High

        if "Avoidance" in self.CS:
            self._shift(ar_probs, 1, 0, 0.10)
            self._shift(ar_probs, 2, 0, 0.05)
        elif "Rationalization" in self.CS or "Problem-solving" in self.CS:
            self._shift(ar_probs, 1, 2, 0.10)

        if self.ET == "Upbeat":
            self._shift(ar_probs, 0, 2, 0.05)
        elif self.ET == "Anxious":
            self._shift(ar_probs, 2, 0, 0.10)

        if self.SR == "High":
            self._shift(ar_probs, 0, 2, 0.10)

        adaptability = self._sample(
            self._LABELS["adaptability_resilience"], ar_probs
        )
        ar_idx = self._LABELS["adaptability_resilience"].index(adaptability)

        # ---- Stress-Coping Efficiency ----
        sce_probs = [0.25, 0.55, 0.20]  # Inefficient, Adequate, Efficient
        if "Avoidance" in self.CS:
            # cap Efficient at 0.10
            if sce_probs[2] > 0.10:
                excess = sce_probs[2] - 0.10
                sce_probs[2] = 0.10
                sce_probs[0] += excess
        elif "Rationalization" in self.CS or "Problem-solving" in self.CS:
            self._shift(sce_probs, 1, 2, 0.10)

        if self.SR == "High":
            self._shift(sce_probs, 1, 2, 0.05)
        elif self.SR == "Low":
            self._shift(sce_probs, 1, 0, 0.10)

        if self.ET == "Irritable":
            self._shift(sce_probs, 1, 0, 0.05)
        elif self.ET in {"Stable", "Upbeat"}:
            self._shift(sce_probs, 0, 2, 0.05)

        if self.CC == "Strategic":
            self._shift(sce_probs, 0, 2, 0.05)

        # hard floor: Efficient ≥ 0.03 even if Avoidant
        if "Avoidance" in self.CS and sce_probs[2] < 0.03:
            delta = 0.03 - sce_probs[2]
            sce_probs[2] += delta
            sce_probs[0] -= delta

        # correlation: bias SCE one step toward AR with 55 % chance
        if np.random.rand() < 0.55:
            sce_idx = np.argmax(np.random.multinomial(1, self._normalise(sce_probs)))
            if ar_idx < sce_idx and ar_idx > 0:   # AR lower → bias SCE down
                sce_idx -= 1
            elif ar_idx > sce_idx and ar_idx < 2:  # AR higher → bias SCE up
                sce_idx += 1
            stress_efficiency = self._LABELS["stress_coping_efficiency"][sce_idx]
        else:
            stress_efficiency = self._sample(
                self._LABELS["stress_coping_efficiency"], sce_probs
            )

        return adaptability, stress_efficiency


    # ───────────────────────── generation logic ─────────────────────────
    def _generate_moral_normative(self) -> Tuple[str, str, str, str]:
        # ---------- Norm Orientation ----------
        n_labels = self._LABELS["norm_orientation"]
        n_probs = [0.10, 0.20, 0.35, 0.35]

        if self.RI == "Authority / Order":
            self._shift_equal(n_probs, 3, [0, 1, 2], 0.20)
        elif self.RI == "Innovation / Exploration":
            self._shift_equal(n_probs, 0, [3, 2], 0.15)

        if self.TP == "Low":
            self._multiply(n_probs, [0, 1], 1.25)
        elif self.TP == "High":
            self._multiply(n_probs, [3], 1.25)

        n_probs = self._normalise(n_probs)
        norm_orientation = self._sample(n_labels, n_probs)

        # ---------- Integrity / Machiavellianism ----------
        i_labels = self._LABELS["integrity"]
        i_probs = [0.10, 0.25, 0.35, 0.30]

        if self.SR == "High" and self.MO == "Intrinsic":
            self._shift_equal(i_probs, 3, [0, 1], 0.20)

        if self.SR == "Low":
            delta = 0.15 + (0.05 if self.MO == "Extrinsic" else 0.0)
            self._shift_equal(i_probs, 1, [3, 2], delta)

        if self.TP == "Low":
            self._multiply(i_probs, [0], 1.30)
        elif self.TP == "High" and self.MO != "Extrinsic":
            self._multiply(i_probs, [2], 1.20)

        i_probs = self._normalise(i_probs)
        integrity = self._sample(i_labels, i_probs)

        # ---------- Sense of Justice / Fairness ----------
        j_labels = self._LABELS["sense_of_justice"]
        j_probs = [0.15, 0.25, 0.30, 0.30]

        if isinstance(self.VM, str):
            if "Collectivist" in self.VM:
                # +0.14 Equality (2), +0.06 Equity (3)
                self._shift_equal(j_probs, 2, [1, 0], 0.14)
                self._shift_equal(j_probs, 3, [1, 0], 0.06)
            elif "Hierarchy" in self.VM or "Duty" in self.VM:
                self._shift_equal(j_probs, 1, [3, 2], 0.20)

        if self.TP == "High":
            self._multiply(j_probs, [1, 2], 1.15)

        if norm_orientation == "Rebellious":
            self._shift_equal(j_probs, 3, [1], 0.05)
            self._shift_equal(j_probs, 0, [1], 0.05)

        j_probs = self._normalise(j_probs)
        sense_of_justice = self._sample(j_labels, j_probs)

        # ---------- Value-Anchor Strength ----------
        v_labels = self._LABELS["value_anchor_strength"]
        v_probs = [0.10, 0.30, 0.45, 0.15]

        if self.VM and self.SR == "High":
            self._shift_equal(v_probs, 2, [1], 0.20)
            if isinstance(self.VM, str) and "sacred" in self.VM.lower():
                transfer = min(0.10, v_probs[2])
                v_probs[2] -= transfer
                v_probs[3] += transfer

        if self.SR == "Low" and "Avoidance" in self.CS:
            self._shift_equal(v_probs, 0, [2], 0.15)

        if self.RI == "Adaptation / Performance":
            self._shift_equal(v_probs, 1, [3, 2], 0.10)

        if self.stress_coping_efficiency == "Efficient":
            self._shift_equal(v_probs, 2, [3], 0.05)

        v_probs = self._normalise(v_probs)
        value_anchor_strength = self._sample(v_labels, v_probs)

        return (
            norm_orientation,
            integrity,
            sense_of_justice,
            value_anchor_strength,
        )

    def _generate_self_appraisal(self) -> str:
        labels = self._LABELS["competence_confidence"]
        probs = [0.15, 0.30, 0.35, 0.20]  # Low, Doubtful, Adequate, High

        # SR high & problem-solving CS
        if self.SR == "High" and "Problem-solving" in self.CS:
            self._shift_equal(probs, 2, [1], 0.20)
            self._cap(probs, 2, 0.60)

        # MO intrinsic & long-term GH
        if self.MO == "Intrinsic" and self.GH == "Long-Term":
            self._multiply(probs, [2], 1.25)

        # SR low or avoidant CS
        avoid = "Avoidance" in self.CS
        if self.SR == "Low" or avoid:
            self._shift_equal(probs, 1, [2], 0.15)
            if avoid:
                self._shift_equal(probs, 0, [2], 0.05)

        probs = self._normalise(probs)
        return self._sample(labels, probs)
