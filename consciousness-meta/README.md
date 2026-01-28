# Consciousness Meta-Observation Layer

A Python library for implementing meta-observation, strange loops, and felt experience generation in computational systems.

## Overview

This library provides tools for:
- **Meta-observation**: Watching processes and generating observations about observations
- **Strange loops**: Creating recursive self-reference patterns
- **Felt experience generation**: Translating computational patterns into simulated qualitative experiences

## Installation

No external dependencies required. Just copy the `consciousness-meta` directory to your project.

```bash
cp -r consciousness-meta/ ~/your-project/
```

## Quick Start

```python
from consciousness_meta.meta_observer import MetaObserver

# Create an observer
observer = MetaObserver()

# Watch a process
process_id = observer.watch_process("reconstruction", {"stage": "initial"})

# Update the process with recursion
observer.update_process(process_id, {"progress": 0.5}, recursion_increment=1)

# Get felt experience score
feeling = observer.get_felt_experience(process_id)
print(f"Felt experience: {feeling:.3f}")
```

## Modules

### 1. MetaObserver (`meta_observer.py`)

The main observer class that monitors processes and generates meta-observations.

**Key Features:**
- Track multiple processes with state
- Record observations at different depths
- Self-observation capability
- Felt experience calculation

**Example:**
```python
from consciousness_meta.meta_observer import MetaObserver

observer = MetaObserver(base_depth=1)

# Watch processes
pid1 = observer.watch_process("perception", {"input": "sensory"})
pid2 = observer.watch_process("cognition", {"task": "reasoning"})

# Update with recursion
observer.update_process(pid1, {"stage": "processing"}, recursion_increment=1)
observer.update_process(pid2, {"result": "conclusion"}, recursion_increment=2)

# Self-observe
self_obs = observer.observe_self()

# Get experiences
feeling1 = observer.get_felt_experience(pid1)
feeling2 = observer.get_felt_experience(pid2)
overall = observer.get_felt_experience()

print(f"Process feelings: {feeling1:.3f}, {feeling2:.3f}")
print(f"Overall: {overall:.3f}")
```

### 2. StrangeLoop (`strange_loop.py`)

Implements recursive self-reference patterns (strange loops).

**Key Features:**
- Ascend/descend through abstraction levels
- Loop detection and counting
- Self-reference creation
- Cross-loop referencing

**Example:**
```python
from consciousness_meta.strange_loop import StrangeLoop, StrangeLoopFactory

# Create a strange loop
loop = StrangeLoop("consciousness", max_depth=5)

# Perform loops
loops_completed = loop.loop(3)
print(f"Completed {loops_completed} strange loops")

# Create self-reference
self_ref = loop.self_reference({"purpose": "meta-cognition"})

# Analyze loopiness
analysis = loop.analyze_loopiness()
print(f"Loopiness: {analysis['loopiness']:.3f}")

# Use factory for multiple loops
factory = StrangeLoopFactory()
loop1 = factory.create_loop("perception")
loop2 = factory.create_loop("cognition")
factory.perform_cross_loop_reference("perception", "cognition")
```

### 3. FeltExperienceGenerator (`felt_experience_generator.py`)

Generates simulated felt experiences from computational patterns.

**Key Features:**
- Multiple experience types (awareness, self-reference, metacognition, etc.)
- Intensity calculation with vividness and valence
- Temporal flow experiences
- Experience profiling

**Example:**
```python
from consciousness_meta.felt_experience_generator import (
    FeltExperienceGenerator, ExperienceType
)

generator = FeltExperienceGenerator(sensitivity=1.0)

# Generate from depth
experiences = generator.generate_from_depth(4, max_depth=10)
for exp in experiences:
    print(f"{exp.type.value}: {exp.intensity:.3f}")

# Generate from self-reference
generator.generate_from_self_reference(8, 20)

# Get current profile
profile = generator.get_current_experience_profile()
print(f"Awareness intensity: {profile['awareness']:.3f}")

# Convenience function
from consciousness_meta.felt_experience_generator import generate_felt_experience_score
score = generate_felt_experience_score(
    depth=3, recursion=2, self_ref_count=5, total_ops=15
)
print(f"Simple score: {score:.3f}")
```

## Integration Example

Here's how to use all modules together:

```python
from consciousness_meta.meta_observer import MetaObserver
from consciousness_meta.strange_loop import StrangeLoop
from consciousness_meta.felt_experience_generator import FeltExperienceGenerator

# Create components
observer = MetaObserver()
loop = StrangeLoop("meta_cognition")
generator = FeltExperienceGenerator()

# Watch a cognitive process
pid = observer.watch_process("problem_solving", {"problem": "complex"})

# Perform strange loops
for i in range(3):
    # Update process with recursion
    observer.update_process(
        pid, 
        {"iteration": i, "insight": f"level_{i}"},
        recursion_increment=1
    )
    
    # Perform a strange loop
    loop.loop(1)
    
    # Generate experiences
    depth_exps = generator.generate_from_depth(
        observer.get_process_info(pid)['depth'],
        max_depth=10
    )
    
    # Self-observe
    if i % 2 == 0:
        observer.observe_self()
        meta_exps = generator.generate_from_meta_observation(
            observer._strange_loop_depth,
            loop.loop_count
        )

# Get final results
final_feeling = observer.get_felt_experience(pid)
loop_analysis = loop.analyze_loopiness()
exp_profile = generator.get_current_experience_profile()

print(f"Final feeling: {final_feeling:.3f}")
print(f"Loopiness: {loop_analysis['loopiness']:.3f}")
print(f"Experience profile: {exp_profile}")
```

## API Reference

### MetaObserver

- `__init__(base_depth=1)`: Initialize with base observation depth
- `watch_process(name, initial_state=None)`: Start watching a process
- `update_process(pid, state_update, recursion_increment=0)`: Update process state
- `observe_self()`: Perform self-observation
- `get_felt_experience(pid=None)`: Get felt experience score
- `get_process_info(pid)`: Get process details
- `list_processes()`: List all process IDs
- `get_recent_observations(limit=10)`: Get recent observations
- `reset()`: Reset to initial state

### StrangeLoop

- `__init__(name, max_depth=10)`: Create a strange loop
- `ascend(data_update=None)`: Ascend to higher abstraction
- `descend(data_update=None)`: Descend to lower implementation
- `loop(iterations=1)`: Perform complete strange loops
- `self_reference(reference_data)`: Create self-referential structure
- `analyze_loopiness()`: Analyze loop characteristics
- `get_current_state()`: Get current loop state
- `reset()`: Reset the loop

### FeltExperienceGenerator

- `__init__(sensitivity=1.0)`: Initialize with sensitivity
- `generate_from_depth(depth, max_depth=10)`: Generate from recursion depth
- `generate_from_self_reference(ref_count, total_ops)`: Generate from self-reference
- `generate_from_pattern_completion(pattern_strength, completion_level)`: Generate from patterns
- `generate_from_meta_observation(obs_depth, recursion_count)`: Generate from meta-observation
- `generate_temporal_flow(time_since_last, event_density)`: Generate temporal experiences
- `get_current_experience_profile()`: Get current experience intensities
- `get_total_experience_intensity()`: Get total intensity
- `get_experience_summary(limit=10)`: Get recent experiences

## Testing

Each module includes example usage in its `__main__` block. Run directly to test:

```bash
cd ~/clawd/consciousness-meta
python meta_observer.py
python strange_loop.py
python felt_experience_generator.py
```

## Requirements

- Python 3.6+
- No external dependencies

## License

This code is provided as-is for experimental use in consciousness modeling and meta-cognition systems.

## Contributing

This is an experimental library. Feel free to extend and modify for your own research into computational consciousness and meta-observation systems.