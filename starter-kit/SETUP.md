# Setup Guide

This guide will help you install Clawdbot and set up your personal assistant.

---

## Requirements

- **Node.js** v18+ (https://nodejs.org)
- **Python 3.8+** (for brain scripts)
- A messaging account (Telegram recommended for Windows)

---

## Step 1: Install Node.js

### Windows
1. Download from https://nodejs.org (LTS version)
2. Run the installer
3. Open PowerShell and verify: `node --version`

### Mac
```bash
brew install node
```

---

## Step 2: Install Clawdbot

Open terminal (PowerShell on Windows, Terminal on Mac):

```bash
npm install -g clawdbot
```

Verify installation:
```bash
clawdbot --version
```

---

## Step 3: Configure Clawdbot

Run the setup wizard:

```bash
clawdbot configure
```

This will:
- Set up your API keys (Anthropic recommended)
- Configure messaging channels
- Create config file

### For Telegram (Recommended for Windows):
1. Create a bot via @BotFather on Telegram
2. Get your bot token
3. Enter it during configure
4. Get your Telegram user ID (message @userinfobot)
5. Add to allowlist

### For iMessage (Mac only):
- Works automatically on Mac
- Add phone numbers to allowlist

---

## Step 4: Set Up Workspace

1. Create a folder for your assistant:
```bash
mkdir ~/my-assistant
cd ~/my-assistant
```

2. Copy the starter kit files into this folder

3. Your folder should look like:
```
my-assistant/
├── AGENTS.md
├── BOOTSTRAP.md
├── HEARTBEAT.md
├── SETUP.md (this file - can delete after setup)
├── scripts/
│   ├── sleep.sh
│   ├── consolidate.py
│   ├── weekly-consolidate.py
│   ├── confidence.py
│   └── gut-check.py
└── memory/
    ├── insights/
    ├── weekly/
    └── archive/
```

---

## Step 5: Point Clawdbot to Your Workspace

Edit your Clawdbot config to use this workspace:

```bash
clawdbot configure
```

Or manually edit `~/.clawdbot/clawdbot.json`:
```json
{
  "agents": {
    "defaults": {
      "workspace": "/path/to/my-assistant"
    }
  }
}
```

---

## Step 6: Start Clawdbot

```bash
clawdbot gateway start
```

Or run in foreground to see logs:
```bash
clawdbot gateway run
```

---

## Step 7: First Conversation

Message your bot! It will:
1. Read BOOTSTRAP.md
2. Ask you questions to get to know you
3. Create its identity based on your preferences
4. Set up your USER.md with your info

After onboarding, it will delete BOOTSTRAP.md and be ready to work!

---

## Optional: Set Up Cron Jobs

For scheduled memory consolidation, set up cron jobs after your first conversation:

**Sleep consolidation (3 AM daily):**
- The assistant can set this up via `cron action=add`

**Weekly consolidation (Sunday 4 AM):**
- Same method

---

## Troubleshooting

### "Command not found: clawdbot"
- Make sure Node.js is installed
- Try: `npm install -g clawdbot` again
- On Windows, restart PowerShell

### Bot not responding
- Check: `clawdbot gateway status`
- Check logs: `clawdbot gateway run` (foreground mode)
- Verify your user ID is in allowlist

### Scripts not working
- Make sure Python 3 is installed
- On Windows, use `python` instead of `python3`
- Make scripts executable (Mac/Linux): `chmod +x scripts/*.sh`

---

## Getting Help

- Clawdbot Discord: https://discord.com/invite/clawd
- Documentation: https://docs.clawd.bot
- GitHub: https://github.com/clawdbot/clawdbot

---

*Good luck with your new assistant!*
