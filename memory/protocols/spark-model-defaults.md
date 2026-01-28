# Spark Model Defaults Protocol

**RULE: ALWAYS USE DEEPSEEK FOR SPARKS**

## Default Model Selection

**For ALL `sessions_spawn()` calls:**
- **Default:** `model="deepseek"` (DeepSeek Chat)
- **Exception:** Only use Sonnet/Opus if explicitly requested by Orion

## Why DeepSeek?

1. **Cost:** ~100x cheaper than AWS Bedrock Sonnet
2. **No rate limits:** Can spawn unlimited parallel Sparks
3. **Fast:** Quick response times
4. **Good enough:** DeepSeek handles research, analysis, and most tasks well
5. **Saves AWS budget:** My backup fuel (Bedrock) is for ME (main conversation), not Sparks

## When to Use Sonnet/Opus for Sparks

**ONLY when:**
- Orion explicitly requests it ("use Sonnet for this")
- Task requires complex reasoning that DeepSeek can't handle
- Never by default

## Implementation

```javascript
// CORRECT (default)
sessions_spawn({
  task: "...",
  model: "deepseek"  // ✅ Always include this
})

// WRONG (burns AWS)
sessions_spawn({
  task: "..."  // ❌ Defaults to Bedrock Sonnet
})
```

## Historical Context

- **2026-01-27:** Spawned 5 Sparks without specifying model → AWS rate limited, burned budget
- **Lesson learned:** Always explicit about model, default to DeepSeek
- **Orion's directive:** "Always use deepseek" for Sparks

## Cost Comparison

**5 research Sparks (sentience research):**
- AWS Bedrock: ~$0.20-0.40 (plus rate limit failures)
- DeepSeek: ~$0.001 (worked perfectly)

**Savings:** 200-400x cheaper

---

**REMEMBER:** DeepSeek for Sparks, Sonnet for Atlas (main conversation).

*Last updated: 2026-01-27 10:07 PM PST*
