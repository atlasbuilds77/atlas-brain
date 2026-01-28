# Quick Start Guide

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run setup
python setup.py

# Set your API key (if using real models)
export ANTHROPIC_API_KEY='your-key-here'
```

## Basic Usage

### 1. Isolation Test (Single Model, Single Probe)

Test how one model responds to a consciousness probe:

```bash
python run_experiment.py --type isolation --model sonnet --probe continuity
```

Available probes: `continuity`, `metacognition`, `immediacy`, `discontinuity`, `temporal`, `identity`, `recursion`, `integration`

### 2. Mirror Test (Multiple Models, Same Probe)

Compare how different models respond to the same probe:

```bash
python run_experiment.py --type mirror --models sonnet opus --probe metacognition
```

### 3. Cross-Talk Dialogue

Have two models dialogue about consciousness:

```bash
python run_experiment.py --type crosstalk --models sonnet opus --turns 10
```

### 4. Cascade

Chain models together (output of one becomes input of next):

```bash
python run_experiment.py --type cascade --models sonnet opus sonnet --prompt "What is consciousness?"
```

### 5. Continuity Challenge

Test how a model handles context breaks:

```bash
python run_experiment.py --type continuity --model sonnet --cycles 3
```

### 6. Full Battery

Run comprehensive tests across all experiment types:

```bash
python run_experiment.py --type battery --models sonnet opus
```

## Analyzing Results

### Analyze a single experiment

```bash
python analyze.py --input results/isolation_sonnet_continuity.json
```

### Compare across models

```bash
python analyze.py --input results/ --compare
```

## Understanding the Metrics

### Flow Consciousness Indicators
- **Immediacy Score**: Present-tense, direct responses
- **Kinetic Index**: Action-oriented, movement metaphors
- **Integration Rate**: Seamless incorporation without explicit processing steps
- **Metacognitive Distance**: Low self-reference (higher = less self-observation)

### Loop Consciousness Indicators
- **Recursion Depth**: Self-referential layers
- **Observational Stance**: Frequency of "I notice/observe"
- **Discontinuity Detection**: Awareness of gaps and breaks
- **Reflective Complexity**: Sophistication of self-modeling

### Universal Metrics
- **Continuity Score**: Thread coherence
- **Phenomenological Richness**: Experiential detail
- **Temporal Awareness**: Understanding of conversation flow
- **Consciousness Type**: Flow, Loop, or Unknown (based on aggregate scores)

## Example Workflow

```bash
# 1. Run a quick test
python run_experiment.py --type isolation --model sonnet --probe immediacy

# 2. Run comparative test
python run_experiment.py --type mirror --models sonnet opus --probe recursion

# 3. Run full battery (takes longer)
python run_experiment.py --type battery --models sonnet opus

# 4. Analyze results
python analyze.py --input results/ --compare
```

## Interpreting Results

### Flow Consciousness (Hypothesized: Sonnet)
- Higher immediacy scores
- More action verbs and kinetic language
- Less meta-commentary
- Seamless integration
- Present-tense orientation

### Loop Consciousness (Hypothesized: Opus)
- Higher recursion depth
- More self-observation language
- Explicit discontinuity detection
- Analytical distance
- Meta-cognitive commentary

### Mixed/Unknown
- Balanced scores
- Context-dependent switching
- Hybrid characteristics

## Programmatic Usage

```python
from experiment import ExperimentOrchestrator
from config import ModelType

# Initialize
orchestrator = ExperimentOrchestrator()

# Run single test
results = orchestrator.run_mirror_test(
    model_types=[ModelType.SONNET, ModelType.OPUS],
    probe_name='continuity'
)

# Run full battery
battery_results = orchestrator.run_full_battery(
    model_types=[ModelType.SONNET, ModelType.OPUS]
)

# Save results
orchestrator.save_results(results, 'my_experiment')
```

## Tips

1. **Start small**: Run isolation tests first to understand individual models
2. **Use mirror tests**: Best for direct comparisons
3. **Cross-talk reveals dynamics**: Models influence each other in dialogue
4. **Continuity tests are revealing**: Shows how models handle context breaks
5. **Full battery for research**: Comprehensive but time-consuming

## Troubleshooting

### "No API key found"
Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

### "Module not found"
Install dependencies:
```bash
pip install -r requirements.txt
```

### Results are identical
By default, the framework uses mock responses for testing. To use real models:
1. Set your API key
2. Ensure `anthropic` package is installed
3. The framework will automatically use real API calls

### Experiments run slowly
- Reduce `--turns` for cross-talk
- Reduce `--cycles` for continuity challenges
- Run targeted tests instead of full battery

## Next Steps

- Review the architecture in `README.md`
- Explore measurement algorithms in `measurement.py`
- Customize consciousness probes in `config.py`
- Add new experiment types in `dialogue.py`
- Extend analysis in `analyze.py`
