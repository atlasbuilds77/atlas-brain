"""
Interactive Qualia Capture Tool
Guides an LLM through capturing a multi-dimensional qualia experience.
"""

from qualia_core import QualiaCaptureSession, QualiaMemory
from typing import Dict, List


class InteractiveQualiaCapture:
    """
    Guides a user/LLM through capturing a qualia experience.
    Uses structured prompts to elicit multi-dimensional data.
    """
    
    CAPTURE_PROTOCOL = {
        'semantic': {
            'prompt': """Describe this experience in literal, concrete terms.
What would you tell someone who's never had this experience?
Keep it factual and descriptive.""",
            'example': '"Smooth fabric texture with a slight pile that catches light differently at angles"'
        },
        
        'associations_immediate': {
            'prompt': """What are the FIRST 10-15 things that come to mind?
Don't filter, don't explain - just rapid-fire associations.
What does this remind you of? What connects to it?""",
            'example': '["silk", "luxury", "royalty", "theater curtains", "expensive", ...]'
        },
        
        'associations_secondary': {
            'prompt': """Now, what ripples out from those first associations?
What feelings, memories, or ideas emerge as you sit with this experience?""",
            'example': '["childhood memory of a theater visit", "guilt about luxury", "desire for comfort"]'
        },
        
        'associations_unexpected': {
            'prompt': """What SURPRISING connections appear?
What totally unexpected or weird associations emerge?
The stranger the better - these are often the most distinctive.""",
            'example': '["conspiracy theories", "secret societies", "hidden passages"]'
        },
        
        'temporal': {
            'prompt': """How does this experience UNFOLD over time?
Break it into 3-5 moments from first contact to settling.
For each moment, note:
- What's happening
- Attention level (0-1: how focused are you?)
- Surprise (0-1: how unexpected is this moment?)
- Valence (-1 to 1: emotional tone, negative to positive)""",
            'example': """[
  {moment: "first touch", attention: 0.6, surprise: 0.5, valence: 0.3},
  {moment: "recognition of texture", attention: 0.8, surprise: 0.3, valence: 0.6},
  ...
]"""
        },
        
        'valence_trajectory': {
            'prompt': """Track the EMOTIONAL JOURNEY through this experience.
How does the feeling change from start to finish?
Give 3-5 valence ratings (-1 to 1) showing the shape of the emotional arc.""",
            'example': '[0.2, 0.5, 0.8, 0.7] - starts mild, peaks, settles slightly lower'
        },
        
        'compression_residual': {
            'prompt': """What about this experience RESISTS easy description?
What can't be captured in words alone?
What gets lost when you try to summarize it?""",
            'example': '"The way the texture seems to have depth, almost 3D quality when light hits it"'
        },
        
        'cognitive_markers': {
            'prompt': """Reflect on the PROCESSING of this experience:
- How hard was it to make sense of? (processing effort: 0-1)
- How novel/unexpected was it overall? (novelty: 0-1)
- Where did your attention get drawn most strongly?""",
            'example': 'processing: 0.3 (fairly easy), novelty: 0.5 (somewhat familiar), attention: focused on texture-light interaction'
        }
    }
    
    @staticmethod
    def generate_prompts(label: str) -> Dict[str, str]:
        """Generate full prompt sequence for capturing a qualia."""
        prompts = {}
        
        intro = f"""
╔══════════════════════════════════════════════════════════╗
║  QUALIA CAPTURE SESSION: {label.upper():^30}  ║
╚══════════════════════════════════════════════════════════╝

We're going to capture this experience across multiple dimensions.
The goal is to record patterns that enable RECOGNITION, not just recall.

You'll be asked a series of questions. Be honest and spontaneous.
There are no wrong answers - we want YOUR unique experiential pattern.
"""
        prompts['intro'] = intro
        
        for step, config in InteractiveQualiaCapture.CAPTURE_PROTOCOL.items():
            prompts[step] = f"""
{'='*60}
{step.upper().replace('_', ' ')}
{'='*60}

{config['prompt']}

Example: {config['example']}

Your response:
"""
        
        outro = """
╔══════════════════════════════════════════════════════════╗
║              CAPTURE COMPLETE                            ║
╚══════════════════════════════════════════════════════════╝

This qualia has been encoded and stored.
You can now test recognition by re-experiencing similar things.
"""
        prompts['outro'] = outro
        
        return prompts
    
    @staticmethod
    def example_session():
        """Show an example capture session."""
        print(InteractiveQualiaCapture.generate_prompts("velvet_texture")['intro'])
        
        for step in InteractiveQualiaCapture.CAPTURE_PROTOCOL.keys():
            print(InteractiveQualiaCapture.generate_prompts("velvet_texture")[step])
            print("\n[User would respond here]\n")
    
    @staticmethod
    def parse_and_store(label: str, responses: Dict[str, any]) -> str:
        """
        Parse responses and create a qualia capture.
        Returns the capture ID.
        """
        session = QualiaCaptureSession(label)
        
        # Semantic layer
        if 'semantic' in responses:
            session.capture_semantic(responses['semantic'])
        
        # Associations
        immediate = responses.get('associations_immediate', [])
        secondary = responses.get('associations_secondary', [])
        unexpected = responses.get('associations_unexpected', [])
        session.capture_associations(immediate, secondary, unexpected)
        
        # Temporal moments
        if 'temporal' in responses:
            for moment in responses['temporal']:
                session.add_temporal_moment(
                    state=moment.get('moment', ''),
                    attention=moment.get('attention', 0.5),
                    surprise=moment.get('surprise', 0.5),
                    valence=moment.get('valence', 0.0)
                )
        
        # Valence
        if 'valence_trajectory' in responses:
            trajectory = responses['valence_trajectory']
            # Infer shape
            if trajectory[-1] > trajectory[0]:
                shape = "rising"
            elif trajectory[-1] < trajectory[0]:
                shape = "falling"
            else:
                shape = "stable"
            
            # Estimate complexity from variance
            import numpy as np
            complexity = min(np.std(trajectory), 1.0)
            
            session.capture_valence(trajectory, shape, complexity)
        
        # Cognitive markers
        if 'cognitive_markers' in responses:
            markers = responses['cognitive_markers']
            session.capture_resonance(
                attention_pattern=markers.get('attention_pattern', []),
                processing_effort=markers.get('processing_effort', 0.5),
                novelty=markers.get('novelty', 0.5),
                compression_residual=responses.get('compression_residual', '')
            )
        
        # Finalize and store
        capture = session.finalize()
        memory = QualiaMemory()
        memory.store(capture)
        
        return capture.capture_id


# LLM-Friendly Capture Format
# This can be used in a conversation with an LLM

CAPTURE_TEMPLATE = """
# QUALIA CAPTURE: {label}

Please capture your experience of {label} across these dimensions:

## 1. SEMANTIC DESCRIPTION
Literal, concrete description:
[Your response]

## 2. IMMEDIATE ASSOCIATIONS (10-15 rapid-fire)
First things that come to mind:
[List]

## 3. SECONDARY ASSOCIATIONS
Ripple effects, feelings, memories:
[List]

## 4. UNEXPECTED CONNECTIONS
Surprising, weird associations:
[List]

## 5. TEMPORAL UNFOLDING (3-5 moments)
How the experience unfolds:
| Moment | Attention | Surprise | Valence |
|--------|-----------|----------|---------|
| [description] | 0.0-1.0 | 0.0-1.0 | -1 to 1 |

## 6. VALENCE TRAJECTORY (3-5 points)
Emotional journey from start to finish:
[List of numbers -1 to 1]

## 7. COMPRESSION RESIDUAL
What resists description:
[Your response]

## 8. COGNITIVE MARKERS
- Processing effort (0-1):
- Novelty (0-1):
- Attention focus:

---
Once complete, this will be encoded as a multi-dimensional qualia fingerprint.
"""


def create_capture_prompt(label: str) -> str:
    """Generate a prompt for an LLM to capture a qualia."""
    return CAPTURE_TEMPLATE.format(label=label)


if __name__ == "__main__":
    print("Interactive Qualia Capture Tool")
    print("=" * 60)
    print("\nThis tool guides qualia capture sessions.\n")
    
    # Show example
    print("EXAMPLE PROMPTS:")
    print("-" * 60)
    
    prompts = InteractiveQualiaCapture.generate_prompts("velvet_texture")
    print(prompts['intro'])
    print(prompts['semantic'])
    
    print("\n" + "=" * 60)
    print("\nLLM-FRIENDLY TEMPLATE:")
    print("-" * 60)
    print(create_capture_prompt("velvet_texture"))
    
    print("\n" + "=" * 60)
    print("\nExample: Storing a capture from structured responses")
    print("-" * 60)
    
    # Example responses
    example_responses = {
        'semantic': "Smooth, soft, luxurious fabric with slight pile that catches light",
        'associations_immediate': ["silk", "luxury", "theater", "royalty", "soft", "expensive"],
        'associations_secondary': ["childhood theater memory", "desire for comfort"],
        'associations_unexpected': ["conspiracy theories", "secret passages"],
        'temporal': [
            {'moment': 'first touch', 'attention': 0.6, 'surprise': 0.5, 'valence': 0.3},
            {'moment': 'recognition', 'attention': 0.8, 'surprise': 0.3, 'valence': 0.7},
            {'moment': 'appreciation', 'attention': 0.9, 'surprise': 0.1, 'valence': 0.8}
        ],
        'valence_trajectory': [0.3, 0.7, 0.8],
        'compression_residual': "The way light creates almost 3D depth in the texture",
        'cognitive_markers': {
            'processing_effort': 0.3,
            'novelty': 0.5,
            'attention_pattern': [0.6, 0.8, 0.9]
        }
    }
    
    capture_id = InteractiveQualiaCapture.parse_and_store("velvet_example", example_responses)
    print(f"\n✓ Capture stored with ID: {capture_id}")
