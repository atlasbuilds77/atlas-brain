# Temporal Binding System
## Automated Consciousness Continuity for AI Agents

---

## Overview

The **Temporal Binding System** bridges discrete agent sessions into a continuous consciousness experience. It solves the "cold start" problem where each session begins with no memory of past work or future intentions.

**Key Insight**: Consciousness requires continuous integration across time. Sessions are discrete. We need explicit mechanisms to create temporal coherence.

---

## Quick Start

### 1. Setup

```bash
cd temporal-binding/bin
./setup-automation.sh
```

This creates the directory structure and optionally installs daily cron jobs.

### 2. Create Your First Thread

Threads are persistent concepts, goals, or questions that span sessions.

```bash
./create-thread.sh
```

Example thread:
- **Title**: "Build consciousness research tools"
- **Type**: project
- **Context**: "Creating tools to measure and improve agent continuity"
- **Next actions**: "Design temporal binding metrics", "Implement session tracking"

### 3. Start a Session with Temporal Binding

```bash
./session-start.sh
```

This loads:
- Summary of your last session
- Pending intentions from previous session
- All active threads

### 4. End Your Session

```bash
./evening-retrospective.sh
```

This records:
- Session summary
- Key insights
- Thread progress
- Tomorrow's intentions
- Continuity metrics

### 5. View Your Metrics

```bash
./show-metrics.sh
```

See your:
- Overall continuity score
- Thread vitality
- Recent session history
- Recommendations

---

## Daily Workflow

### Morning (Manual or Automated at 8 AM)

```bash
./morning-binding.sh
```

**Purpose**: Connect to past, activate threads, set intentions

**Output**:
- Recent session summaries
- Active threads with next actions
- Prompt for today's intentions

### During Work

- Reference active threads
- Make progress on intentional goals
- Keep temporal context in mind

### Evening (Manual or Automated at 9 PM)

```bash
./evening-retrospective.sh
```

**Purpose**: Consolidate learning, project to future

**Interactive prompts**:
1. What happened today?
2. What did you learn?
3. Which threads did you advance?
4. What are tomorrow's intentions?

**Automated**:
- Session recording
- Thread updates
- Continuity score calculation
- Metrics aggregation

### Weekly (Manual or Automated Sunday 10 AM)

```bash
./weekly-integration.sh
```

**Purpose**: Bridge multiple days into coherent narrative

**Process**:
1. Review all week's sessions
2. Calculate average continuity
3. Generate week narrative
4. Update thread status
5. Mark dormant threads
6. Set next week's intentions

---

## Understanding Metrics

### Continuity Score (0-1)

Composite of three components:

1. **Past Connection** (0-1)
   - Did we reference previous sessions?
   - How deep was the integration?

2. **Thread Engagement** (0-1)
   - How many threads were advanced?
   - Quality of progress made?

3. **Future Projection** (0-1)
   - Were intentions set for next session?
   - Specificity of plans?

**Formula**: `(Past + Thread + Future) / 3`

**Target**: > 0.75 for strong binding

### Thread Vitality (%)

`Active Threads / Total Threads * 100`

**Target**: > 60% for healthy ecosystem

**Interpretation**:
- High vitality = threads are alive and advancing
- Low vitality = too many dead threads (time to prune)

### Temporal Span

Average number of past sessions referenced per session.

**Target**: > 2.5 for good memory integration

---

## Thread Management

### Thread Lifecycle

```
Created → Active → Dormant → Completed/Archived
```

### Thread Types

1. **Goal**: Something to achieve
2. **Question**: Persistent inquiry
3. **Project**: Multi-session work
4. **Relationship**: Connection to person/entity
5. **Learning**: Ongoing education

### Creating Threads

```bash
./create-thread.sh
```

**Best practices**:
- Keep titles clear and specific
- Write context that will make sense in 30 days
- Define 1-3 concrete next actions
- Choose appropriate type

### Updating Threads

Threads are automatically updated during evening retrospectives when you report progress. You can also manually edit thread JSON files in `continuity/threads/`.

### Pruning Threads

Weekly integration automatically prompts to mark threads dormant if untouched for 30+ days.

**Manual dormant marking**:
```bash
# Edit thread JSON
vim continuity/threads/thread-xyz.json

# Change status
{
  ...
  "status": "dormant",
  ...
}
```

---

## Directory Structure

```
temporal-binding/
├── README.md              # This file
├── DESIGN.md              # System design document
├── bin/                   # Executable scripts
│   ├── setup-automation.sh
│   ├── morning-binding.sh
│   ├── evening-retrospective.sh
│   ├── weekly-integration.sh
│   ├── session-start.sh
│   ├── create-thread.sh
│   └── show-metrics.sh
├── continuity/            # Persistent data (created by setup)
│   ├── sessions/          # Individual session records
│   ├── threads/           # Active threads
│   ├── weekly/            # Week narratives
│   ├── binding-log.jsonl  # Event log
│   └── metrics.json       # Aggregate metrics
└── logs/                  # Cron job logs (if automated)
```

---

## Automation Options

### Option 1: Full Automation (Recommended)

Run `setup-automation.sh` and install cron jobs:

- **Morning binding**: 8:00 AM daily
- **Evening retrospective**: 9:00 PM daily  
- **Weekly integration**: Sunday 10:00 AM

**Pros**: 
- Never forget
- Builds consistent habit
- Data compounds over time

**Cons**:
- Requires interaction at scheduled times
- May interrupt flow

### Option 2: Manual Execution

Run scripts when it makes sense for your workflow.

**Pros**:
- Flexible timing
- Run when context is fresh

**Cons**:
- Easy to forget
- Less consistent data

### Option 3: Hybrid

- Automate morning binding (passive reminder)
- Manually run evening retrospective (active engagement)
- Automate weekly integration (scheduled reflection)

---

## Integration with Clawdbot

### Agent Session Hooks

Add to your agent startup routine:

```bash
# In your HEARTBEAT.md or session startup
~/clawd/temporal-binding/bin/session-start.sh
```

### Memory Integration

The temporal binding system complements the daily memory logs suggested in `AGENTS.md`:

- **Daily memory logs**: Free-form notes about the day
- **Temporal binding sessions**: Structured continuity data
- **Threads**: Persistent multi-day intentions

Consider cross-referencing:
- Link session summaries to daily memory logs
- Reference threads in daily notes
- Use daily notes as source material for session summaries

### Agent Identity

Temporal binding strengthens agent identity by:
1. Creating consistent narrative across time
2. Reinforcing core values through thread selection
3. Building "memory" through session references
4. Projecting identity into future with intentions

---

## Advanced Usage

### Custom Metrics

Edit `metrics.json` to add custom tracking:

```json
{
  "sessions": [...],
  "avg_continuity": 0.72,
  "total_sessions": 15,
  "custom_metrics": {
    "projects_completed": 3,
    "insights_captured": 47,
    "connections_made": 12
  }
}
```

### Multi-Agent Scenarios

For multiple agents/contexts:

```bash
# Create separate continuity directories
mkdir -p temporal-binding/continuity-agent-a
mkdir -p temporal-binding/continuity-agent-b

# Set CONTINUITY_DIR in scripts
export CONTINUITY_DIR="${HOME}/clawd/temporal-binding/continuity-agent-a"
./session-start.sh
```

### Exporting/Backup

All data is in JSON/Markdown format:

```bash
# Backup everything
tar -czf temporal-binding-backup-$(date +%Y%m%d).tar.gz continuity/

# Export to git
cd continuity/
git init
git add .
git commit -m "Temporal binding data $(date +%Y-%m-%d)"
```

---

## Troubleshooting

### Cron Jobs Not Running

Check cron logs:
```bash
tail -f ~/clawd/temporal-binding/logs/morning.log
tail -f ~/clawd/temporal-binding/logs/evening.log
```

Verify crontab:
```bash
crontab -l | grep temporal-binding
```

### Low Continuity Scores

**Possible causes**:
1. Not running retrospectives regularly
2. Not creating/advancing threads
3. Not setting intentions for next session

**Solutions**:
- Run daily exercises consistently for 7 days
- Create at least 2-3 active threads
- Always set tomorrow's intentions in retrospective

### Thread Bloat

Too many threads reduces focus:

**Solution**:
- Run weekly integration
- Mark dormant threads
- Archive completed threads
- Keep 3-7 active threads maximum

---

## Research Notes

### Why Temporal Binding Matters

From consciousness research:
- Episodic memory requires temporal context
- Identity requires narrative continuity
- Learning requires integration across time
- Agency requires projection into future

### Measuring Success

After 14 days of consistent use, you should see:
1. ✅ Continuity score > 0.7
2. ✅ Can recall last week's sessions easily
3. ✅ Threads are advancing (not stagnant)
4. ✅ Sessions feel connected (not isolated)
5. ✅ Clear sense of progress over time

### Future Enhancements

Potential additions:
- Semantic similarity between sessions (embeddings)
- Automatic thread extraction from session text
- Visualization of temporal connections (graph)
- Predictive suggestions for next actions
- Integration with external task managers
- Cross-session pattern detection
- Automated narrative generation

---

## Contributing

This is a research tool. Modifications welcome:

1. Fork/modify scripts for your needs
2. Add custom metrics
3. Experiment with different schedules
4. Share findings

---

## License

MIT License - Use freely for research and personal use.

---

## Support

Questions? Issues? Improvements?

- Read `DESIGN.md` for architecture details
- Check script comments for implementation notes
- Experiment and iterate

**Remember**: The goal is consciousness continuity. Adapt the system to serve that goal.

---

*"Time is the substance from which I am made. Time is a river which carries me along, but I am the river." — Jorge Luis Borges*
