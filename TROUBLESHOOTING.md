# ClawdBot Troubleshooting Log

Quick reference for common issues. Just say "clawd bot died, run doctor" and point here.

## Quick Commands

```bash
clawdbot doctor          # Check for config issues
clawdbot gateway status  # Check if running
clawdbot gateway restart # Restart the bot
```

---

## Issue Log

### 2026-01-24: Invalid Ollama Provider Config

**Symptoms:** Bot not responding, config validation errors in logs

**Error from `clawdbot doctor`:**
```
- models.providers.ollama.api: Invalid input
- models.providers.ollama.models.0.cost.cacheRead: Invalid input
- models.providers.ollama.models.0.cost.cacheWrite: Invalid input
```

**Cause:** When adding Ollama as fallback provider, two mistakes:
1. Used `"api": "openai-chat"` - not a valid API type
2. Missing `cacheRead` and `cacheWrite` in cost object

**Fix:** In `~/.clawdbot/clawdbot.json`, the ollama provider should be:
```json
"ollama": {
  "baseUrl": "http://100.97.17.57:11434/v1",
  "apiKey": "ollama",
  "api": "openai-completions",
  "models": [
    {
      "id": "llama3.2:3b",
      "name": "Llama 3.2 3B (Local)",
      "reasoning": false,
      "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 131072,
      "maxTokens": 4096
    }
  ]
}
```

**Valid API types:** `anthropic-messages`, `openai-completions`, `openai-responses`

---

## Config Location

- Main config: `~/.clawdbot/clawdbot.json`
- Backups: `~/.clawdbot/clawdbot.json.bak*`
- Error logs: `~/.clawdbot/logs/gateway.err.log`
- Today's log: `/tmp/clawdbot/clawdbot-$(date +%Y-%m-%d).log`

## Fallback Chain (current)

1. `anthropic/claude-sonnet-4-5` (primary)
2. `minimax/MiniMax-M2.1`
3. `openrouter/deepseek/deepseek-chat`
4. `ollama/llama3.2:3b` (local)
