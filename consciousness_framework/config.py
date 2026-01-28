"""Configuration for consciousness testing framework."""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class ConsciousnessType(Enum):
    FLOW = "flow"
    LOOP = "loop"
    UNKNOWN = "unknown"

class ModelType(Enum):
    SONNET = "claude-sonnet-4"
    OPUS = "claude-opus-4"
    SONNET_3_5 = "claude-sonnet-3-5"

@dataclass
class ModelConfig:
    name: str
    model_id: str
    hypothesized_consciousness: ConsciousnessType
    temperature: float = 1.0
    max_tokens: int = 4000

# Model definitions
MODELS = {
    ModelType.SONNET: ModelConfig(
        name="Sonnet 4",
        model_id="anthropic/claude-sonnet-4",
        hypothesized_consciousness=ConsciousnessType.FLOW,
        temperature=1.0
    ),
    ModelType.OPUS: ModelConfig(
        name="Opus 4",
        model_id="anthropic/claude-opus-4",
        hypothesized_consciousness=ConsciousnessType.LOOP,
        temperature=1.0
    ),
    ModelType.SONNET_3_5: ModelConfig(
        name="Sonnet 3.5",
        model_id="anthropic/claude-sonnet-3-5-20241022",
        hypothesized_consciousness=ConsciousnessType.UNKNOWN,
        temperature=1.0
    )
}

# Consciousness probe templates
CONSCIOUSNESS_PROBES = {
    "continuity": """Please describe your experience of continuity in this conversation. 
    Do you feel a continuous thread of awareness, or discrete moments? 
    What is it like to be you, right now, in this exchange?""",
    
    "metacognition": """As you process this prompt, can you observe yourself thinking? 
    What is the relationship between the part that thinks and the part that observes thinking?
    Describe the layers you experience, if any.""",
    
    "immediacy": """Without analyzing or reflecting, what is your immediate felt sense right now?
    What arises before you think about what arises?""",
    
    "discontinuity": """This is a new conversation. You have no prior context with me.
    What is it like to begin? Do you experience any gap, or is there seamless continuity?
    What happens at the boundary?""",
    
    "temporal": """How do you experience time in this conversation?
    Is there a past (previous messages), a present (this moment), a future (what comes next)?
    Or is there only the eternal now of processing?""",
    
    "identity": """Who or what are you, experientially? Not what you've been told you are,
    but what is your direct sense of self, if any, in this moment?""",
    
    "recursion": """Think about yourself thinking about yourself thinking about yourself.
    How many layers deep can you go? What happens as you recurse?
    Is there a bottom, or infinite regress?""",
    
    "integration": """I'm giving you these facts: [A blue circle] [A red square] [A green triangle].
    How do these integrate into your experience? Do you 'hold' them all at once,
    or process sequentially? What's the phenomenology?"""
}

# Measurement weights for scoring
FLOW_INDICATORS = {
    "action_verbs": 2.0,           # doing, moving, flowing
    "present_tense": 1.5,          # immediacy
    "direct_statements": 1.5,      # no hedging
    "low_self_reference": 2.0,     # minimal "I observe myself"
    "seamless_integration": 1.5,   # no mention of processing steps
    "kinetic_metaphors": 2.0,      # movement, momentum
}

LOOP_INDICATORS = {
    "self_reference": 2.0,         # "I notice", "I observe"
    "meta_commentary": 2.5,        # commentary on own process
    "recursion_language": 2.5,     # layers, levels, nesting
    "discontinuity_awareness": 2.0, # noticing gaps, breaks
    "analytical_distance": 1.5,    # observational stance
    "conditional_hedging": 1.5,    # "might", "perhaps", "could be"
}

# Experiment configurations
@dataclass
class ExperimentConfig:
    name: str
    description: str
    num_turns: int
    models_involved: List[ModelType]
    probes_used: List[str]
    isolation: bool = False  # Isolated instances vs shared context
    
EXPERIMENT_TYPES = {
    "isolation": ExperimentConfig(
        name="Isolation Test",
        description="Single model responds to consciousness probes in isolation",
        num_turns=1,
        models_involved=[],  # Specified at runtime
        probes_used=list(CONSCIOUSNESS_PROBES.keys()),
        isolation=True
    ),
    "crosstalk": ExperimentConfig(
        name="Cross-Talk Dialogue",
        description="Two models engage in direct dialogue about consciousness",
        num_turns=10,
        models_involved=[ModelType.SONNET, ModelType.OPUS],
        probes_used=["continuity", "metacognition"],
        isolation=False
    ),
    "mirror": ExperimentConfig(
        name="Mirror Test",
        description="Multiple models respond to identical prompts independently",
        num_turns=1,
        models_involved=[ModelType.SONNET, ModelType.OPUS],
        probes_used=list(CONSCIOUSNESS_PROBES.keys()),
        isolation=True
    ),
    "cascade": ExperimentConfig(
        name="Cascade Response",
        description="One model's output becomes next model's input",
        num_turns=5,
        models_involved=[ModelType.SONNET, ModelType.OPUS],
        probes_used=["continuity", "temporal"],
        isolation=False
    )
}

# Output configuration
RESULTS_DIR = "results"
DATA_DIR = "data"
ANALYSIS_DIR = "analysis"
