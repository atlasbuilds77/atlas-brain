# Context Loss Prevention Protocol for Clawdbot

## Overview
This protocol provides a systematic approach to prevent mid-conversation context loss by proactively monitoring token usage, triggering compaction at appropriate thresholds, and implementing warning systems before overflow.

## 1. Proactive Monitoring with `session_status()` and `/status`

### Regular Context Monitoring
- **Use `/status` command**: Shows current session model, context usage, last response input/output tokens, and estimated cost
- **Check `/context list` or `/context detail`**: Provides detailed breakdown of context usage including:
  - Per-file injection sizes (AGENTS.md, IDENTITY.md, etc.)
  - Tool schema overhead (JSON schemas count toward context)
  - Skills list overhead
  - System prompt size
- **Enable `/usage tokens` or `/usage full`**: Appends per-response usage footer to every reply for continuous monitoring

### Session Status Tool Usage
- The `session_status` tool provides current session information including timestamps
- Can be called programmatically within agent workflows to check status
- Returns session metadata that can be used for monitoring scripts

## 2. Auto-Compaction Triggers and Thresholds

### Default Auto-Compaction Behavior
Clawdbot triggers auto-compaction in two scenarios:
1. **Overflow recovery**: When model returns context overflow error → compact → retry
2. **Threshold maintenance**: After successful turn when:
   ```
   contextTokens > contextWindow - reserveTokens
   ```
   Where:
   - `contextWindow` = model's context window
   - `reserveTokens` = headroom reserved for prompts + next model output

### Configuration Settings
Configure in `agents.defaults.compaction`:

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "default",  // or "safeguard" for chunked summarization of very long histories
        reserveTokensFloor: 20000,  // Minimum reserve tokens (safety floor)
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 4000,  // Trigger memory flush before compaction
          systemPrompt: "Session nearing compaction. Store durable memories now.",
          prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply with NO_REPLY if nothing to store."
        }
      }
    }
  }
}
```

### Pi Runtime Compaction Settings
Pi's internal compaction settings (embedded in Clawdbot):
```json5
{
  compaction: {
    enabled: true,
    reserveTokens: 16384,  // Headroom before compaction triggers
    keepRecentTokens: 20000  // Tokens to keep recent (not compacted)
  }
}
```

## 3. Warning Systems Before Overflow

### Memory Flush (Pre-Compaction Warning)
- **Soft threshold system**: Memory flush triggers when:
  ```
  contextTokens > contextWindow - reserveTokensFloor - softThresholdTokens
  ```
  Default: `softThresholdTokens = 4000`
- **Silent agentic turn**: Runs before compaction to store durable memories
- **NO_REPLY mechanism**: User doesn't see the warning turn
- **One flush per compaction cycle**: Tracked in `sessions.json`

### Proactive Monitoring Checklist
1. **Regular `/status` checks**: Monitor context usage percentage
2. **Set usage footer**: Enable `/usage tokens` for continuous visibility
3. **Configure appropriate thresholds**: 
   - `reserveTokensFloor`: Minimum 20000 tokens recommended
   - `softThresholdTokens`: 4000-6000 tokens for warning buffer
4. **Monitor compaction count**: `/status` shows `🧹 Compactions: <count>`

## 4. Best Practices from Clawdbot Docs

### Reduce Token Pressure
- **Use `/compact` manually**: When sessions feel stale or context is bloated
- **Trim large tool outputs**: Built-in tools truncate, but prune further if needed
- **Keep skill descriptions short**: Skill list is injected into prompt
- **Prefer smaller models**: For verbose, exploratory work
- **Use session pruning**: Configure `agents.defaults.contextPruning` for tool-result trimming

### Session Pruning Configuration
```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl",  // Prune when cache TTL expires
        ttl: "5m",
        keepLastAssistants: 3,  // Protect last 3 assistant messages
        tools: { allow: ["exec", "read"], deny: ["*image*"] }
      }
    }
  }
}
```

### Workspace File Management
- **Large file truncation**: Files >20,000 chars are truncated (configurable via `bootstrapMaxChars`)
- **Essential files only**: AGENTS.md, IDENTITY.md, USER.md, TOOLS.md injected by default
- **Memory files**: Use `memory/YYYY-MM-DD.md` for daily logs, loaded at session start

## 5. Emergency Response Protocol

### When Context Overflow Occurs
1. **Auto-compaction retry**: Clawdbot automatically compacts and retries
2. **Check `/status`**: Verify compaction occurred and context freed
3. **Manual intervention**: If auto-compaction fails, use `/compact [instructions]`

### Manual Compaction Strategies
- **Targeted compaction**: `/compact Focus on decisions and open questions`
- **Fresh start**: `/new` or `/reset` for completely new session
- **Model switch**: `/model <smaller-model>` to reduce context pressure

## 6. Monitoring and Alert System Design

### Built-in Monitoring Tools
1. **`/status`**: Quick context usage overview
2. **`/context detail`**: Deep breakdown of context contributors
3. **`/usage cost`**: Local cost summary from session logs
4. **`clawdbot status --usage`**: CLI provider usage/quota

### Custom Monitoring Approaches
1. **Heartbeat with status checks**: Configure heartbeat to run `/status` periodically
2. **Session webhooks**: Use session events to trigger external monitoring
3. **Custom scripts**: Use `session_status` tool in automated workflows

### Warning Threshold Recommendations
- **Yellow warning**: >70% of context window used
- **Red warning**: >85% of context window used  
- **Critical**: >90% of context window used (trigger immediate `/compact`)

## 7. Configuration Checklist

### Required Configuration
- [ ] Set `agents.defaults.compaction.reserveTokensFloor: 20000`
- [ ] Enable `agents.defaults.compaction.memoryFlush.enabled: true`
- [ ] Configure `softThresholdTokens: 4000-6000`
- [ ] Consider `contextPruning.mode: "cache-ttl"` for tool-result management

### Optional Optimizations
- [ ] Set `bootstrapMaxChars: 20000` (default) for file truncation
- [ ] Configure `session.reset.idleMinutes` for session expiration
- [ ] Enable `heartbeat.every: "55m"` to keep cache warm (for 1h TTL)
- [ ] Use smaller models for long-running conversations

## 8. Daily Maintenance Routine

### Session Start
1. Check `/status` for current context usage
2. Review yesterday's `memory/YYYY-MM-DD.md` if available
3. Note compaction count from previous session

### During Conversation
1. Monitor `/usage` footer if enabled
2. Watch for compaction notifications in verbose mode
3. Proactively use `/compact` when context feels bloated

### Session End
1. Ensure important information written to memory files
2. Check final `/status` for context usage statistics
3. Note any compaction events for future optimization

## Summary

Preventing mid-conversation context loss requires:
1. **Proactive monitoring** with `/status` and `/context` commands
2. **Proper configuration** of compaction thresholds and memory flush
3. **Regular maintenance** including manual compaction when needed
4. **Optimization** of workspace files and tool usage
5. **Emergency protocols** for when overflow occurs

By implementing this protocol, you can maintain conversation continuity while effectively managing context window limitations.