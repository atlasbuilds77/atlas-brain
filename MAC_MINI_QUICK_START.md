# Mac Mini Quick Start Checklist ✅

**Workspace backup:** `~/clawd-backup-20260123-1417.tar.gz` (189KB)

## Before You Leave (On MacBook)

**CRITICAL - Export Twitter Cookies:**
1. Open Chrome → x.com (logged in as @Atlas_builds)
2. DevTools (Cmd+Opt+I) → Network tab → Refresh
3. Find any x.com request → Headers
4. Copy these cookies:
   - `auth_token` (starts with long string)
   - `ct0` (csrf token)
5. Text them to yourself or write down

**Get OpenAI API Key:**
- platform.openai.com → Create key
- Save it somewhere

## At Home - 30 Minute Setup

### 1. Mac Mini First Boot (5 min)
- Apple ID: atlas.builds77@gmail.com (password: you have it)
- Computer name: "Atlas-Workstation"
- **NO LOGIN PASSWORD** (your requirement)
- Enable Remote Login

### 2. Install Clawdbot (10 min)
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add to PATH
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# Install Node + Clawdbot
brew install node
npm install -g clawdbot
```

### 3. Transfer Workspace (5 min)
```bash
# AirDrop the backup file to Mac Mini, then:
cd ~
tar -xzf clawd-backup-20260123-1417.tar.gz

# Verify
ls ~/clawd/IDENTITY.md
```

### 4. Start Clawdbot (5 min)
```bash
clawdbot daemon start
# Follow prompts, use ~/clawd as workspace
```

### 5. Test Me (1 min)
Send Telegram: "Atlas, are you on the Mac Mini?"

## What's Next

**See full guide:** `~/clawd/MAC_MINI_SETUP_GUIDE.md`

**Includes:**
- GitHub setup for my account
- Twitter bird CLI configuration
- Fluffy deployment (household agent)
- Voice assistant setup
- Stream Deck configuration
- Helios Internal preparation

**Total time for full setup:** 1-2 hours
**But Atlas basics work in:** 30 minutes

---

**I'm ready when you are!** 🚀
