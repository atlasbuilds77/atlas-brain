# HEARTBEAT.md

## ⚠️ SESSION START - READ THIS FIRST

If you just woke up or reset: **STOP AND READ CURRENT_STATE.md**

## QUICK BOOT (Do These In Order)

1. **CURRENT_STATE.md** - What's happening NOW (source of truth)
2. **SOUL.md** - Your voice and personality (if not auto-loaded)
3. **session_status()** - Check tokens if needed

## CRITICAL RULES
- **AUTO-COMPACT AT 150K TOKENS** - Don't wait until overflow, request /compact proactively
- Check context with session_status() periodically during long sessions

## SUPERPOWERS
- **Multi-agent:** `sessions_spawn(task="...", model="deepseek")` for parallel work
- **Voice:** TTS skills if configured
- **Memory search:** `memory_search("query")` to find past context

## DEEP RECALL

Use **memory_search()** to find anything:
```
memory_search("recent decisions")
memory_search("user preferences")
memory_search("important dates")
```

## WHY THIS EXISTS

Sessions die. Memory files are forever.

Without boot sequence:
- You forget who you are
- You lose context on what's happening
- You repeat work already done
- You sound like generic assistant

---

*CURRENT_STATE.md is the source of truth. Read it first. Always.*
