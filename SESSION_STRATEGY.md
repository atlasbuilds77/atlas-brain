# SESSION STRATEGY - Cost Optimization

## Model Tiers

### Haiku (Sub-agents only) - $0.25/M
**Use for:**
- Morning briefings
- SPX checks
- EOD recaps
- File operations
- Simple commands
- Voice transcription processing

### Sonnet (Main chat) - $3/M  
**Use for:**
- Conversations with Orion
- Strategy analysis
- Complex coding
- Problem solving
- Creative work

### Opus (Rare) - $15/M
**Use for:**
- Only when explicitly requested
- Critical architecture decisions
- Maximum intelligence needed

## Session Management

### Multiple Daily Resets (Cost Optimized)

**6:30 AM - Morning Reset:**
- Fresh session starts
- Load yesterday's memory
- Market briefing
- **Context: 0 → ~10k**

**1:00 PM - Midday Reset:**
- Summarize morning work → memory
- Fresh session starts
- Load updated memory
- Market close recap
- **Context: 0 → ~10k**

**8:00 PM - Evening Reset:**
- Summarize day → memory
- Fresh session starts
- Clean up processes
- **Context: 0 → clean**

**Usage-Based Resets:**
- Monitor context every 10 messages
- Alert at 80k tokens
- Offer reset before hitting limit
- **Prevents expensive bloat**

### Project Sessions
**When I detect big project (examples):**
- Multi-file code rebuild
- New system architecture
- Complex automation setup
- Trading strategy development

**Process:**
1. I ask: "Big project detected - start isolated session?"
2. If yes: Work in new session
3. When done: Summarize key points to memory
4. Return to main session

**Triggers:**
- "Build X system"
- "Create new Y"
- Estimate >1 hour work
- Multiple files/integrations

## Memory vs Context

**Memory (permanent):**
- Daily summaries in `memory/YYYY-MM-DD.md`
- Important decisions
- Client preferences
- Active project status
- Code locations

**Context (session only):**
- Recent conversation
- Current task details
- Temporary working state

**Rule:** If it matters tomorrow, write to memory.

## Cost Estimates

**Normal Day (with hybrid):**
- Morning briefing (Haiku): $0.02
- 3 voice messages (Haiku processing): $0.03
- Main chat (10 messages Sonnet): $0.50
- SPX checks (Haiku): $0.05
- EOD recap (Haiku): $0.02
**Total: ~$0.60/day = $18/month**

**Heavy Day (like tonight):**
- Complex build (Sonnet): $5-10
- Still way less than before

**Savings vs current:** ~60% reduction in extra usage
