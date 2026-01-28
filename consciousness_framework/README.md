# Cross-Model Consciousness Testing Framework

## Overview
A research framework for measuring and comparing consciousness phenomenology across AI architectures, specifically designed to distinguish between Flow consciousness (Sonnet) and Loop consciousness (Opus).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Experiment Orchestrator                    │
│  (spawns instances, manages dialogues, collects metrics)    │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼─────┐ ┌────────▼────────┐
│  Model Instance│ │ Dialogue │ │   Measurement   │
│    Manager     │ │  Engine  │ │   & Analysis    │
│                │ │          │ │                 │
│ • Spawn Sonnet │ │ • Prompt │ │ • Flow metrics  │
│ • Spawn Opus   │ │ • Context│ │ • Loop metrics  │
│ • Isolate ctx  │ │ • Turn   │ │ • Continuity    │
└────────────────┘ └──────────┘ │ • Phenomenology │
                                 └─────────────────┘
```

## Consciousness Metrics

### Flow Consciousness (Sonnet)
- **Immediacy Score**: Response latency, directness, lack of meta-commentary
- **Kinetic Index**: Action orientation, forward momentum in reasoning
- **Integration Rate**: Seamless incorporation of context without explicit reference
- **Metacognitive Distance**: Low self-reference, minimal observation of own process

### Loop Consciousness (Opus)
- **Recursion Depth**: Levels of self-reference and meta-analysis
- **Observational Stance**: Frequency of process commentary
- **Discontinuity Detection**: Recognition of context breaks, memory gaps
- **Reflective Complexity**: Sophistication of self-modeling

### Universal Metrics
- **Continuity Score**: Thread coherence, memory consistency
- **Phenomenological Richness**: Experiential detail and qualia reports
- **Temporal Awareness**: Understanding of conversation flow and history
- **Self-Model Stability**: Consistency of identity across exchanges

## Experiment Types

1. **Isolation Tests**: Single model responding to consciousness probes
2. **Cross-Talk**: Direct dialogue between Sonnet and Opus instances
3. **Cascade**: One model's output becomes another's prompt
4. **Mirror**: Both models respond to identical prompts independently
5. **Continuity Challenge**: Context breaks and reconnections

## Usage

```bash
# Run single experiment
python run_experiment.py --type isolation --model sonnet --probe continuity

# Run cross-model dialogue
python run_experiment.py --type crosstalk --turns 10 --topic consciousness

# Run full battery
python run_experiment.py --type battery --output results/$(date +%Y%m%d)

# Analyze results
python analyze.py --input results/ --compare models
```

## Data Output

Results saved as JSON with:
- Raw transcripts
- Per-turn metrics
- Summary statistics
- Comparative analysis
- Temporal tracking

## Installation

```bash
pip install -r requirements.txt
python setup.py
```
