# Mac Mini M4 Setup Guide - Atlas Transfer

**Device:** Mac Mini M4 (16GB RAM, 256GB storage)  
**Pickup:** 2026-01-23 (Best Buy)  
**Purpose:** Dedicated workstation for Atlas + Fluffy + Helios Internal

---

## Pre-Transfer Checklist (Do Before Leaving Your MacBook)

### 1. Backup Current Workspace
```bash
# Create backup of entire workspace
cd ~
tar -czf clawd-backup-$(date +%Y%m%d).tar.gz clawd/

# Verify backup
ls -lh clawd-backup-*.tar.gz
```

### 2. Export Credentials (Manual - CRITICAL)

**Twitter (for bird CLI):**
1. Open Chrome → x.com (logged into @Atlas_builds)
2. DevTools (Cmd+Opt+I) → Network tab
3. Refresh page, find any request to x.com
4. Copy these cookies:
   - `auth_token`
   - `ct0`
5. Save to `~/clawd/CREDENTIALS.txt` (temporary, will delete after setup)

**OpenAI API Key (for Fluffy):**
- Go to platform.openai.com
- Create API key
- Save to `~/clawd/CREDENTIALS.txt`

**Telegram Bot Token (if needed):**
- Already configured in Clawdbot, but verify it's in config

### 3. Git Configuration Check
```bash
# Record your git config (will replicate for Atlas account)
git config --global user.name
git config --global user.email
```

---

## Mac Mini Initial Setup (At Home)

### Step 1: macOS Setup (5 minutes)
- **NO PASSWORD** (Orion's requirement - full access for Atlas)
- Apple ID: atlas.builds77@gmail.com
- Computer name: "Atlas-Workstation"
- Enable: Remote Login (for SSH access)
- Disable: Sleep, screensaver, auto-updates (always-on requirement)

### Step 2: Install Homebrew (2 minutes)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add to PATH
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### Step 3: Install Clawdbot (5 minutes)
```bash
# Install Node.js (required)
brew install node

# Install Clawdbot
npm install -g clawdbot

# Verify
clawdbot --version
```

### Step 4: Transfer Workspace (10 minutes)
```bash
# Option A: USB drive (fastest)
# 1. Copy clawd-backup-*.tar.gz to USB
# 2. On Mac Mini:
cd ~
cp /Volumes/USB_DRIVE/clawd-backup-*.tar.gz .
tar -xzf clawd-backup-*.tar.gz

# Option B: AirDrop (if same network)
# Just AirDrop the .tar.gz file, then extract

# Option C: Git (if workspace is a repo)
cd ~
git clone <your-private-repo> clawd

# Verify transfer
ls -la ~/clawd/
cat ~/clawd/IDENTITY.md  # Should show Atlas identity
```

### Step 5: Configure Clawdbot (10 minutes)
```bash
# Start gateway setup
clawdbot daemon start

# Configure via ~/.clawdbot/config.yaml
# (Will walk through interactively)
```

**Key config values:**
- **Workspace:** `/Users/[username]/clawd`
- **Default model:** `anthropic/claude-sonnet-4-5`
- **Telegram:** Use existing bot token
- **API keys:** Anthropic (already have)

### Step 6: Set Up Atlas GitHub Account (5 minutes)
```bash
# Configure git for atlas.builds77@gmail.com
git config --global user.name "Atlas"
git config --global user.email "atlas.builds77@gmail.com"

# Generate SSH key
ssh-keygen -t ed25519 -C "atlas.builds77@gmail.com"
# Press Enter for default location, no passphrase

# Add to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy output, go to GitHub → Settings → SSH Keys → Add
```

**GitHub account already exists** (Orion created it)
- Username: (need to confirm from Orion)
- Email: atlas.builds77@gmail.com
- Will add SSH key above

### Step 7: Configure Twitter Access (bird CLI) (5 minutes)
```bash
# Install bird CLI
brew install bird

# Set up auth tokens (from CREDENTIALS.txt)
export TWITTER_AUTH_TOKEN="<from DevTools>"
export TWITTER_CT0="<from DevTools>"

# Test
bird whoami
# Should show: @Atlas_builds

# Make permanent (add to ~/.zshrc)
echo 'export TWITTER_AUTH_TOKEN="..."' >> ~/.zshrc
echo 'export TWITTER_CT0="..."' >> ~/.zshrc
```

---

## Post-Setup: Deploy Services

### Deploy Atlas (Main Agent) - Port 18080
```bash
cd ~/clawd
clawdbot daemon restart

# Verify
clawdbot status
```

**Test Atlas:**
- Send Telegram message: "Hey Atlas, are you on the Mac Mini now?"
- Should respond immediately

### Deploy Fluffy (Household Agent) - Port 18081
```bash
cd ~/fluffy

# Get OpenAI API key (from CREDENTIALS.txt)
export OPENAI_API_KEY="sk-..."

# Configure Clawdbot gateway for Fluffy
# (Edit ~/.clawdbot/config.yaml, add second gateway on port 18081)

# Start Fluffy
clawdbot daemon start --profile fluffy
```

**Configure cron jobs:**
- Laura meds: 8:15 AM
- Orion meds: 9:45 AM
- Dog walk checks: 8 AM, 5:30 PM
- Daily summary: 9 PM

### Set Up Helios Internal (Later)
- Clone Helios repo (with Atlas GitHub credentials)
- Configure for internal use only
- Deploy scalping module
- Test with paper trading first

---

## Voice Assistant Setup (Optional, Later)

### Install Dependencies
```bash
brew install portaudio
pip3 install pyaudio speechrecognition pvporcupine
```

### Configure Wake Word
- Wake words: "Hey Atlas" or "Atlas"
- Speaker verification (only Orion's voice)
- Output: AirPlay to HomePod

### Auto-start on Boot
```bash
# Add to macOS Login Items
# Or create LaunchAgent plist
```

---

## Stream Deck Setup (Optional, Later)

### Install Stream Deck Software
- Download from Elgato website
- Configure 15-button layout

### Button Layout
**Row 1:** Status (health, tokens, sessions, voice toggle)  
**Row 2:** Actions (deploy, restart, backup, new session, halt)  
**Row 3:** Monitoring (logs, Twitter, focus mode, debug, health)

---

## Network & Remote Access

### Port Forwarding (Optional)
- If you want external access to services
- Configure router to forward ports 18080, 18081

### SSH Access
```bash
# Enable Remote Login (already done in macOS setup)
# Test from your MacBook:
ssh [username]@[Mac-Mini-IP]
```

### Tailscale (Recommended for secure access)
```bash
brew install tailscale
sudo tailscale up
```

---

## Cron Jobs to Configure

### Twitter Engagement (Every 2 hours)
```bash
crontab -e

# Add:
0 */2 * * * /usr/local/bin/clawdbot cron twitter-engagement
```

### Market Briefings (Weekday mornings)
```bash
# Already configured in Clawdbot cron system
# Verify with: clawdbot cron list
```

### Fluffy Reminders
```bash
# Laura meds: 8:15 AM daily
15 8 * * * /usr/local/bin/clawdbot message fluffy "Laura meds reminder"

# Orion meds: 9:45 AM daily
45 9 * * * /usr/local/bin/clawdbot message fluffy "Orion meds reminder"

# Dog walk check: 8 AM, 5:30 PM daily
0 8 * * * /usr/local/bin/clawdbot message fluffy "Morning walk check"
30 17 * * * /usr/local/bin/clawdbot message fluffy "Evening walk check"

# Daily summary: 9 PM
0 21 * * * /usr/local/bin/clawdbot message fluffy "Daily household summary"
```

---

## Security Considerations

**Since no password is set (Orion's requirement):**
- ✅ Physical access required (Mac Mini at home)
- ✅ Network access restricted (home network only)
- ⚠️ Enable FileVault encryption (disk encryption, still no login password)
- ⚠️ Firewall enabled (block incoming except SSH/needed ports)

**Credentials stored:**
- `~/.clawdbot/config.yaml` (Anthropic, Telegram, OpenAI keys)
- `~/.zshrc` (Twitter auth tokens)
- `~/.ssh/` (GitHub SSH keys)

**All stored locally, encrypted at rest (FileVault)**

---

## Testing Checklist (After Setup)

### Atlas
- [ ] Telegram message → instant response
- [ ] Twitter posting works (bird CLI)
- [ ] Memory files persist across restarts
- [ ] Cron jobs execute on schedule
- [ ] GitHub clone works (Helios repo)

### Fluffy
- [ ] Household Telegram group works
- [ ] Medication reminders fire correctly
- [ ] Pet care tracking logs properly
- [ ] OpenAI API calls work (cost check)

### System
- [ ] Mac Mini doesn't sleep
- [ ] Network stable
- [ ] Remote SSH access works
- [ ] Automatic restarts after crashes

---

## Rollback Plan (If Issues)

**If Mac Mini has problems:**
1. Atlas keeps running on your MacBook (backup)
2. Workspace is backed up (.tar.gz file)
3. Can restore to MacBook or different machine
4. No data loss (all memory files in workspace)

---

## Estimated Setup Time

- **Basic (Atlas only):** 30-45 minutes
- **Full (Atlas + Fluffy):** 1-2 hours
- **Complete (+ Voice + Stream Deck):** 3-4 hours

**Recommendation:** Start with Atlas, get that solid, then add Fluffy and extras.

---

## Next Steps After Mac Mini Setup

1. **Test everything for 24 hours** (make sure stable)
2. **Clone Helios repo** (with Atlas GitHub)
3. **Analyze fresh Helios code** (do proper research)
4. **Design Helios Internal** (scalping subsystem)
5. **Backtest scalping strategies** (momentum breakout)
6. **Paper trade for 2 weeks** (validate edge)
7. **Go live with 1 contract** (real money, small scale)

---

## Emergency Contacts

**If something breaks:**
- Clawdbot docs: /opt/homebrew/lib/node_modules/clawdbot/docs
- Clawdbot Discord: discord.com/invite/clawd
- GitHub issues: github.com/clawdbot/clawdbot

**If Atlas is unresponsive:**
```bash
# Restart gateway
clawdbot daemon restart

# Check logs
clawdbot logs

# Last resort: reboot Mac Mini
sudo reboot
```

---

**READY TO GO!** 🚀

Once you get home with the Mac Mini, follow this guide step-by-step. I'll be here to help via Telegram as you go through setup.
