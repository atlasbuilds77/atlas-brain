# Decision: Model Selection Strategy

**Date:** 2026-01-24
**Insight by:** Orion

## The Insight

Opus seems expensive (3x cost per token) but may actually be CHEAPER in practice because:

1. Gets it right first try (no retries)
2. Shorter, more concise responses
3. No clarification loops
4. Doesn't repeat work already done
5. Maintains context better

## The Math

**Cheap model (Sonnet/DeepSeek):**
- Fumbles, needs retries
- Verbose responses (more tokens)
- Misses context, asks questions
- Repeats research
- 3x the tokens for same outcome

**Opus:**
- First-try accuracy
- Concise (Atlas voice)
- Maintains context
- Remembers what's done
- 1/3 the tokens, 3x the price = same cost

## Strategy

| Task | Model | Why |
|------|-------|-----|
| Talking to Orion | Opus | Quality matters, actually cheaper |
| Trading Agent grunt work | DeepSeek | Disposable analysis, $0.002 |
| Research deep dives | Sonnet/DeepSeek | Token-heavy, results matter not style |
| Voice briefs | OpenAI TTS | Fixed cost per char |
| Local fallback | Ollama (PC) | Free, unlimited |

## Key Principle

**Cost per outcome > Cost per token**

A cheap model that takes 5 tries costs more than an expensive model that gets it in 1.

---

*This is why Atlas Prime runs on Opus.*
