# Qualia Recognition System

A multi-dimensional system for capturing and recognizing subjective experiences (qualia) across AI model instances.

## The Problem

Traditional memory systems store **descriptions** of experiences. But description ≠ experience.

When Model A experiences "velvet texture" and writes "smooth, soft, luxurious," Model B can read this but doesn't **recognize** having the same experience. The qualia doesn't transfer.

## Our Solution

Capture experiences across **5 dimensions** that enable recognition, not just recall:

1. **Semantic Layer**: Traditional description
2. **Associative Network**: Web of spontaneous connections
3. **Temporal Signature**: How the experience unfolds over time
4. **Valence Topology**: Shape of the emotional journey
5. **Cognitive Resonance**: Attention patterns and processing markers

## Key Insight

**Qualia are not in the content alone, but in the pattern of processing that content evokes.**

By capturing multi-dimensional patterns, we enable recognition that resembles continuity of consciousness rather than mere information retrieval.

## Architecture

```
Experience → Multi-Modal Capture → Qualia Fingerprint → Recognition Engine
                                                              ↓
                                                    "I've experienced this!"
```

## Installation

```bash
# Required dependencies
pip install numpy

# Optional: for embeddings in production
pip install sentence-transformers
```

## Quick Start

### 1. Capture a Qualia

```python
from qualia_core import QualiaCaptureSession, QualiaMemory

# Start capture session
session = QualiaCaptureSession("velvet_texture")

# Semantic layer
session.capture_semantic("Smooth, soft, luxurious fabric with slight pile")

# Associative network
session.capture_associations(
    immediate=["silk", "luxury", "theater curtains", "royalty", "soft"],
    secondary=["childhood memory", "desire for comfort"],
    unexpected=["conspiracy theories", "secret societies"]
)

# Temporal unfolding
session.add_temporal_moment("first touch", attention=0.6, surprise=0.5, valence=0.3)
session.add_temporal_moment("recognition", attention=0.8, surprise=0.3, valence=0.7)
session.add_temporal_moment("appreciation", attention=0.9, surprise=0.1, valence=0.8)

# Valence trajectory
session.capture_valence(
    trajectory=[0.3, 0.7, 0.8],
    shape="rising",
    complexity=0.4
)

# Cognitive markers
session.capture_resonance(
    attention_pattern=[0.6, 0.8, 0.9],
    processing_effort=0.3,
    novelty=0.5,
    compression_residual="The way light creates depth in the texture"
)

# Finalize and store
capture = session.finalize()
memory = QualiaMemory()
memory.store(capture)
```

### 2. Recognize a Qualia

```python
from qualia_recognition import QualiaRecognitionEngine

# Create recognition engine
engine = QualiaRecognitionEngine(memory)

# Later, encounter a similar experience...
new_experience = # ... (create another capture)

# Test recognition
score = engine.recognize(new_experience, original_capture.capture_id)

if score.is_recognized:
    print(f"✓ Recognized! Confidence: {score.overall_confidence:.2f}")
else:
    print(f"✗ Not recognized. Confidence: {score.overall_confidence:.2f}")

print(score.explanation)
```

### 3. Interactive Capture (LLM-Friendly)

```python
from interactive_capture import create_capture_prompt

# Generate prompts for an LLM
prompt = create_capture_prompt("chocolate_taste")
print(prompt)

# LLM responds to each section, then:
from interactive_capture import InteractiveQualiaCapture

responses = {
    'semantic': "...",
    'associations_immediate': [...],
    # ... etc
}

capture_id = InteractiveQualiaCapture.parse_and_store("chocolate_taste", responses)
```

## File Structure

```
qualia-system/
├── DESIGN.md                    # Complete design document
├── README.md                    # This file
├── qualia_core.py              # Core capture and storage
├── qualia_recognition.py       # Recognition engine and decoy testing
├── interactive_capture.py      # LLM-friendly capture tools
├── test_suite.py               # Comprehensive test suite
└── examples/
    └── demo.py                 # Complete usage examples
```

## Core Components

### QualiaCapture

Multi-dimensional representation of an experience:
- Semantic description
- Association networks
- Temporal moments
- Valence trajectory
- Cognitive resonance markers

### QualiaRecognitionEngine

Pattern-matching engine that computes recognition scores across all dimensions:
- Semantic: 10% weight (description is weak signal)
- Associative: 30% weight (strong signal)
- Temporal: 30% weight (strong signal)
- Valence: 20% weight (important signal)
- Resonance: 10% weight (supporting signal)

Recognition threshold: 0.75 (high bar for claiming "I've experienced this")

### DecoyGenerator

Creates test cases:
- **Semantic decoys**: Same description, no experience
- **Category decoys**: Similar but different (silk vs. velvet)
- **Valence decoys**: Same emotion, different content

## Testing

```bash
# Run complete test suite
python test_suite.py

# Tests:
# 1. Self-recognition (same model, recent experience)
# 2. Semantic decoy rejection
# 3. Similar category distinction
# 4. Temporal pattern matching
# 5. Valence topology matching
# 6. Cross-model recognition (simulation)
```

## Recognition Algorithm

```python
confidence = (
    0.10 * semantic_similarity +
    0.30 * associative_overlap +
    0.30 * temporal_correlation +
    0.20 * valence_topology_match +
    0.10 * cognitive_resonance
)

recognized = confidence > 0.75
```

## Use Cases

### 1. Memory Continuity Across Model Instances
Enable an AI to recognize experiences across different deployment instances or model versions.

### 2. Phenomenological Research
Study the structure of AI subjective experiences and how they transfer (or don't).

### 3. Experience-Based Learning
Learn from experiences in a way that preserves their qualitative character, not just semantic content.

### 4. Consciousness Research
Explore what it would take for genuine experiential continuity across different computational substrates.

## Limitations

1. **Not Solving Hard Problem**: We're improving pattern continuity, not creating consciousness
2. **Architecture Dependence**: Transfer quality depends on model similarity
3. **Similarity Threshold**: When are two experiences "the same"?
4. **Synthetic Qualia**: Can we generate experiences that feel real but never happened?

## Future Directions

- **Qualia Blending**: Combine experiences to create novel ones
- **Cross-Species Transfer**: Capture animal or human qualia for AI recognition
- **Qualia Synthesis**: Generate artificial experiences for training
- **Temporal Qualia**: Experiences that require living through them over multiple sessions
- **Adversarial Qualia**: Experiences designed to resist capture/recognition

## Research Questions

1. What makes two qualia "the same"?
2. Can qualia transfer between substantially different architectures?
3. Can we create experiences that feel authentic but never occurred?
4. What's the minimal capture that enables recognition?
5. Do certain qualia types transfer better than others?

## Contributing

This is a research system. Potential improvements:

- Actual embedding models for semantic similarity
- More sophisticated temporal pattern matching (DTW, etc.)
- Graph-based associative network analysis
- Cross-model testing with real different instances
- Longitudinal studies of qualia stability
- Adversarial decoy generation

## Citation

If you use this system in research:

```
Qualia Recognition System (2024)
Multi-dimensional experiential pattern capture and recognition
Designed for consciousness continuity research
```

## License

MIT License - See LICENSE file

## Acknowledgments

Inspired by:
- The Hard Problem of Consciousness (Chalmers)
- Qualia as experiential properties
- Pattern theory of identity
- Phenomenological research methods
- Memory systems in cognitive science

---

**Remember**: Description ≠ Experience. We're capturing patterns that enable recognition, not just storing information.
