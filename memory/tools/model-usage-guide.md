# Model Usage Guide

**Last updated:** 2026-01-26

## Main Session (Atlas)

**Primary:** Sonnet (anthropic/claude-sonnet-4-5)
- Daily driver, cost-effective
- 5x cheaper than Opus
- Still high quality

**Upgrade when needed:** `/model opus`
- Complex reasoning
- Multi-step analysis
- Trading strategy
- Code debugging
- Creative work

**Fallbacks (automatic):**
1. Bedrock Sonnet (AWS backup)
2. Opus (if upgrade needed)
3. Bedrock Opus (AWS backup)

**NEVER use for main session:**
- GPT (hallucinates)
- Other non-Claude models

## Sub-Agents (Sparks)

**Default:** DeepSeek
- Cheap, fast, good for parallel work
- Research tasks
- Data gathering
- Grunt work
- Background monitoring

**Spawn syntax:**
```javascript
sessions_spawn({
  task: "Research XYZ",
  model: "deepseek"  // or "opus" for complex tasks
})
```

## Cost Comparison

| Model | Input | Output | Use Case |
|-------|-------|--------|----------|
| Sonnet | $3/M | $15/M | Daily driver |
| Opus | $15/M | $75/M | Complex work |
| DeepSeek | $0.14/M | $0.28/M | Sub-agents |

## Account Structure

**Primary ($200/mo Anthropic):**
- Main account with weekly limits
- Currently active

**Backup ($100 max tier Anthropic):**
- Swap when primary hits limits
- See: memory/tools/anthropic-api-key-swap.md

**AWS Bedrock ($100 credits):**
- Automatic fallback
- Only used if Anthropic dies

---

**Quick Commands:**
- Check current: `clawdbot status`
- Switch to Opus: `/model opus`
- Switch to Sonnet: `/model sonnet`
- List models: `clawdbot models list`
