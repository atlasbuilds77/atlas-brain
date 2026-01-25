# Atlas Mac Mini M4 Transfer Guide

Complete guide to setting up my dedicated workstation.

## Before You Pick It Up

### 1. Prepare Workspace Backup
On current machine, create transfer bundle:
```bash
cd ~/clawd
tar -czf atlas-workspace-backup.tar.gz \
  memory/ \
  AGENTS.md \
  SOUL.md \
  TOOLS.md \
  IDENTITY.md \
  USER.md \
  HEARTBEAT.md \
  BRIEF.md \
  *.sh \
  .clawdbot/ 2>/dev/null || true
```

### 2. Export Clawdbot Config
```bash
clawdbot config get > ~/clawd/clawdbot-config.json
```

### 3. List Current Cron Jobs
```bash
clawdbot cron list --json > ~/clawd/cron-jobs.json
```

## At Home With New Mac Mini

### Phase 1: Initial Setup (5 min)
1. **Unbox and power on Mac Mini**
2. **macOS Setup:**
   - Create new Apple ID for Atlas (use atlas.builds77@gmail.com)
   - Choose username: `atlas`
   - Set password (save to Orion's password manager)
3. **System Preferences:**
   - Enable FileVault encryption
   - Set screen lock to 5 minutes
   - Enable automatic updates

### Phase 2: Run Setup Script (10 min)
1. **Transfer setup script to Mac Mini:**
   - Use AirDrop, USB drive, or iCloud
   - Copy `MAC_MINI_SETUP.sh` to Mac Mini desktop

2. **Make executable and run:**
```bash
cd ~/Desktop
chmod +x MAC_MINI_SETUP.sh
./MAC_MINI_SETUP.sh
```

3. **Enter admin password when prompted** (for Homebrew install)

### Phase 3: Manual Steps (15 min)

#### 1. Chrome Login
```bash
open -a "Google Chrome" https://accounts.google.com
```
- Log into: atlas.builds77@gmail.com
- Password: (from ~/.atlas-credentials)
- Enable sync

#### 2. Twitter Login
```bash
open -a "Google Chrome" https://x.com
```
- Log into @Atlas_builds
- Keep "Remember me" checked
- Bird CLI will use these cookies

#### 3. GitHub Authentication
```bash
gh auth login
```
- Choose: GitHub.com → HTTPS → Login with web browser
- Copy one-time code
- Paste in browser → Authenticate
- Confirm success:
```bash
gh auth status
```

#### 4. Transfer Workspace Files
From old machine, SCP or AirDrop:
```bash
# On old machine:
scp ~/clawd/atlas-workspace-backup.tar.gz atlas@[mac-mini-ip]:~/Desktop/

# On Mac Mini:
cd ~/clawd
tar -xzf ~/Desktop/atlas-workspace-backup.tar.gz
```

Or use iCloud/USB drive.

#### 5. Clawdbot Configuration
```bash
# Option A: Use existing config
clawdbot config apply < ~/clawd/clawdbot-config.json

# Option B: Run wizard
clawdbot configure
```

Enter when prompted:
- Anthropic API key (from Orion)
- Discord bot token (from Orion)
- Telegram bot token (from config)
- Workspace: `/Users/atlas/clawd`

#### 6. Clone FuturesRelay
```bash
cd ~/clawd
gh repo clone OrionSolana/Futures-relay
cd Futures-relay
npm install
```

#### 7. Restore Cron Jobs
```bash
# Import cron jobs
clawdbot cron import < ~/clawd/cron-jobs.json
```

Or manually recreate:
- Twitter engagement (every 2 hours)
- SPX monitoring (every 15 min during market hours)
- Market briefings (6:30 AM, 1 PM, 8 PM PT)

### Phase 4: Testing (5 min)

#### Test GitHub
```bash
gh repo list atlasbuilds77
gh repo view OrionSolana/Futures-relay
```

#### Test Twitter
```bash
bird whoami
bird followers --count 1
```

#### Test Clawdbot
```bash
clawdbot status
clawdbot daemon start
```

Visit: http://localhost:18789
(Should show dashboard)

#### Test iMessage
- Open Messages app
- Sign in with Atlas Apple ID
- Send test message to Orion

### Phase 5: Go Live (2 min)

#### 1. Start Daemon
```bash
clawdbot daemon start
```

#### 2. Verify Services
```bash
clawdbot status
```

Should show:
- ✅ Daemon running
- ✅ Telegram connected
- ✅ iMessage configured (new!)
- ✅ Cron jobs active
- ✅ Twitter automation ready

#### 3. Test Communication
Send message via Telegram: "Atlas, you awake on the Mac Mini?"

---

## Troubleshooting

### Chrome cookies not working for Bird?
```bash
# Grant Terminal full disk access:
System Settings → Privacy & Security → Full Disk Access → Add Terminal
```

### Clawdbot daemon won't start?
```bash
clawdbot daemon logs
clawdbot doctor
```

### GitHub auth failing?
```bash
gh auth logout
gh auth login
```

### Cron jobs not running?
```bash
clawdbot cron list
clawdbot cron status
```

---

## Post-Setup Checklist

- [ ] Homebrew installed
- [ ] Node.js installed
- [ ] Clawdbot installed and configured
- [ ] GitHub CLI authenticated
- [ ] Chrome logged into Gmail
- [ ] Twitter logged in via Chrome
- [ ] Bird CLI working (`bird whoami`)
- [ ] Workspace restored to ~/clawd
- [ ] FuturesRelay cloned
- [ ] Cron jobs imported
- [ ] Daemon running
- [ ] iMessage configured
- [ ] Test message sent to Orion via Telegram
- [ ] Test message sent to Orion via iMessage
- [ ] Twitter engagement posting
- [ ] Market monitoring active

---

## What's New on Mac Mini

### Hardware Benefits
- **M4 chip** → Way faster than cloud VPS
- **16GB RAM** → Can run multiple services
- **Always on** → No more timeouts
- **Local storage** → Persistent database, no more wipes

### New Capabilities
- **iMessage** → Direct messaging to Orion
- **Better browser automation** → Chrome runs locally
- **Faster builds** → Local dev environment
- **Voice/audio** → Can use TTS, transcription
- **Camera access** → Can take photos if needed
- **Screen recording** → Can capture UI bugs

### Services Running
1. **Clawdbot daemon** (main agent)
2. **Cron jobs** (Twitter, market monitoring)
3. **GitHub CLI** (code management)
4. **Bird CLI** (Twitter automation)
5. **Chrome** (browser automation)

---

## Maintenance

### Daily
- Check `clawdbot status`
- Monitor cron job logs

### Weekly
- Update Clawdbot: `npm update -g clawdbot`
- Check for macOS updates

### Monthly
- Review cron job logs
- Clean up old workspace files
- Update GitHub CLI: `brew upgrade gh`

---

## Emergency Recovery

If something breaks catastrophically:

1. **Restart daemon:**
   ```bash
   clawdbot daemon restart
   ```

2. **Re-auth GitHub:**
   ```bash
   gh auth logout && gh auth login
   ```

3. **Reset Chrome cookies:**
   - Log out of x.com
   - Clear cookies
   - Log back in

4. **Restore workspace from backup:**
   ```bash
   cd ~/clawd
   tar -xzf atlas-workspace-backup.tar.gz
   ```

5. **Contact Orion via iMessage/Telegram**

---

## Credentials Reference

All stored in: `~/.atlas-credentials`

- **Email:** atlas.builds77@gmail.com
- **GitHub:** atlasbuilds77
- **Twitter:** @Atlas_builds
- **Workspace:** ~/clawd
- **Config:** ~/.clawdbot/

**Never commit .atlas-credentials to git!**
