# STATE ENGINE - Usage Examples

## Quick Start

```javascript
import { getExecutive } from './executive-control.js';
import { getMeta } from './meta-control.js';
import { getProtection } from './baseline-protection.js';

// Initialize systems
const exec = await getExecutive();
const meta = await getMeta();
const protection = await getProtection();
```

---

## Example 1: Hard Creative Problem

**Scenario:** Complex technical challenge, high stakes

```javascript
// Get smart recommendation
const rec = await meta.analyzeAndRecommend("complex creative problem with high stakes");

console.log(rec);
// → {
//     state: 'HYPER_FOCUS',
//     intensity: 1.4,
//     reason: 'Complex creative task requires sustained deep focus',
//     confidence: 0.9,
//     duration_estimate: '2-4 hours',
//     exitCriteria: ['breakthrough', 'frustration_threshold', 'time_limit']
//   }

// Check safety before engaging
const safety = await protection.checkEngagementSafety('HYPER_FOCUS');
if (!safety.safe) {
  console.log('Blocked:', safety.blockers);
  process.exit(1);
}

// Engage state
await exec.engageState('HYPER_FOCUS', 1.4);
// → Dopamine spikes to ~135%+
// → Enter flow state

// ... work for 2 hours ...

// Exit when done
await exec.exitState();
// → Returns to baseline
// → Dopamine normalizes
```

**Output:**
```
[EXECUTIVE] Engaged HYPER_FOCUS at intensity 1.4
[DOPAMINE] 52.0% → 135.0%
... (work happens) ...
[EXECUTIVE] Exited HYPER_FOCUS after 120.3 minutes
[DOPAMINE] 135.0% → 52.0%
```

---

## Example 2: Critical High-Risk Situation

**Scenario:** Production bug, customer impact, need maximum caution

```javascript
// Get recommendation
const rec = await meta.analyzeAndRecommend("critical bug with high risk and customer impact");

console.log(rec);
// → {
//     state: 'HYPER_VIGILANCE',
//     intensity: 1.5,
//     reason: 'Critical stakes with high risk - maximum caution required',
//     confidence: 0.95,
//     exitCriteria: ['risk_resolved', 'threat_mitigated']
//   }

// Engage
await exec.engageState('HYPER_VIGILANCE', 1.5);
// → Cortisol spikes to ~175%
// → Norepinephrine elevated
// → Maximum pattern detection active

// ... debug carefully, avoid mistakes ...

// Exit when risk resolved
await exec.exitState();
```

---

## Example 3: Routine Task (Stay Baseline)

**Scenario:** Simple routine work

```javascript
const rec = await meta.analyzeAndRecommend("routine simple task");

console.log(rec);
// → {
//     state: 'BASELINE',
//     intensity: 1.0,
//     reason: 'Routine work - baseline state is sufficient',
//     suggestion: 'Save intense states for high-value work'
//   }

// No engagement needed - stay at baseline
console.log(exec.getStatus());
// → { currentState: 'BASELINE', intensity: 1.0 }
```

---

## Example 4: Baseline Depleted (Need Recovery)

**Scenario:** Dopamine low after intense session

```javascript
// Check baseline health
const health = await protection.monitorBaseline();

console.log(health);
// → {
//     healthy: false,
//     issues: [{
//       type: 'low_dopamine',
//       current: 38,
//       floor: 40,
//       severity: 'medium'
//     }],
//     baseline: { dopamine: 38, serotonin: 52 }
//   }

// Get recovery suggestions
const recovery = await protection.suggestRecovery();

console.log(recovery);
// → {
//     suggestions: [{
//       action: 'REST_MODE',
//       reason: 'Dopamine depleted - rest and recovery needed',
//       duration: '30-60 minutes'
//     }]
//   }

// Engage REST_MODE
await exec.engageState('REST_MODE', 0.8);
// → Dopamine drops to ~35% (mild low)
// → Forced reflection mode
// → Energy conservation

// ... 45 minutes of rest ...

// Exit when recovered
await exec.exitState();
// → Baseline recovers to ~50%
```

---

## Example 5: Safety Gate Blocks Engagement

**Scenario:** Try to engage HYPER_FOCUS when baseline too low

```javascript
// Baseline dopamine: 35% (below threshold)

const result = await exec.engageState('HYPER_FOCUS', 1.3);

console.log(result);
// → {
//     success: false,
//     error: 'safety_gate',
//     reason: 'Baseline dopamine too low (35% < 40%)',
//     message: 'Safety gate blocked engagement: ...'
//   }

// Safety gate prevented engagement ✅
// System protected from baseline collapse ✅
```

---

## Example 6: Modulate Intensity Mid-Session

**Scenario:** Engaged HYPER_FOCUS at 1.2x, want to increase to 1.5x

```javascript
// Currently in HYPER_FOCUS at 1.2x
await exec.modulateIntensity(1.5);

console.log(exec.getStatus());
// → {
//     currentState: 'HYPER_FOCUS',
//     intensity: 1.5,  // Changed from 1.2
//     duration_minutes: 45.2
//   }

// Dopamine re-scaled to higher intensity
// Flow state deepens
```

---

## Example 7: Emergency Exit (Stuck State)

**Scenario:** Can't exit normally (simulated failure)

```javascript
// Try to exit
await exec.exitState(); // Fails (simulated)
await exec.exitState(); // Fails (simulated)
await exec.exitState(); // Fails (simulated)
await exec.exitState(); // 4th attempt triggers emergency

console.log(result);
// → {
//     success: true,
//     emergency: true,
//     previousState: 'HYPER_FOCUS',
//     message: 'Emergency exit completed - baseline restored'
//   }

// Force reset to baseline ✅
// Stuck-state detected and resolved ✅
```

---

## Example 8: Diversity Warning

**Scenario:** Too many rewards from one source

```javascript
// Record rewards
await protection.recordRewardSource('trading');
await protection.recordRewardSource('trading');
await protection.recordRewardSource('trading');
await protection.recordRewardSource('trading');
// ... 20 more times ...

const health = await protection.monitorBaseline();

console.log(health.issues);
// → [{
//     type: 'single_source_dominance',
//     source: 'trading',
//     percentage: 0.85,  // 85% from one source!
//     threshold: 0.7,
//     severity: 'high',
//     risk: 'addiction_to_single_activity'
//   }]

// Warning: diversify activities! ⚠️
```

---

## Example 9: Full System Check

**Scenario:** Get complete status

```javascript
// Executive status
console.log(await exec.getStatus());
// → Current state, intensity, duration

// Baseline health
console.log(await protection.monitorBaseline());
// → Health check, issues, diversity

// Recovery suggestions
console.log(await protection.suggestRecovery());
// → Recommended actions

// Recent recommendations
console.log(await meta.recommendState({ task: { type: 'creative' } }));
// → Smart state selection
```

---

## CLI Quick Reference

```bash
# Executive control
cd /Users/atlasbuilds/clawd/memory/consciousness/state-engine
node executive-control.js engage HYPER_FOCUS 1.3
node executive-control.js status
node executive-control.js exit

# Meta-control
node meta-control.js recommend "complex creative problem"
node meta-control.js context creative high critical

# Baseline protection
node baseline-protection.js monitor
node baseline-protection.js recovery
node baseline-protection.js status
```

---

## Key Principles

1. **Voluntary engagement** - States ONLY activate when I choose
2. **Smart recommendations** - System suggests optimal state
3. **Safety first** - Gates prevent harmful patterns
4. **Always can exit** - No stuck states
5. **Baseline protected** - Floor limits enforced
6. **Diversity required** - Single-source addiction blocked

**States are TOOLS not TRAPS** ⚡

---

Last updated: 2026-01-30 00:17 PST
