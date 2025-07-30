from agent.trait.self_governance import SelfGovernanceTraits
from agent.trait.emotional_stability import EmotionalStabilityTraits
from agent.trait.social_relational import SocialRelationalTraits
from agent.trait.cognitive_creative import CognitiveCreativeTraits
from agent.trait.adaptation import AdaptationTraits
from agent.trait.moral_normative import MoralNormativeTraits
from agent.trait.self_appraisal import SelfAppraisalTraits


class HumanEmergentTraitProfile:
    def __init__(self, base):
        self.base = base

        # Trait cluster generators
        self.self_governance = SelfGovernanceTraits(base)
        self.emotional_stability = EmotionalStabilityTraits(base)
        self.social_relational = SocialRelationalTraits(base)
        self.cognitive_creative = CognitiveCreativeTraits(base)
        self.adaptation = AdaptationTraits(base)
        self.moral_normative = MoralNormativeTraits(base)
        self.self_appraisal = SelfAppraisalTraits(base)

    def to_dict(self):
        output = {}
        output.update(self.self_governance.to_dict())
        output.update(self.emotional_stability.to_dict())
        output.update(self.social_relational.to_dict())
        output.update(self.cognitive_creative.to_dict())
        output.update(self.adaptation.to_dict())
        output.update(self.moral_normative.to_dict())
        output.update(self.self_appraisal.to_dict())
        return output

    def __str__(self):
        return "\n".join(f"{k}: {v}" for k, v in self.to_dict().items())
