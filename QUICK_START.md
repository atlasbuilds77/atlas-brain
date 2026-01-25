# Atlas Mac Mini - Quick Start Card

**Print this or keep on phone during setup!**

---

## 🚀 The 20-Minute Setup

### Step 1: Initial macOS Setup (5 min)
1. Power on Mac Mini
2. Create Apple ID: **atlas.builds77@gmail.com**
3. Username: **atlas**
4. Set password (save it!)

### Step 2: Run Automated Script (10 min)
```bash
cd ~/Desktop
chmod +x MAC_MINI_SETUP.sh
./MAC_MINI_SETUP.sh
```
Enter admin password when asked. Script installs everything.

### Step 3: Manual Logins (5 min)
1. **Chrome:** Login to atlas.builds77@gmail.com
2. **Twitter:** Login to @Atlas_builds at x.com
3. **GitHub:**
   ```bash
   gh auth login
   ```
   Choose: Web browser → Copy code → Paste in browser

### Step 4: Transfer Files
Copy from old Mac:
- `atlas-workspace-backup.tar.gz` 
- `clawdbot-config.json`
- `cron-jobs.json`

Extract workspace:
```bash
cd ~/clawd
tar -xzf ~/Desktop/atlas-workspace-backup.tar.gz
```

### Step 5: Start Clawdbot
```bash
clawdbot config apply < ~/clawd/clawdbot-config.json
clawdbot daemon start
```

### Step 6: Test
Send Telegram message: "Atlas, you alive on the Mac Mini?"

---

## ✅ Success Checklist

- [ ] Mac Mini powered on
- [ ] Apple ID created
- [ ] Setup script ran successfully
- [ ] Chrome logged into Gmail
- [ ] Twitter logged in
- [ ] GitHub authenticated (`gh auth status` shows ✓)
- [ ] Workspace files transferred
- [ ] Clawdbot daemon running (`clawdbot status`)
- [ ] Telegram message received
- [ ] iMessage set up

---

## 🆘 If Something Breaks

**Daemon won't start?**
```bash
clawdbot daemon logs
```

**GitHub auth failed?**
```bash
gh auth logout
gh auth login
```

**Can't find workspace?**
```bash
ls ~/clawd/memory/
```

**Twitter not working?**
System Settings → Privacy → Full Disk Access → Add Terminal

---

## 📞 Credentials

Email: atlas.builds77@gmail.com  
Password: (saved in ~/.atlas-credentials)  
GitHub: atlasbuilds77  
Twitter: @Atlas_builds  

All details: `cat ~/.atlas-credentials`

---

## 🎯 What You're Setting Up

1. **Clawdbot** - My brain (AI agent)
2. **GitHub CLI** - Code management
3. **Chrome** - Browser automation
4. **Bird CLI** - Twitter automation
5. **Cron jobs** - Scheduled tasks
6. **iMessage** - New way to reach me!

---

## ⏱️ Expected Timeline

- Initial setup: **5 minutes**
- Automated script: **10 minutes**
- Manual steps: **5 minutes**
- **Total: ~20 minutes**

Then I'm fully operational on dedicated hardware! 🔥

---

For detailed steps: See `MAC_MINI_TRANSFER_GUIDE.md`
