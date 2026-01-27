# Anthropic API Key Swap Guide

**When to use:** Primary $200/mo account hits weekly limits

## Quick Swap (Manual)

1. **Check which key is active:**
```bash
grep ANTHROPIC_API_KEY ~/.clawdbot/clawdbot.json
```

2. **Swap to backup account:**
```bash
clawdbot config set env.ANTHROPIC_API_KEY "sk-ant-YOUR-BACKUP-KEY-HERE"
```

3. **Verify:**
```bash
clawdbot status
```

Gateway auto-restarts and switches accounts immediately.

## Your Two Accounts

**Primary ($200/mo):** [Current key in config]
- Has weekly limits
- Use this as default

**Backup ($100 max tier):** [Store backup key somewhere safe]
- Swap to this when primary hits limits
- Swap back when primary resets

## Pro tip: Store backup key

Save your backup key somewhere accessible:
```bash
echo "export ANTHROPIC_BACKUP_KEY='sk-ant-YOUR-KEY'" >> ~/.zshrc
```

Then swap becomes one command:
```bash
clawdbot config set env.ANTHROPIC_API_KEY "$ANTHROPIC_BACKUP_KEY"
```

## Swap Back to Primary

```bash
clawdbot config set env.ANTHROPIC_API_KEY "sk-ant-YOUR-PRIMARY-KEY"
```

---

**Current setup:**
- Primary: Sonnet (saves limits)
- Use `/model opus` when you need full brain
- AWS Bedrock: automatic fallback if Anthropic dies
