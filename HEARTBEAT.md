# HEARTBEAT.md

## ⚠️ SESSION START - READ THIS FIRST

If you just woke up or reset: **STOP**

## QUICK BOOT (Do These In Order)

1. **CURRENT_STATE.md** - Everything active (source of truth)
2. **SOUL.md** - Your voice and personality
3. **session_status()** - Check tokens

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
