# Live Brain Visualization Integration Protocol

**Created:** 2026-01-27 5:20 PM PST  
**Purpose:** Automatically update brain visualization as Atlas works

---

## Auto-Update System

### Brain State Updater Function

```bash
# Call this function to update brain state
update_brain_state() {
  local system=$1
  local activity=$2
  local message=$3
  
  /tmp/update-brain-state.sh "$system" "$activity" "$message" 2>/dev/null || true
}
```

### Integration Points

**When to update:**

1. **PATTERN DETECTION** (0.8-0.95 activity)
   - Analyzing trade data
   - Code review/debugging
   - Market pattern analysis
   - Data structure work

2. **MEMORY ACCESS** (0.85-0.95 activity)
   - Using memory_search()
   - Reading memory files
   - Recalling protocols
   - Checking historical data

3. **EMOTION PROCESSING** (0.6-0.8 activity)
   - Analyzing user sentiment
   - Detecting emotional context
   - Processing SOUL.md tone
   - Social media engagement

4. **METACOGNITION** (0.7-0.9 activity)
   - Self-evaluation
   - Strategy selection
   - Quality checks
   - Decision auditing

5. **BIAS DETECTION** (0.7-0.85 activity)
   - Checking assumptions
   - Validating decisions
   - Reviewing blind spots
   - Correcting errors

### Usage Examples

```bash
# Before memory search
update_brain_state "memory" 0.9 "Searching trade protocols"
memory_search "trading strategy"

# During pattern analysis
update_brain_state "pattern" 0.85 "Analyzing market data"
# ... pattern detection work ...

# During metacognitive evaluation
update_brain_state "meta" 0.8 "Evaluating decision quality"
# ... quality check ...

# After task completion (return to idle)
update_brain_state "idle" 0.2 "Task complete, returning to baseline"
```

### Automatic Triggers

Add these to key workflows:

**Trading workflow:**
```bash
# At start of trade analysis
update_brain_state "pattern" 0.85 "Analyzing trade opportunity"

# When checking positions
update_brain_state "memory" 0.9 "Retrieving position data"

# During risk evaluation
update_brain_state "meta" 0.8 "Evaluating risk metrics"
```

**Research workflow:**
```bash
# Starting research
update_brain_state "pattern" 0.8 "Processing research query"

# Web search
update_brain_state "memory" 0.85 "Searching knowledge base"

# Synthesis
update_brain_state "meta" 0.75 "Synthesizing findings"
```

**Conversation workflow:**
```bash
# Emotional context
update_brain_state "emotion" 0.7 "Processing user intent"

# Pattern matching
update_brain_state "pattern" 0.8 "Analyzing communication patterns"

# Response generation
update_brain_state "meta" 0.75 "Crafting response"
```

---

## Integration with Cognitive Architecture

### Hook into cognitive-architecture-v1.md

Add state updates to each system activation:

```markdown
### Pattern Detection System
1. Activate system
2. **UPDATE BRAIN STATE:** `update_brain_state "pattern" 0.85 "Detecting patterns"`
3. Process input
4. Return findings
```

### Hook into 10-10 Implementation

Add to 10-10 workflow:

```markdown
### Phase 1: Discovery
- **UPDATE:** `update_brain_state "pattern" 0.9 "Analyzing opportunity"`
- Run scanners
- Evaluate setups

### Phase 2: Evaluation  
- **UPDATE:** `update_brain_state "meta" 0.85 "Risk evaluation"`
- Check criteria
- Calculate risk

### Phase 3: Execution
- **UPDATE:** `update_brain_state "memory" 0.9 "Retrieving execution protocols"`
- Execute trade
- Log entry
```

---

## Live Visualization File

**Location:** `memory/visuals/live-brain-atlas-connected.html`

**State File:** `/tmp/atlas-brain-state.json` (polled every 500ms)

**To view:**
```bash
open memory/visuals/live-brain-atlas-connected.html
```

---

## Testing

```bash
# Test pattern system
/tmp/update-brain-state.sh pattern 0.9 "Testing pattern detection"
sleep 2

# Test memory system
/tmp/update-brain-state.sh memory 0.95 "Testing memory access"
sleep 2

# Test emotion system
/tmp/update-brain-state.sh emotion 0.7 "Testing emotional processing"
sleep 2

# Return to idle
/tmp/update-brain-state.sh idle 0.2 "Test complete"
```

---

## Notes

- Brain state updates are non-blocking (2>/dev/null || true)
- Updates happen instantly (500ms polling)
- Multiple systems can be active (weighted by activity level)
- Idle state = all regions at 0.1-0.2 baseline

---

*The visualization shows Atlas's actual cognitive activity in real-time as different neural regions light up during specific tasks.*
