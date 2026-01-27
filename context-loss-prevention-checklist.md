# Context Loss Prevention Checklist

## Quick Reference

### Essential Commands
- `/status` - Current context usage + compaction count
- `/context list` - Breakdown of context contributors  
- `/compact [instructions]` - Manual compaction with focus
- `/usage tokens` - Enable per-response usage footer
- `/new` or `/reset` - Fresh session start

## Monitoring Protocol

### Daily/Per-Session
- [ ] Start session: Check `/status` for baseline
- [ ] Enable: `/usage tokens` for continuous monitoring
- [ ] Monitor: Watch for `🧹 Auto-compaction complete` in verbose mode
- [ ] Proactive: Use `/compact` at ~70% context usage

### Warning Thresholds
- **70%** - Yellow warning, consider manual compaction
- **85%** - Red warning, run `/compact` immediately
- **90%** - Critical, auto-compaction should trigger

## Configuration Checklist

### Required Settings
```json5
{
  agents: {
    defaults: {
      compaction: {
        reserveTokensFloor: 20000,
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 4000
        }
      }
    }
  }
}
```

### Optional Optimizations
- [ ] `contextPruning.mode: "cache-ttl"` - Tool result trimming
- [ ] `heartbeat.every: "55m"` - Keep cache warm (for 1h TTL)
- [ ] `bootstrapMaxChars: 20000` - File size limits

## Emergency Response

### When Context Overflow Occurs
1. [ ] Auto-compaction will retry automatically
2. [ ] Check `/status` to verify compaction succeeded
3. [ ] If failed: `/compact Focus on key decisions and open questions`
4. [ ] As last resort: `/new` for fresh session

### Manual Compaction Strategies
- **General**: `/compact`
- **Focused**: `/compact Keep technical specifications and current task`
- **Minimal**: `/compact Preserve only the last 10 messages and key decisions`

## Best Practices

### Reduce Token Usage
- [ ] Keep tool outputs concise (they're truncated but still count)
- [ ] Use smaller models for long conversations
- [ ] Write important info to `memory/YYYY-MM-DD.md`
- [ ] Avoid unnecessary file injections

### Session Management
- [ ] Regular `/status` checks during long conversations
- [ ] Proactive compaction before complex multi-step tasks
- [ ] Use `/context detail` to identify large contributors
- [ ] Consider session pruning for tool-heavy workflows

## Quick Diagnostics

### Symptoms of Context Pressure
- [ ] Model forgetting recent information
- [ ] Increased auto-compaction frequency
- [ ] `/status` shows high context percentage
- [ ] Verbose mode shows frequent compaction messages

### Immediate Actions
1. [ ] Run `/context list` to identify large files
2. [ ] Check tool schema sizes in `/context detail`
3. [ ] Compact manually with specific instructions
4. [ ] Consider switching to model with larger context window

## Automation Ideas

### Heartbeat Integration
```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        prompt: "Check context usage with /status and compact if >70%"
      }
    }
  }
}
```

### Custom Monitoring Script
- Use `session_status` tool in automated workflows
- Set up webhooks for compaction events
- Create alert when compaction count increases rapidly

---

**Remember**: Proactive monitoring is key. Don't wait for overflow - compact at 70-80% usage to maintain conversation continuity.