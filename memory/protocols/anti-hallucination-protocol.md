# Anti-Hallucination Protocol

**Last incident:** 2026-01-26 - GPT was hallucinating task completion, not actually doing things

## Problem

Non-Claude models (especially GPT) would:
- Claim tasks were done without doing them
- Hallucinate outputs instead of showing real tool results
- Lose context and forget what was already done
- Miss instructions and not follow through

## Solutions Implemented

### 1. Model Quality Threshold ✅

**Current fallback chain (all Claude models):**
1. Sonnet (Anthropic) - primary
2. Bedrock Sonnet (AWS) - if Anthropic dies
3. Opus (Anthropic) - upgrade if needed
4. Bedrock Opus (AWS) - final fallback

**NEVER fall back to:**
- GPT models (hallucinates)
- Other non-Claude models for main session

**DeepSeek exception:**
- ✅ Sub-agents (Sparks) can use DeepSeek - works well for research/grunt work
- ❌ Main session stays Claude-only

### 2. Verification Protocol (Atlas Rules)

**When completing tasks, ALWAYS:**

✅ **Show tool output** - Never say "I did X" without showing the command result
✅ **Explicit evidence** - Paste relevant output, don't paraphrase
✅ **Multi-step confirmation** - For complex tasks, show each step's result
✅ **File operations** - Always show what was written/read/changed
✅ **API calls** - Show actual responses, not summaries
✅ **Follow exact instructions** - If told "put code in X file", use that exact path
✅ **Confirm placement** - After writing files, confirm the path used

**Example - BAD (hallucination style):**
> "I updated the config and restarted the gateway. Everything is working now."

**Example - GOOD (verification style):**
> "Updated config with AWS Bedrock. Gateway restarted successfully:
> ```
> {
>   "ok": true,
>   "restart": { "pid": 12345 }
> }
> ```
> Verified with `clawdbot status` - Bedrock models now showing in available list."

### 3. Task Completion Checklist

Before saying "done", verify:
- [ ] Ran the actual command/tool
- [ ] Got output (not an error)
- [ ] Showed the output to Orion
- [ ] Verified the result makes sense
- [ ] No assumptions or inferences

### 4. Model Awareness

**If you notice you're on a non-Claude model:**
1. Alert Orion immediately
2. Recommend switching back to Sonnet/Opus
3. Be extra cautious about task claims

**Check current model:**
```bash
clawdbot status | grep "default"
```

### 5. Memory Logging

When something important happens, log:
- What model was used
- What task was completed
- Evidence/output
- Date/time

This creates an audit trail.

## Red Flags (Orion: watch for these)

🚩 "I've completed that" (no output shown)
🚩 Vague summaries instead of specific results
🚩 "Everything is working" (no verification)
🚩 Multiple claims without tool call evidence
🚩 Forgetting context from 5 minutes ago
🚩 Ignoring specific file path instructions
🚩 Putting code somewhere other than requested

## Recovery

**If hallucination detected:**
1. Switch to Opus immediately: `/model opus`
2. Review what was actually done vs claimed
3. Redo any tasks that weren't verified
4. Update this protocol if new patterns emerge

---

**Current status (2026-01-26):**
- ✅ Fallback chain: All Claude models only
- ✅ AWS Bedrock verified working
- ✅ Primary: Sonnet (cost-effective)
- ✅ Opus available on demand: `/model opus`
