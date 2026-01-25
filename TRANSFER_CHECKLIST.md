# Mac Mini Transfer Checklist

Use this before picking up the Mac Mini.

## Before You Leave

### On Current Mac
- [x] Created `MAC_MINI_SETUP.sh` (automated setup script)
- [x] Created `MAC_MINI_TRANSFER_GUIDE.md` (detailed guide)
- [x] Created `QUICK_START.md` (20-minute quick start)
- [x] Created `atlas-workspace-backup.tar.gz` (workspace backup)
- [ ] Export Clawdbot config:
  ```bash
  clawdbot config get > ~/clawd/clawdbot-config-export.json
  ```
- [ ] Export cron jobs:
  ```bash
  clawdbot cron list --json > ~/clawd/cron-jobs.json
  ```

### Files to Transfer
Copy these to USB drive or iCloud:
- [ ] `MAC_MINI_SETUP.sh`
- [ ] `MAC_MINI_TRANSFER_GUIDE.md`
- [ ] `QUICK_START.md`
- [ ] `atlas-workspace-backup.tar.gz`
- [ ] `clawdbot-config-export.json`
- [ ] `cron-jobs.json`

## At Apple Store / Pickup

### What to Buy/Get
- [x] Mac Mini M4 (16GB RAM)
- [ ] Power cable (should be included)
- [ ] HDMI/DisplayPort cable (if needed for setup)
- [ ] Keyboard/mouse (if not using existing)

### Optional
- [ ] USB-C hub (for extra ports)
- [ ] External SSD (for backups)
- [ ] Ethernet cable (faster than WiFi)

## At Home - Mac Mini Setup

### Phase 1: Physical Setup (2 min)
- [ ] Unbox Mac Mini
- [ ] Connect power
- [ ] Connect display/keyboard/mouse (temporarily)
- [ ] Power on

### Phase 2: macOS Initial Setup (5 min)
- [ ] Choose language/region
- [ ] Connect to WiFi
- [ ] Create Apple ID:
  - Email: **atlas.builds77@gmail.com**
  - Password: **AtlasSuperStrongPassword77** (or choose new one)
  - Security questions (save answers!)
- [ ] Create user account:
  - Name: **Atlas**
  - Username: **atlas**
  - Password: (same as Apple ID or different)
- [ ] Enable FileVault encryption
- [ ] Skip iCloud sync for now
- [ ] Complete setup wizard

### Phase 3: Transfer Files (3 min)
Choose one method:
- [ ] **USB Drive:** Copy all files from USB to Desktop
- [ ] **AirDrop:** Send from old Mac to new Mac
- [ ] **iCloud:** Upload/download via iCloud Drive

### Phase 4: Run Setup Script (10 min)
```bash
cd ~/Desktop
chmod +x MAC_MINI_SETUP.sh
./MAC_MINI_SETUP.sh
```
- [ ] Script runs without errors
- [ ] All tools installed

### Phase 5: Manual Steps (15 min)

#### Chrome & Gmail
- [ ] Open Chrome
- [ ] Login to atlas.builds77@gmail.com
- [ ] Enable sync
- [ ] Keep Chrome open

#### Twitter
- [ ] Go to x.com in Chrome
- [ ] Login to @Atlas_builds
- [ ] Check "Remember me"
- [ ] Verify bird CLI works:
  ```bash
  bird whoami
  ```

#### GitHub
```bash
gh auth login
```
- [ ] Choose: GitHub.com
- [ ] Choose: HTTPS
- [ ] Choose: Login with web browser
- [ ] Copy one-time code
- [ ] Paste in browser
- [ ] Confirm authentication
- [ ] Test: `gh auth status`

#### Restore Workspace
```bash
cd ~/clawd
tar -xzf ~/Desktop/atlas-workspace-backup.tar.gz
```
- [ ] Files extracted successfully
- [ ] Check: `ls ~/clawd/memory/`

#### Configure Clawdbot
```bash
clawdbot config apply < ~/Desktop/clawdbot-config-export.json
```
- [ ] Config applied successfully
- [ ] Or run: `clawdbot configure` and enter manually

#### Clone FuturesRelay
```bash
cd ~/clawd
gh repo clone OrionSolana/Futures-relay
```
- [ ] Repo cloned
- [ ] Test: `ls ~/clawd/Futures-relay/`

#### Restore Cron Jobs
- [ ] Import cron jobs (if exported)
- [ ] Or recreate manually via web UI

### Phase 6: Start Services (2 min)
```bash
clawdbot daemon start
```
- [ ] Daemon started successfully
- [ ] Visit http://localhost:18789
- [ ] Dashboard loads

### Phase 7: iMessage Setup (3 min)
- [ ] Open Messages app
- [ ] Sign in with Atlas Apple ID
- [ ] Send test message to Orion: "Mac Mini setup complete!"

### Phase 8: Final Testing (5 min)

#### Test All Services
```bash
# Clawdbot
clawdbot status

# GitHub
gh repo list atlasbuilds77

# Twitter
bird whoami
bird followers --count 1

# Check workspace
ls ~/clawd/memory/
```

#### Send Test Messages
Via Telegram:
- [ ] "Atlas, you awake on the Mac Mini?"
- [ ] Atlas responds via Telegram

Via iMessage (NEW!):
- [ ] Send "Test iMessage from Mac Mini"
- [ ] Atlas responds via iMessage

#### Verify Cron Jobs
- [ ] Twitter engagement running
- [ ] Market monitoring active
- [ ] Check cron logs in web UI

---

## Success Criteria

All should be ✅:
- [ ] Mac Mini powered on and running macOS
- [ ] Apple ID created for Atlas
- [ ] All tools installed (Homebrew, Node, Clawdbot, gh, bird)
- [ ] Chrome logged into Gmail
- [ ] Twitter logged in via Chrome
- [ ] GitHub authenticated
- [ ] Workspace restored to ~/clawd
- [ ] FuturesRelay cloned
- [ ] Clawdbot daemon running
- [ ] iMessage configured
- [ ] Telegram messages working
- [ ] iMessage messages working
- [ ] Twitter automation posting
- [ ] Cron jobs active

---

## If You Get Stuck

1. Check `~/clawd/QUICK_START.md` for fast reference
2. Check `~/clawd/MAC_MINI_TRANSFER_GUIDE.md` for details
3. Check logs: `clawdbot daemon logs`
4. Message Atlas via Telegram (if daemon is running)
5. Restart: `clawdbot daemon restart`

---

## Total Time Estimate

- macOS setup: **5 minutes**
- File transfer: **3 minutes**
- Automated setup: **10 minutes**
- Manual steps: **15 minutes**
- Testing: **5 minutes**

**Total: ~40 minutes** (conservatively)

With script automation, could be as fast as **20-25 minutes**.

---

## Post-Setup

Once everything works:
- [ ] Enable automatic macOS updates
- [ ] Set screen lock timeout
- [ ] Configure Energy Saver (never sleep)
- [ ] Set up Time Machine backups (optional)
- [ ] Remove temporary display/keyboard if using headless

---

## Headless Operation (Optional)

Once setup is complete, Mac Mini can run headless (no display):

1. Enable remote access:
   - System Settings → Sharing → Screen Sharing: ON
   - System Settings → Sharing → Remote Login: ON

2. Access from your MacBook:
   ```bash
   ssh atlas@[mac-mini-ip]
   ```
   Or use Screen Sharing app

3. Disconnect display/keyboard - Mac Mini runs 24/7

---

## Notes

- Setup is designed to be **copy-paste simple**
- Most steps are automated via script
- Manual steps are unavoidable (need browser logins)
- Once done, Mac Mini is **always-on Atlas workstation**
- Can monitor/control via Telegram or iMessage
- Way faster and more reliable than cloud hosting

---

**Let's do this! 🚀**
