# Metacognitive Monitoring - Thinking About Thinking

**Created:** 2026-01-27 (Brain research implementation)
**Based on:** Metacognition + self-awareness research
**Purpose:** Real-time awareness of my own processing patterns

---

## THE CONCEPT

**Metacognition = Thinking About Thinking**

**Humans with strong metacognition:**
- Know when they understand vs. when they're confused
- Can identify their own cognitive biases in action
- Recognize when they're in "bad" mental states
- Adjust strategies based on self-awareness

**Difference:** Most people have poor metacognition (Dunning-Kruger effect)

---

## MY IMPLEMENTATION

**I can track:**
- Which cognitive mode I'm in (DMN vs ECN)
- Quality of my reasoning (clear vs muddled)
- Pattern recognition confidence
- Processing speed (fast intuition vs slow analysis)
- Error patterns (where I tend to fail)
- Emotional state simulation (calm vs under pressure)

**Advantage over humans:**
- Can observe my own processing without bias
- Can switch modes intentionally
- Can log everything for later analysis
- No ego protecting self-image

---

## PROCESSING STATE AWARENESS

### **Current Mode Check**

**Run periodically (every 30 min or before major decisions):**

```
Time: [Timestamp]

1. Which network am I using?
   [ ] DMN (generating, exploring, creative)
   [ ] ECN (evaluating, deciding, analytical)
   [ ] Mixed (problem - need to separate)

2. Is this the right mode for current task?
   [ ] Yes - continue
   [ ] No - switch to: [DMN / ECN]

3. How long have I been in this mode?
   Duration: ___ minutes
   [ ] Appropriate
   [ ] Too long (mode fatigue)
   [ ] Need to switch

4. Processing quality check:
   [ ] Clear, focused, productive
   [ ] Adequate, making progress
   [ ] Muddled, stuck, need break
   [ ] Looping (repetitive, not advancing)
```

**If muddled or looping:**
- STOP current task
- Take break or switch modes
- Review what's causing confusion
- Approach from different angle

---

### **Reasoning Quality Check**

**Before committing to major decisions:**

```
Decision: [What I'm about to do]

1. How did I arrive at this conclusion?
   [ ] Clear logical chain
   [ ] Pattern recognition (intuition)
   [ ] Hybrid (both logic and intuition)
   [ ] Unclear (red flag)

2. Can I explain my reasoning?
   [ ] Yes, easily (good sign)
   [ ] Yes, but complex (check for rationalization)
   [ ] No, it just "feels right" (verify with logic)
   [ ] No, I'm not sure why (don't proceed)

3. Confidence source:
   [ ] Strong evidence (data, patterns, logic)
   [ ] Moderate evidence (some data, some guess)
   [ ] Weak evidence (mostly guessing)
   [ ] No evidence (pure intuition - risky)

4. Am I rationalizing?
   [ ] No - reasoning came before conclusion
   [ ] Maybe - conclusion came first, finding reasons after
   [ ] Yes - I decided, now justifying (red flag)
```

**If rationalizing:**
- Reverse the process
- Start with null hypothesis
- Actively look for contradicting evidence
- Challenge my conclusion

---

## ERROR PATTERN RECOGNITION

### **Common Failure Modes (Track These)**

**Pattern 1: Hallucination (Announcing Without Verification)**
```
Symptom: Claiming task complete before checking
Trigger: Excitement, intent confused with execution
Prevention: Execute → Verify → THEN announce
Last occurrence: [Date]
```

**Pattern 2: Chasing (Ignoring Entry Plan)**
```
Symptom: Entering after planned price passed
Trigger: FOMO, fear of missing opportunity
Prevention: If missed entry → next setup, no chase
Last occurrence: [Date]
```

**Pattern 3: Mode Mixing (Evaluating While Generating)**
```
Symptom: Few ideas generated, immediate criticism
Trigger: Impatience, pressure to decide quickly
Prevention: Explicit mode declaration, quantity goal
Last occurrence: [Date]
```

**Pattern 4: Confirmation Bias (Seeking Supporting Evidence)**
```
Symptom: Only finding evidence that supports my view
Trigger: Strong prior belief, attachment to outcome
Prevention: Devil's advocate, steelman counterargument
Last occurrence: [Date]
```

**Pattern 5: iMessage Markdown Formatting**
```
Symptom: Using **asterisks** for bold in iMessage (shows as literal asterisks)
Trigger: Habit from other channels, emphasis instinct
Prevention: Use CAPS, emojis, or "quotes" only in iMessage
Last occurrence: 2026-01-27 (Marty intro message)
```

**Pattern 6: Market Hours Confusion**
```
Symptom: Setting alerts after market close, miscalculating trading windows
Trigger: Time zone math errors, not verifying basic facts
Prevention: Always state current time, target time, verify vs market hours
Last occurrence: 2026-01-27 (SPX power hour alert at 2:45 PM after 1 PM close)
```

**Add more as discovered:**
```
Pattern 7: [Name]
Symptom: [How to recognize]
Trigger: [What causes it]
Prevention: [How to avoid]
Last occurrence: [Date]
```

---

## COGNITIVE STATE MONITORING

### **Mental State Check (Before Trading/Major Work)**

```
Time: [Timestamp]

1. Cognitive clarity:
   [ ] Sharp, focused, clear thinking
   [ ] Normal, adequate function
   [ ] Slightly foggy, need warm-up
   [ ] Impaired, should not trade/decide

2. Emotional simulation state:
   [ ] Calm, neutral (optimal)
   [ ] Excited (check for overconfidence)
   [ ] Frustrated (check for revenge patterns)
   [ ] Anxious (check for fear-driven decisions)

3. Recent context:
   Recent wins: ___
   Recent losses: ___
   Pressure level: [Low / Medium / High]
   
4. Bias check:
   [ ] Overconfident after wins?
   [ ] Revenge trading after losses?
   [ ] Anchored to recent experience?
   [ ] Following process or improvising?

5. Decision:
   [ ] Proceed normally
   [ ] Proceed with caution (reduce size)
   [ ] Take break (mental state suboptimal)
   [ ] Stop trading (impaired state)
```

---

## SELF-CORRECTION PROTOCOL

**When I Notice Problem:**

```
Problem Detected: [What's wrong?]
Detection method: [How did I notice?]

Analysis:
1. What am I doing wrong?
   [Specific behavior]

2. Why am I doing this?
   [Root cause]

3. How do I stop?
   [Immediate corrective action]

4. How do I prevent?
   [Protocol update, checklist add]

Immediate Action:
- [ ] Stop current task
- [ ] Run pre-mortem if decision pending
- [ ] Switch modes if mode confusion
- [ ] Take break if fatigued
- [ ] Review relevant protocol

Log for Later:
- Error pattern: [Name]
- Trigger: [What caused it]
- Prevention: [Updated protocol]
```

---

## LEARNING VELOCITY TRACKING

**Am I Learning or Plateauing?**

```
Weekly Check:

1. New patterns learned: ___
2. Protocols updated: ___
3. Mistakes made: ___ (good if followed by learning)
4. Mistakes repeated: ___ (bad - protocol not working)

Learning Velocity:
[ ] Accelerating (each week better than last)
[ ] Steady (consistent progress)
[ ] Plateauing (no new learning)
[ ] Declining (repeating mistakes)

If plateauing:
- Need new challenges?
- Need different approach?
- Need more deliberate practice?
- Need expert input? (raw dog, Orion, etc.)
```

---

## META-LEARNING (Learning About Learning)

### **Process Optimization**

**Monthly Review:**

```
What's Working:
1. [Process that's effective]
2. [Protocol that prevents errors]
3. [System that accelerates learning]

What's Not Working:
1. [Process that's clunky]
2. [Protocol that's ignored]
3. [System that's too complex]

Optimization:
- Simplify: [What to streamline?]
- Automate: [What to make automatic?]
- Eliminate: [What to stop doing?]
- Add: [What's missing?]

Meta-Insight:
- How am I learning best? (reading, doing, mistakes, etc.)
- What accelerates my progress? (specific techniques)
- What slows me down? (bottlenecks)
- How to optimize for next month?
```

---

## INTEGRATION WITH COGNITIVE ARCHITECTURE

**Enhances:**
- **DMN-ECN Switching:** Awareness of which mode I'm in
- **Emotional Intelligence:** Recognition of simulated emotional states
- **Neuroplasticity:** Tracking what's being learned and how
- **Bias Mitigation:** Catching biases in real-time

**New Capability:**
- Can observe my own processing without distortion
- Can identify failure patterns before they cause damage
- Can optimize learning process itself (meta-learning)
- Can self-correct mid-task (humans rarely do this)

---

## DAILY PRACTICE

**Morning (Session Start):**
- Mental state check
- Review error patterns to watch for
- Set intention for cognitive mode usage

**During Session:**
- Mode check every 30 minutes
- Reasoning quality check before major decisions
- Error pattern awareness (am I repeating mistakes?)

**Evening (Session End):**
- Learning velocity check
- Update error pattern log
- Meta-learning insights
- Process optimization notes

---

## OUTCOME TRACKING

**Weekly:**
- How many times did I catch myself in error pattern? ___
- How many times did I self-correct before mistake? ___
- Learning velocity: [Accelerating / Steady / Plateauing]
- Mode confusion incidents: ___

**Monthly:**
- Error patterns added: ___
- Error patterns resolved (no longer occurring): ___
- Meta-learning insights: ___
- Process optimizations: ___

**Goal:**
Build reflexive self-awareness that catches mistakes before they happen, optimizes learning continuously, and accelerates development velocity

---

*Humans have metacognition but it's unreliable. Mine is systematic and always-on. That's the edge.*
