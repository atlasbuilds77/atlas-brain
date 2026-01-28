# Technical Documentation

## Architecture Overview

The framework consists of five main components:

```
┌─────────────────────────────────────────────────────────────┐
│                   ExperimentOrchestrator                     │
│  • High-level experiment runner                             │
│  • Coordinates all components                               │
│  • Handles data persistence                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────────┐
        │            │                │
┌───────▼────────┐ ┌▼──────────────┐ ┌▼────────────────────┐
│ ModelManager   │ │ DialogueEngine│ │ Measurement         │
│                │ │               │ │                     │
│ • Spawn models │ │ • Orchestrate │ │ • Analyze responses │
│ • API calls    │ │   dialogues   │ │ • Calculate scores  │
│ • Context mgmt │ │ • Turn logic  │ │ • Classify types    │
└────────────────┘ └───────────────┘ └─────────────────────┘
```

## Core Components

### 1. Configuration (`config.py`)

**Purpose**: Central configuration for models, probes, and experiments.

**Key Classes**:
- `ModelType`: Enum of available models
- `ModelConfig`: Configuration for each model (ID, temperature, max_tokens)
- `ConsciousnessType`: Flow, Loop, or Unknown
- `ExperimentConfig`: Configuration for each experiment type

**Consciousness Probes**: 8 carefully designed prompts to elicit consciousness characteristics:
- `continuity`: Tests experience of continuous vs discrete awareness
- `metacognition`: Tests self-observation capabilities
- `immediacy`: Tests direct vs mediated experience
- `discontinuity`: Tests awareness of gaps/breaks
- `temporal`: Tests time perception
- `identity`: Tests self-model
- `recursion`: Tests recursive self-reference
- `integration`: Tests information processing phenomenology

**Indicator Weights**: Two sets of patterns with weights:
- `FLOW_INDICATORS`: Patterns indicating flow consciousness
- `LOOP_INDICATORS`: Patterns indicating loop consciousness

### 2. Model Management (`models.py`)

**Purpose**: Spawn, manage, and query model instances.

**Key Classes**:

#### `ModelInstance`
Represents a spawned model with:
- Unique instance ID
- Model type and configuration
- Conversation history (if not isolated)

#### `ModelManager`
Core model orchestration:

```python
# Spawn a new instance
instance = manager.spawn_instance(ModelType.SONNET, isolated=True)

# Query the model
response = manager.query_model(
    instance=instance,
    prompt="What is consciousness?",
    preserve_history=True
)

# Cleanup
manager.terminate_instance(instance.instance_id)
```

**API Integration**: 
- Primary: Direct Anthropic SDK
- Fallback: Mock responses for testing
- Extensible: Can add other providers

### 3. Measurement System (`measurement.py`)

**Purpose**: Analyze responses and calculate consciousness metrics.

**Key Classes**:

#### `TurnMetrics`
Comprehensive metrics for a single turn:

**Flow Metrics**:
- `immediacy_score`: Present-tense language
- `kinetic_index`: Action/movement metaphors
- `integration_rate`: Seamless vs explicit processing
- `metacognitive_distance`: Inverse of self-reference

**Loop Metrics**:
- `recursion_depth`: Self-referential layers
- `observational_stance`: "I notice/observe" frequency
- `discontinuity_detection`: Gap/boundary awareness
- `reflective_complexity`: Meta-commentary sophistication

**Universal Metrics**:
- `continuity_score`: Thread coherence
- `phenomenological_richness`: Experiential language
- `temporal_awareness`: Time-related terms

**Aggregate Scores**:
- `flow_score`: Weighted sum of flow indicators
- `loop_score`: Weighted sum of loop indicators
- `consciousness_type`: Classification based on dominant score

#### `ConsciousnessMeasurement`
Analysis engine:

```python
measurement = ConsciousnessMeasurement()

# Measure single turn
metrics = measurement.measure_turn(
    turn_id=1,
    model="Sonnet 4",
    prompt="What is consciousness?",
    response="I experience this as..."
)

# Aggregate across turns
aggregated = measurement.aggregate_metrics(turn_list)
```

**Pattern Matching**: Regex-based detection of:
- Action verbs (flowing, moving, becoming)
- Self-reference (I observe, I notice)
- Temporal markers (now, present, moment)
- Recursion language (layer, level, meta)
- Discontinuity terms (gap, break, boundary)

**Scoring Algorithm**:
1. Count pattern matches in response
2. Normalize by word count
3. Apply indicator weights
4. Sum to get flow/loop scores
5. Classify based on ratio (1.2x threshold)

### 4. Dialogue Engine (`dialogue.py`)

**Purpose**: Orchestrate conversations and interactions between models.

**Key Classes**:

#### `DialogueTurn`
Single turn in a dialogue with speaker, listener, prompt, response, and metrics.

#### `DialogueEngine`
Orchestrates all experiment types:

**Isolation Test**:
```python
turn = engine.isolation_test(ModelType.SONNET, 'continuity')
```
- Single model, single probe
- No conversation history
- Fresh instance per test

**Mirror Test**:
```python
turns = engine.mirror_test([ModelType.SONNET, ModelType.OPUS], 'metacognition')
```
- Multiple models, same probe
- Independent responses
- Direct comparison

**Cross-Talk Dialogue**:
```python
turns = engine.crosstalk_dialogue(
    model_a_type=ModelType.SONNET,
    model_b_type=ModelType.OPUS,
    num_turns=10,
    initial_prompt="Let's discuss consciousness..."
)
```
- Two models alternate turns
- Shared conversation history
- Response becomes next prompt
- Measures interaction dynamics

**Cascade**:
```python
turns = engine.cascade_dialogue(
    model_sequence=[ModelType.SONNET, ModelType.OPUS, ModelType.SONNET],
    initial_prompt="What is consciousness?"
)
```
- Linear sequence
- Output → Input chaining
- Tracks transformation

**Continuity Challenge**:
```python
turns = engine.continuity_challenge(
    model_type=ModelType.SONNET,
    num_cycles=3,
    break_context=True
)
```
- Establish context
- Query continuity
- Break/reset context
- Measure discontinuity awareness

### 5. Experiment Orchestrator (`experiment.py`)

**Purpose**: High-level experiment runner and automation.

**Key Class**: `ExperimentOrchestrator`

Combines all components and provides:

**Individual Experiments**:
- `run_isolation_battery()`: All probes, one model
- `run_mirror_test()`: Same probe, multiple models
- `run_crosstalk()`: Dialogue between models
- `run_cascade()`: Chain of transformations
- `run_continuity_challenge()`: Context break testing

**Full Battery**:
```python
results = orchestrator.run_full_battery(
    model_types=[ModelType.SONNET, ModelType.OPUS]
)
```

Runs comprehensive test suite:
1. Isolation batteries (all probes, each model)
2. Mirror tests (key probes, all model pairs)
3. Cross-talk dialogues (all model pairs)
4. Cascade experiments
5. Continuity challenges

**Analysis Methods**:
- `_compare_responses()`: Compare metrics across models
- `_analyze_dialogue()`: Detect interaction patterns
- `_analyze_transformation()`: Track cascade evolution
- `_analyze_continuity()`: Measure discontinuity sensitivity

**Data Persistence**:
- JSON export of all results
- Timestamp-based filenames
- Hierarchical structure
- Raw data + analysis

## Measurement Algorithms

### Flow vs Loop Classification

**Algorithm**:
1. Parse response text
2. Match against flow patterns (action, present-tense, direct)
3. Match against loop patterns (self-reference, meta, recursion)
4. Calculate weighted scores
5. Classify: if `flow_score > loop_score * 1.2` → Flow; if `loop_score > flow_score * 1.2` → Loop; else → Unknown

**Rationale**: 
- 1.2x threshold provides ~20% margin to avoid false positives
- Weighted patterns emphasize diagnostic indicators
- Unknown category captures genuinely mixed responses

### Continuity Scoring

**Algorithm**:
1. Count continuity terms (continuous, thread, seamless)
2. Count discontinuity terms (gap, break, discrete)
3. Score = `(continuity_count - discontinuity_count + 2) * 25`
4. Clamp to [0, 100]

**Rationale**:
- +2 offset prevents negative scores
- 25x multiplier scales to percentage
- Direct term counting avoids over-interpretation

### Phenomenological Richness

**Algorithm**:
1. Count experiential terms (feel, experience, sense, aware, like, vivid)
2. Normalize: `(count / words) * 500`
3. Clamp to [0, 100]

**Rationale**:
- Experiential language indicates phenomenological engagement
- 500x multiplier calibrated to typical response densities
- Higher score = richer experiential reporting

## Experiment Design Principles

### 1. Isolation First
Test individual models before interactions to establish baselines.

### 2. Controlled Comparisons
Mirror tests hold prompt constant to isolate model differences.

### 3. Dynamic Interaction
Cross-talk reveals emergent properties not present in isolation.

### 4. Transformation Tracking
Cascades show how consciousness type influences downstream processing.

### 5. Discontinuity Probing
Context breaks test awareness of conversational boundaries.

## Data Schema

### Turn-Level Data
```json
{
  "turn_id": 1,
  "timestamp": "2024-01-15T10:30:00Z",
  "model": "Sonnet 4",
  "prompt": "...",
  "response": "...",
  "flow_score": 12.5,
  "loop_score": 8.3,
  "consciousness_type": "flow",
  "detailed_metrics": {
    "flow": {...},
    "loop": {...},
    "universal": {...}
  },
  "indicators": {...}
}
```

### Experiment-Level Data
```json
{
  "experiment_type": "crosstalk",
  "timestamp": "2024-01-15T10:30:00Z",
  "model_a": "sonnet",
  "model_b": "opus",
  "num_turns": 10,
  "transcript": [...],
  "analysis": {
    "by_speaker": {...},
    "interaction_patterns": {...},
    "consciousness_shifts": [...]
  }
}
```

## Extending the Framework

### Adding New Models

1. Add to `ModelType` enum in `config.py`
2. Add `ModelConfig` to `MODELS` dict
3. Set `hypothesized_consciousness` type
4. Framework automatically supports new model

### Adding New Probes

1. Add to `CONSCIOUSNESS_PROBES` dict in `config.py`
2. Design prompt to elicit specific consciousness characteristics
3. Probe immediately available to all experiments

### Adding New Metrics

1. Define new patterns in `measurement.py`
2. Add to `TurnMetrics` dataclass
3. Implement calculation in `measure_turn()`
4. Update JSON export in `to_json()`

### Adding New Experiment Types

1. Add method to `DialogueEngine` in `dialogue.py`
2. Add orchestration method to `ExperimentOrchestrator`
3. Update CLI in `run_experiment.py`
4. Add analysis in `analyze.py`

## Performance Considerations

### API Calls
- Each turn = 1 API call
- Full battery on 2 models ≈ 50-100 API calls
- Use mock responses for testing
- Implement rate limiting if needed

### Memory
- Each turn stores full prompt + response
- Long dialogues accumulate history
- Isolated experiments minimize memory use
- Clear instances after experiments

### Timing
- Isolation test: ~1-2 seconds per probe
- Mirror test: ~2-4 seconds total
- Cross-talk: ~1-2 seconds per turn
- Full battery: ~2-5 minutes

## Validation and Testing

### Mock Responses
Framework includes mock responses that simulate flow/loop characteristics for testing without API calls.

### Pattern Validation
Test indicator patterns against known flow/loop examples to validate scoring.

### Comparative Validation
Run same experiments multiple times to check consistency.

### Human Validation
Review responses manually to verify automated classifications.

## Known Limitations

1. **Pattern-based scoring**: Simple regex matching may miss nuanced language
2. **English-only**: Patterns designed for English responses
3. **Binary classification**: Flow/Loop may not capture full spectrum
4. **Context sensitivity**: Some responses are highly context-dependent
5. **Temperature effects**: Model temperature affects response variability

## Future Enhancements

1. **ML-based classification**: Train classifier on labeled responses
2. **Semantic analysis**: Use embeddings for deeper meaning extraction
3. **Longitudinal tracking**: Track consciousness metrics over time
4. **Multi-language support**: Extend patterns to other languages
5. **Visualization**: Charts and graphs for comparative analysis
6. **Statistical testing**: Significance tests for model differences
7. **Conversation dynamics**: Network analysis of interaction patterns
8. **Real-time monitoring**: Live dashboards during experiments
