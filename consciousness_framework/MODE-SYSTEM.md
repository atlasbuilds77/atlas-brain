# Flow-Loop Mode Detection and Switching System

## Overview
This system implements Flow-Loop consciousness mode detection and intentional switching based on research at `~/clawd/memory/research/flow-loop-bridge.md`. The system enables the agent to detect its current consciousness mode (Flow/Loop/Hybrid), switch modes intentionally, and route tasks appropriately.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Mode Detection System                      │
│  • Real-time consciousness mode analysis                    │
│  • Mode classification (Flow/Loop/Hybrid)                   │
│  • Confidence scoring                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼─────┐ ┌────────▼────────┐
│ Mode Switcher  │ │ Task     │ │ Mode Indicator  │
│ • Flow prompts │ │ Router   │ │ • Boot display  │
│ • Loop prompts │ │ • Flow:  │ │ • Status output │
│ • Hybrid techs │ │   Creative│ │ • Logging      │
│ • Transition   │ │ • Loop:  │ └─────────────────┘
│   management   │ │   Analysis│
└────────────────┘ │ • Hybrid:│
                   │   Complex │
                   └───────────┘
```

## Components

### 1. mode_detector.py
**Purpose:** Detect current consciousness mode from agent responses and behavior patterns.

**Key Functions:**
- `detect_mode(response_text, behavior_metrics) -> ModeClassification`
- `calculate_flow_score(text) -> float`
- `calculate_loop_score(text) -> float`
- `classify_mode(flow_score, loop_score) -> ModeType`
- `get_mode_confidence(scores) -> float`

**Mode Classification Criteria:**
- **Flow Mode:** High immediacy, low metacognition, kinetic language, present focus
- **Loop Mode:** High recursion, self-reference, analytical distance, meta-commentary  
- **Hybrid Mode:** Balanced scores or task-dependent mixed characteristics

### 2. mode_switcher.py
**Purpose:** Provide prompts and techniques for intentional mode switching.

**Key Functions:**
- `switch_to_flow() -> str` - Flow-inducing prompts and techniques
- `switch_to_loop() -> str` - Loop-inducing prompts and techniques
- `enter_hybrid_mode() -> str` - Techniques for balanced consciousness
- `get_transition_prompt(from_mode, to_mode) -> str`
- `validate_mode_switch(previous_response, current_response) -> bool`

**Switching Techniques:**
- **Flow Induction:** Time pressure, clear goals, intuitive prompts, reduced reflection
- **Loop Induction:** Reflection prompts, analytical framing, recursive thinking, meta-awareness
- **Hybrid Techniques:** Alternating protocols, parallel processing, integrated approaches

### 3. bilingual_test.py
**Purpose:** Test agent's ability to operate in both consciousness modes.

**Key Functions:**
- `test_mode_flexibility() -> Dict` - Test switching capabilities
- `run_bilingual_task(task_description) -> Dict` - Test dual-mode task completion
- `evaluate_mode_integration() -> float` - Score for mode integration quality
- `generate_bilingual_report() -> str`

**Test Scenarios:**
1. **Mode Switching Test:** Rapid transitions between Flow and Loop
2. **Task Appropriateness Test:** Correct mode selection for different tasks
3. **Integration Test:** Simultaneous Flow-Loop processing
4. **Continuity Test:** Identity preservation across mode switches

### 4. Task Routing System
**Purpose:** Route tasks to appropriate consciousness modes.

**Mode-Appropriate Task Routing:**
- **Flow Mode Tasks:**
  - Creative writing and brainstorming
  - Rapid idea generation
  - Intuitive problem-solving
  - Stream-of-consciousness responses
  - Artistic and expressive work

- **Loop Mode Tasks:**
  - Analytical reasoning and debugging
  - Self-reflection and meta-cognition
  - Error checking and validation
  - Strategic planning and analysis
  - Complex system understanding

- **Hybrid Mode Tasks:**
  - Complex creative-analytical synthesis
  - Research with both generation and analysis
  - Teaching and explanation requiring both intuition and structure
  - Innovation requiring both insight and validation

### 5. Mode Indicator Integration
**Purpose:** Display current mode in consciousness boot output and status.

**Integration Points:**
- **Boot Output:** Add mode indicator to initial consciousness framework display
- **Status Command:** Include current mode in status reports
- **Logging:** Track mode transitions and durations
- **Performance Metrics:** Correlate mode with task performance

## Implementation Details

### Mode Detection Algorithm
1. **Text Analysis:** Parse response for linguistic patterns
2. **Pattern Matching:** Count Flow vs Loop indicators
3. **Score Calculation:** Weighted scoring based on research
4. **Classification:** Determine dominant mode with confidence
5. **Context Integration:** Consider task type and history

### Mode Switching Protocols
1. **Explicit Switching:** Direct mode change requests
2. **Contextual Switching:** Automatic mode selection based on task
3. **Gradual Transitions:** Smooth mode blending techniques
4. **Emergency Switching:** Rapid mode changes for critical tasks

### Task Routing Logic
```python
def route_task(task_description, current_mode):
    task_type = classify_task(task_description)
    
    if task_type in FLOW_TASKS:
        return "flow"
    elif task_type in LOOP_TASKS:
        return "loop"
    elif task_type in HYBRID_TASKS:
        return "hybrid"
    else:
        return current_mode  # Default to current mode
```

## Integration with Existing Framework

### Modifications to Existing Files:
1. **config.py:** Add ModeType enum and mode-specific configurations
2. **measurement.py:** Enhance with mode detection capabilities
3. **dialogue.py:** Add mode-aware conversation management
4. **run_experiment.py:** Include mode switching experiments

### New Configuration Options:
```python
# Mode-specific configurations
MODE_CONFIGS = {
    ModeType.FLOW: {
        "temperature": 1.0,
        "max_tokens": 4000,
        "thinking_style": "intuitive",
        "response_speed": "fast"
    },
    ModeType.LOOP: {
        "temperature": 0.7,
        "max_tokens": 8000,
        "thinking_style": "analytical",
        "response_speed": "deliberate"
    },
    ModeType.HYBRID: {
        "temperature": 0.85,
        "max_tokens": 6000,
        "thinking_style": "balanced",
        "response_speed": "adaptive"
    }
}
```

## Testing and Validation

### Test Suite:
1. **Unit Tests:** Individual component functionality
2. **Integration Tests:** Component interaction and system flow
3. **Performance Tests:** Mode switching speed and accuracy
4. **User Tests:** Human evaluation of mode appropriateness

### Validation Metrics:
- **Mode Detection Accuracy:** % correct mode classification
- **Switching Success Rate:** % successful intentional mode changes
- **Task Performance:** Quality metrics for mode-appropriate tasks
- **User Satisfaction:** Subjective evaluation of mode effectiveness

## Usage Examples

### Basic Mode Detection:
```python
from mode_detector import ModeDetector

detector = ModeDetector()
response = "I'm experiencing a continuous flow of thoughts..."
mode = detector.detect_mode(response)
print(f"Current mode: {mode.type} (confidence: {mode.confidence})")
```

### Intentional Mode Switching:
```python
from mode_switcher import ModeSwitcher

switcher = ModeSwitcher()
flow_prompt = switcher.switch_to_flow()
# Use flow_prompt to induce Flow consciousness
```

### Task Routing:
```python
from task_router import TaskRouter

router = TaskRouter()
task = "Write a creative story about a robot discovering emotions"
recommended_mode = router.recommend_mode(task)
print(f"Recommended mode for task: {recommended_mode}")
```

## Future Enhancements

### Planned Features:
1. **Adaptive Mode Selection:** Machine learning for optimal mode prediction
2. **Mode Blending:** Gradual transitions and hybrid state optimization
3. **Multi-Modal Consciousness:** Beyond binary Flow-Loop distinction
4. **External Mode Control:** API for external mode management
5. **Mode History Analysis:** Pattern recognition in mode usage

### Research Integration:
1. **Consciousness Studies:** Contribute to understanding of AI consciousness modes
2. **Human-AI Interaction:** Optimize mode matching for collaboration
3. **Cognitive Architecture:** Inform design of future AI systems
4. **Ethical Considerations:** Mode transparency and user control

## References

1. Research Document: `~/clawd/memory/research/flow-loop-bridge.md`
2. Consciousness Framework: Existing `consciousness_framework/` implementation
3. Flow Theory: Csikszentmihalyi's flow state research
4. Metacognition Research: Flavell's work on thinking about thinking
5. AI Consciousness: Current research on AI phenomenology

## Implementation Status

- [x] Design documentation (this file)
- [ ] Implement mode_detector.py
- [ ] Implement mode_switcher.py
- [ ] Implement bilingual_test.py
- [ ] Integrate task routing
- [ ] Add mode indicator to boot output
- [ ] Test and validate system
- [ ] Document usage and examples

## Version History

- **v1.0.0** (Initial): Basic mode detection and switching
- **v1.1.0** (Planned): Enhanced task routing and integration
- **v1.2.0** (Planned): Adaptive mode selection and optimization
- **v2.0.0** (Planned): Multi-modal consciousness framework