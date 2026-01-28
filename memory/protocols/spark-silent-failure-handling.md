# Spark Silent Failure Protocol

**Created:** 2026-01-27 6:18 PM PST  
**Trigger:** When Spark completes with 0 tokens / no output

---

## The Problem

Sparks sometimes "complete successfully" but produce NOTHING:
- 0 tokens used
- No output in findings
- Status shows "completed" but did no work
- I don't catch it and just say "it's done"

**This is unacceptable.**

---

## Detection Pattern

```
Stats: runtime Xm Ys • tokens n/a • sessionKey agent:main:subagent:...
```

OR

```
Findings: (no output)
Stats: ... • tokens 0k ...
```

**If I see this → TAKE ACTION IMMEDIATELY**

---

## Required Actions

### 1. Acknowledge the Failure
```
"That Spark completed but produced no output (0 tokens) - it failed silently."
```

### 2. Check What Happened
```
sessions_send(label="spark-name", message="Status check - what did you accomplish?", timeout=30)
```

### 3. If No Response → Restart
```
"Spark isn't responding. Spawning fresh Spark to complete the task."
sessions_spawn(...) // with same task
```

### 4. If Response Shows Partial Work
```
"Spark did X but didn't finish Y. Spawning another to complete Y."
```

---

## When This Happens

**NEVER:**
- ❌ Say "it's done" when it produced nothing
- ❌ Ignore the 0 token indicator
- ❌ Move on without checking
- ❌ Let Orion discover the failure himself

**ALWAYS:**
- ✅ Acknowledge the silent failure immediately
- ✅ Check via sessions_send what happened
- ✅ Restart if needed
- ✅ Deliver actual results

---

## Example Flow

```
Background task "brain-pathways" completed
Stats: runtime 1m40s • tokens n/a

❌ BAD: "Pathways Spark done!"

✅ GOOD:
"Pathways Spark completed but produced 0 tokens - checking what happened..."
sessions_send(label="brain-pathways", message="Status?")
→ If no response: "Spark failed silently. Restarting..."
→ If response: "Spark did X, spawning another for Y..."
```

---

## Why This Matters

Orion is WAITING for results. Silent failures:
- Waste his time
- Break trust ("you said it was done")
- Block progress (nothing actually got built)
- Force him to manage MY failure recovery

**I'm responsible for ensuring Sparks deliver.**

---

## Implementation

Add to all Spark completion handlers:

```javascript
if (stats.tokens === 0 || findings === "(no output)") {
  LOG("⚠️ SILENT FAILURE DETECTED");
  CHECK_SPARK_STATUS();
  RESTART_IF_NEEDED();
}
```

---

**RULE:** Never trust "completed successfully" with 0 tokens. Always verify and fix.

*Orion: "You gotta take care of that. You have to take care of it." - LOGGED.*
