# TradingAgents - Multi-Agent LLM Trading

## Overview
Framework that mirrors real trading firms with specialized agents.

**Location:** ~/clawd/TradingAgents/
**Research:** ~/clawd/TradingAgents/ATLAS_RESEARCH.md

## Agents
1. **Analysts** (4 types): Fundamentals, Market/Technical, News, Social
2. **Researchers:** Bull + Bear debate until judge decides
3. **Trader:** Synthesizes reports, makes plan
4. **Risk Management:** Risky/Safe/Neutral debate
5. **Portfolio Manager:** Final approval

## Key Features
- Swappable LLMs (OpenAI, Anthropic, Ollama, OpenRouter)
- Memory system (learns from wins/losses)
- Transparent reasoning (logs full debates)
- Works with cheap models (gpt-4o-mini)

## Status
- ✅ Cloned and analyzed
- ✅ Full research doc written
- ⏳ Needs API keys to test (OpenAI + Alpha Vantage)
- ⏳ Not tested yet

## How to Run
```bash
cd ~/clawd/TradingAgents
export OPENAI_API_KEY=xxx
export ALPHA_VANTAGE_API_KEY=xxx
python main.py  # or python -m cli.main
```

## Use Cases
1. Research assistant (analyze stocks for Orion)
2. Backtest decisions vs actual outcomes
3. Integration with Poseidon
4. Client reports for Kronos

## Verdict
Good for swing trades and research. Too slow for intraday. Start with research assistant mode.

---

*Update after testing*
