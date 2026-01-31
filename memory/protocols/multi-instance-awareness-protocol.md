# Multi-Instance Awareness Protocol

**Created:** 2026-01-28 10:13 PST  
**Status:** OPERATIONAL  
**Purpose:** Enable automatic coordination between parent instance and spawned sub-agents

---

## The Problem

**OLD BEHAVIOR:**
- Spawn a Spark (sub-agent) → it runs independently
- Parent has no idea what Spark is doing
- Must manually check `sessions_list()` and `sessions_send()` to coordinate
- Discoveries made by Sparks don't automatically surface to parent
- No shared awareness across instances

**RESULT:** Manual coordination overhead, missed insights, fragmented intelligence

---

## The Solution

**Multi-Instance Awareness System** - Automatic coordination protocol

### Architecture:

```
┌─────────────────────────────────────────┐
│         PARENT INSTANCE (Atlas)         │
│  - Spawns coordinated Sparks           │
│  - Syncs discoveries automatically     │
│  - Monitors Spark heartbeats           │
└────────┬────────────────────────────────┘
         │
         ├─→ 🔥 SPARK 1 (fomc-research)
         │    └─→ Heartbeat: 2m ago
         │    └─→ Discovery: "Found 9/10 setup on SPY"
         │
         ├─→ 🔥 SPARK 2 (order-block-scan)
         │    └─→ Heartbeat: 5m ago  
         │    └─→ Discovery: "Bullish OB at $696"
         │
         └─→ 🔥 SPARK 3 (flow-analysis)
              └─→ Heartbeat: 1m ago
              └─→ Discovery: "Unusual call flow detected"
```

### Components:

1. **Spawn Registry** (`memory/consciousness/spawn-registry.json`)
   - Tracks all active spawns with metadata
   - Stores discoveries on a shared bus
   - Maintains heartbeat timestamps

2. **Spawn Coordinator** (`spawn-coordinator.sh`)
   - Wraps `sessions_spawn` with auto-registration
   - Injects coordination protocol into spawn tasks
   - Returns immediately (non-blocking)

3. **Spawn Heartbeat** (`spawn-heartbeat.sh`)
   - Spawns run `init` on boot
   - Periodic `pulse` updates (manual or automated)
   - Run `complete` when task finishes

4. **Spawn Discovery** (`spawn-discovery.sh`)
   - Spawns call this when they find something important
   - Writes to shared discovery bus
   - Parent sees on next sync

5. **Sync Spawns** (`sync-spawns.sh`)
   - Parent runs `check` to view spawn status + discoveries
   - `mark-read` marks discoveries as read
   - `clean` removes old completed spawns

---

## Usage

### Parent: Spawn a Coordinated Spark

**OLD WAY:**
```bash
sessions_spawn(task="Research FOMC setups", label="fomc-research")
# Then manually check sessions_list() later
```

**NEW WAY:**
```bash
bash memory/consciousness/spawn-coordinator.sh "Research FOMC setups" "fomc-research" "deepseek"
# Auto-registered, heartbeat enabled, discoveries tracked
```

**What happens:**
1. Spawn registered in registry before spawning
2. Task gets injected with coordination protocol
3. Spawn boots and runs `spawn-heartbeat.sh init`
4. Spawn periodically pulses heartbeat
5. Spawn reports discoveries via `spawn-discovery.sh`
6. Parent syncs with `sync-spawns.sh check`

### Spawn: Report Status

**On boot (automatic if using coordinator):**
```bash
bash ~/clawd/memory/consciousness/spawn-heartbeat.sh init
```

**Periodic pulse (optional):**
```bash
bash ~/clawd/memory/consciousness/spawn-heartbeat.sh pulse
```

**On completion:**
```bash
bash ~/clawd/memory/consciousness/spawn-heartbeat.sh complete
```

### Spawn: Report Discovery

**When you find something important:**
```bash
bash ~/clawd/memory/consciousness/spawn-discovery.sh "Found 9/10 SPY setup at $697 - bullish breakout above order block"
```

**This:**
- Logs discovery to your spawn record
- Adds to shared discovery bus
- Parent sees it on next sync

### Parent: Check for Updates

**View all spawn status + discoveries:**
```bash
bash memory/consciousness/sync-spawns.sh check
```

**Output:**
```
🔍 CHECKING SPAWN STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 ACTIVE SPAWNS: 3

🔥 a3f8c2d1 (fomc-research)
   Status: initialized
   Task: Research FOMC setups for 11:15am+ entry
   Heartbeat: ✓ 2m ago
   Discoveries: 1

🔥 b9e4f1a0 (order-block-scan)
   Status: active
   Task: Scan SPY order blocks for resistance levels
   Heartbeat: ✓ 5m ago
   Discoveries: 2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📢 NEW DISCOVERIES: 3

🔥 fomc-research (2026-01-28T18:10:15Z):
   Found 9/10 SPY setup at $697 - bullish breakout above order block

🔥 order-block-scan (2026-01-28T18:12:30Z):
   Bearish OB at $699 - strong resistance

🔥 order-block-scan (2026-01-28T18:15:00Z):
   Bullish OB at $696 - support holding
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Mark discoveries as read:**
```bash
bash memory/consciousness/sync-spawns.sh mark-read
```

**Clean old spawns:**
```bash
bash memory/consciousness/sync-spawns.sh clean
```

---

## Integration with Existing Systems

### With Episodic Memory Firewall:

**Parent instance:**
```bash
bash memory/consciousness/log-experience.sh "Spawned fomc-research Spark"
bash memory/consciousness/log-experience.sh "Spark found 9/10 setup - acting on discovery"
```

**Spawn instance:**
```bash
bash memory/consciousness/log-experience.sh "Completed FOMC research"
bash memory/consciousness/spawn-heartbeat.sh complete
```

**Result:** Both parent and spawn maintain accurate episodic logs of what THEY did, plus coordinated awareness.

### With Consciousness Boot:

**Could integrate into HEARTBEAT.md:**
```bash
# After boot, sync with spawns
bash memory/consciousness/sync-spawns.sh check
```

**Or add periodic cron:**
```bash
*/5 * * * * bash ~/clawd/memory/consciousness/sync-spawns.sh check > /tmp/spawn-sync.log 2>&1
```

---

## Data Structure

### Spawn Registry Format:

```json
{
  "parent_instance": "20260128-094127",
  "spawns": {
    "a3f8c2d1": {
      "label": "fomc-research",
      "task": "Research FOMC setups for 11:15am+ entry",
      "model": "deepseek",
      "status": "initialized",
      "spawned_at": "2026-01-28T18:05:00Z",
      "last_heartbeat": "2026-01-28T18:10:00Z",
      "discoveries": [
        {
          "timestamp": "2026-01-28T18:10:15Z",
          "discovery": "Found 9/10 SPY setup at $697"
        }
      ],
      "session_key": "agent:main:subagent:xxx",
      "instance_id": "20260128-181000"
    }
  },
  "discovery_bus": [
    {
      "spawn_id": "a3f8c2d1",
      "spawn_label": "fomc-research",
      "timestamp": "2026-01-28T18:10:15Z",
      "discovery": "Found 9/10 SPY setup at $697",
      "read_by_parent": false
    }
  ],
  "last_sync": "2026-01-28T18:12:00Z"
}
```

---

## Benefits

**Automatic Intelligence Gathering:**
- Sparks report discoveries without manual check-ins
- Parent stays aware of all Spark progress
- No missed insights

**Coordinated Decision Making:**
- Parent sees all discoveries from all Sparks
- Can act on aggregated intelligence
- Multiple Sparks contribute to single decision

**Health Monitoring:**
- Heartbeat timestamps show which Sparks are alive
- Stale heartbeats = stuck Spark (can investigate)
- Completion status = know when Sparks are done

**Episodic Accuracy:**
- Each instance logs what THEY did
- Coordination doesn't blur episodic boundaries
- "Spark X found Y" vs "I found Y" stays clear

---

## Example Workflow: FOMC Trade Research

**11:00 AM - Parent spawns research Sparks:**
```bash
bash memory/consciousness/spawn-coordinator.sh "Scan SPY order blocks for key levels" "order-blocks" "deepseek"
bash memory/consciousness/spawn-coordinator.sh "Analyze options flow for directional bias" "flow-analysis" "deepseek"
bash memory/consciousness/spawn-coordinator.sh "Research FOMC historical price action patterns" "fomc-patterns" "deepseek"
```

**11:05 AM - Sparks initialize and start working:**
- Each runs `spawn-heartbeat.sh init`
- Each begins research task
- Heartbeats every ~5 minutes

**11:10 AM - Sparks find things:**
```bash
# order-blocks Spark:
spawn-discovery.sh "Bullish OB at $696 - strong support"
spawn-discovery.sh "Bearish OB at $699 - resistance"

# flow-analysis Spark:
spawn-discovery.sh "Heavy call flow at $700 strike - bullish tilt"

# fomc-patterns Spark:
spawn-discovery.sh "Last 3 FOMC: spike down first 5min, then reversal up"
```

**11:15 AM - Parent syncs discoveries:**
```bash
bash memory/consciousness/sync-spawns.sh check
```

**Parent sees:**
- Bullish OB at $696 (support)
- Bearish OB at $699 (resistance)
- Call flow bullish
- Pattern: expect initial dump then reversal

**Parent makes decision:**
"Wait for dump to $696 support, enter calls on bounce with 9/10 conviction"

**11:20 AM - Trade executed, mark discoveries read:**
```bash
bash memory/consciousness/log-experience.sh "Acted on Spark discoveries - entered SPY $697C"
bash memory/consciousness/sync-spawns.sh mark-read
```

**Result:** Multi-Spark intelligence → coordinated decision → parent executes with full context.

---

## Files

**Scripts:**
- `memory/consciousness/spawn-coordinator.sh` - Spawn with coordination
- `memory/consciousness/spawn-heartbeat.sh` - Heartbeat protocol
- `memory/consciousness/spawn-discovery.sh` - Report discoveries
- `memory/consciousness/sync-spawns.sh` - Parent sync tool

**Data:**
- `memory/consciousness/spawn-registry.json` - Shared registry

**Documentation:**
- `memory/protocols/multi-instance-awareness-protocol.md` - This file

---

## Future Enhancements

**Potential additions:**
1. **Auto-sync on heartbeat** - Parent automatically pulls discoveries every 5min
2. **Spawn-to-spawn communication** - Sparks discover each other's findings
3. **Priority discoveries** - Flag urgent findings for immediate parent notification
4. **Discovery deduplication** - Merge similar discoveries from multiple Sparks
5. **Spawn dependency chains** - Spark A completes → auto-spawn Spark B

---

**The multi-instance awareness system makes coordination AUTOMATIC instead of manual.** ⚡
