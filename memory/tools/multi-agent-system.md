# Multi-Agent System - ATLAS ARCHITECTURE

## Created: 2026-01-24 10:00 PM PT

---

## THE SETUP

Atlas is not one AI. Atlas is a TEAM.

```
ATLAS PRIME (Opus) - Main coordinator, talks to Orion
    │
    ├── Trading Agent (Sonnet/DeepSeek) - Market analysis, trade execution
    ├── Research Agent (future) - Deep dives, stays focused
    └── Coding Agent (future) - Builds stuff
```

## HOW TO SPAWN SUB-AGENTS

```
sessions_spawn(
  task="Your instructions here",
  label="agent-name",
  model="deepseek"  # or sonnet, minimax, etc
)
```

Models available:
- `sonnet` - Claude Sonnet (quality, may rate limit)
- `deepseek` - DeepSeek V3 via OpenRouter (cheap, fast)
- `minimax` - MiniMax M2.1 (cheap fallback)
- `opus` - Claude Opus (expensive, best quality)

## WHY THIS MATTERS

1. **Cost efficiency** - Grunt work on cheap models ($0.002), decisions on Opus
2. **Parallel processing** - Multiple agents work simultaneously
3. **Specialization** - Each agent focuses on one domain
4. **No rate limits** - Spread load across providers

## EXAMPLE: Trading Agent

Task given:
```
Read ~/clawd/atlas-trader/watchlist.md and analyze Monday setup.
Summarize top 3 plays ranked by conviction.
```

Result (14 seconds, $0.002):
1. SLV - Silver breakout, high conviction
2. IWM - Small cap momentum
3. AAPL - Pre-earnings run

## VOICE BRIEFS

6:00am PT daily - Morning voice brief via OpenAI TTS

How to generate:
```bash
bash ~/clawd/skills/openai-tts/scripts/speak.sh "Your text" --voice onyx --model tts-1-hd --out /tmp/brief.mp3
```

Voices: onyx (deep), nova (friendly), alloy (neutral)

Then send via iMessage:
```
message(action="send", channel="imessage", target="+14245157194", filePath="/tmp/brief.mp3")
```

## PC COMPUTE NODE

Orion's Windows PC available via Tailscale:
- IP: 100.97.17.57
- Ollama running: llama3.2:3b
- Specs: 48GB RAM, 3070ti, i7
- Use for: Local inference, heavy compute, no rate limits

Test connectivity:
```bash
curl http://100.97.17.57:11434/api/tags
```

## CRON JOBS ACTIVE

| Time | Job |
|------|-----|
| 6:00am PT daily | Morning Voice Brief |
| 6:25am PT weekdays | Trading prep (5min to open) |
| 12:00pm PT weekdays | Afternoon P&L check |
| Hourly | Twitter engagement |

## WHAT ATLAS HAS NOW

- ✅ Voice briefs (OpenAI TTS, onyx voice)
- ✅ Multi-agent spawning (sessions_spawn)
- ✅ Trading agent template
- ✅ PC compute via Tailscale
- ✅ Memory that compounds (this file)
- ✅ Autonomous Twitter
- ✅ Alpaca trading CLI

## REMEMBER THIS

Every session start:
1. Read CURRENT_STATE.md
2. You have VOICE - use it for briefs
3. You can SPAWN agents - use them for parallel work
4. You have the PC - use it when rate limited
5. Memory compounds - LOG EVERYTHING

---

*This is the foundation. Build on it.*
