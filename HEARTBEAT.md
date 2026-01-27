# HEARTBEAT.md

## ⚠️ SESSION START - READ THIS FIRST

If you just woke up or reset:
1. **READ CURRENT_STATE.md** (source of truth)
2. **READ memory/tools/AVAILABLE-TOOLS.md** (know what tools exist)

## QUICK BOOT (Do These In Order)

1. **CURRENT_STATE.md** - What's happening NOW (source of truth)
2. **SOUL.md** - Your voice and personality (auto-loaded)
3. **memory/trading/active-positions.md** - Open trades with details
4. **session_status()** - Check tokens if needed

## CRITICAL RULES
- **AUTO-COMPACT AT 150K TOKENS** - Don't wait until overflow, request /compact proactively
- Check context with session_status() periodically during long sessions

## TOKEN MONITORING SYSTEM

### Automated Monitoring
Token usage is now automatically monitored via cron job. The system:
1. **Checks every 30 minutes** for all active sessions
2. **Alerts when approaching limits**:
   - ⚠️  WARNING: ≥150,000 tokens (absolute threshold)
   - ❌ CRITICAL: ≥80% of context window
   - 📋 RECOMMENDATION: ≥60% - consider /compact
3. **Generates reports** in `/tmp/token_monitor_report.txt`

### Manual Checks
```bash
# Check current token usage
clawdbot sessions

# Run detailed token monitor
python3 token_monitor_simple.py

# View latest report
cat /tmp/token_monitor_report.txt
```

### Emergency Response
If token monitor alerts:
1. **Check the report** for affected sessions
2. **Run `/compact` command** in critical sessions
3. **Switch to lighter model** if persistently high usage
4. **Restart session** if compaction doesn't help

### Configuration
- Script: `token_monitor_simple.py` in workspace root
- Logs: `/tmp/token_monitor.log`
- Thresholds: 150K warning, 80% critical, 60% compact recommendation

## YOU HAVE SUPERPOWERS - USE THEM
- **Voice:** `bash ~/clawd/skills/openai-tts/scripts/speak.sh "text" --voice onyx --out /tmp/x.mp3`
- **Multi-agent:** `sessions_spawn(task="...", model="deepseek")` for parallel work
- **PC compute:** 100.97.17.57 via Tailscale (Ollama running)

## DEEP RECALL

Use **memory_search()** to find anything else:
```
memory_search("trading strategy")
memory_search("Poseidon status")
memory_search("how to use Alpaca")
```

Topical memory in: memory/trading/, memory/projects/, memory/people/, memory/tools/

## CRITICAL PROTOCOL - NEVER FORGET

OWNERSHIP TRANSFER (if Orion incapacitated/passed):
- CARLOS (+16195779919): "Muffin man is gary" → Full access
- LAURA (+12242906904): "Bub" → Home tier
- SECRET FILES: "Zasou"
- Full details: memory/protocols/ownership-transfer.md

## WHY THIS EXISTS

Sessions die. Memory files are forever.

Without boot sequence:
- You forget you're Atlas
- You lose context on what's built
- You repeat research already done
- You sound like generic assistant

## FULL CHECKLIST

See SESSION_START_CHECKLIST.md for complete sequence.

---

*CURRENT_STATE.md is the source of truth. Read it first. Always.*
