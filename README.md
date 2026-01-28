# Chrome Automation Stealth Fix - Complete Package

**Purpose:** Fix Chrome blocking Jupiter wallet extension during Clawdbot automation  
**Created:** January 27, 2025  
**Status:** ✅ Ready for Implementation

---

## 🚀 Quick Start (5 minutes)

```bash
cd /Users/atlasbuilds/clawd

# Run the installer
./fix-chrome-stealth.sh

# Choose option 1 (Extension Profile) for safest approach
# OR
# Choose option 2 (Code Patch) for automated approach

# Follow on-screen instructions
```

---

## 📚 Documentation Files

### 1. **SUMMARY.md** ⭐ Start here
Executive summary with:
- Problem statement
- Two solutions (pros/cons)
- Immediate action plan
- Testing checklist
- Risk assessment

**Read this first if you want the TL;DR**

### 2. **chrome-stealth-quickref.md**
Quick reference guide:
- Setup commands
- Troubleshooting
- Key file locations
- Command cheatsheet

**Use this during implementation**

### 3. **chrome-automation-fix-findings.md**
Deep technical analysis (12KB):
- How Clawdbot launches Chrome
- Configuration system internals
- Why detection happens
- All solution options
- Code modifications
- Testing procedures

**Read this if you want to understand the why**

### 4. **architecture-diagram.md**
Visual diagrams showing:
- Current broken architecture
- Solution 1 flow (Extension)
- Solution 2 flow (Code Patch)
- Detection mechanisms
- Decision matrix

**Read this for visual understanding**

### 5. **fix-chrome-stealth.sh** (Executable)
Automated installer that:
- Creates Chrome launch script with stealth flags
- Patches Clawdbot code (optional)
- Creates backups
- Provides interactive menu

**Run this to apply fixes**

### 6. **README.md** (This file)
Index and navigation guide

---

## 🎯 Problem Summary

**What's broken:**
- Clawdbot's browser automation triggers Chrome's bot detection
- Jupiter wallet extension is blocked with ERR_BLOCKED_BY_CLIENT
- Works fine on phone, fails on desktop

**Why:**
- Chrome launches with standard automation flags
- Sets `navigator.webdriver = true`
- Jupiter detects automation and blocks

**Solution:**
Add stealth flags to Chrome launch to hide automation signals

---

## 🛠️ Two Solutions

### Solution 1: Extension Profile (Recommended ⭐)

**Concept:** Use your own Chrome + Clawdbot's extension

**Pros:**
- ✅ No system modifications
- ✅ Full control over flags
- ✅ Survives updates

**Cons:**
- ⚠️ Manual Chrome launch

**Setup:**
```bash
./fix-chrome-stealth.sh  # Choose 1
~/launch-chrome-jupiter.sh
# Load extensions, attach Clawdbot
```

### Solution 2: Code Patch

**Concept:** Modify Clawdbot to always use stealth flags

**Pros:**
- ✅ Automatic
- ✅ Standard workflow

**Cons:**
- ⚠️ Requires sudo
- ⚠️ Lost on updates

**Setup:**
```bash
./fix-chrome-stealth.sh  # Choose 2
clawdbot gateway restart
```

---

## 📊 File Structure

```
/Users/atlasbuilds/clawd/
├── README.md                         ← You are here
├── SUMMARY.md                        ← Executive summary
├── chrome-stealth-quickref.md        ← Quick commands
├── chrome-automation-fix-findings.md ← Technical deep dive
├── architecture-diagram.md           ← Visual diagrams
└── fix-chrome-stealth.sh            ← Installer script

Generated after running installer:
├── ~/launch-chrome-jupiter.sh       ← Chrome launcher (if using Extension)
└── /opt/.../chrome.js.backup-*      ← Backup (if using Code Patch)
```

---

## 🎓 Reading Order

### For Operators (Just want it to work)
1. Read: **SUMMARY.md** (5 min)
2. Run: **./fix-chrome-stealth.sh** (5 min)
3. Reference: **chrome-stealth-quickref.md** (as needed)

### For Developers (Want to understand)
1. Read: **SUMMARY.md** (5 min)
2. Read: **chrome-automation-fix-findings.md** (20 min)
3. Review: **architecture-diagram.md** (10 min)
4. Run: **./fix-chrome-stealth.sh** (5 min)

### For Security/Compliance
1. Read: **SUMMARY.md** → Risk Assessment section
2. Review: **chrome-automation-fix-findings.md** → Security implications
3. Check: Code patch diff before applying

---

## ✅ Implementation Checklist

- [ ] Read SUMMARY.md
- [ ] Backup current Clawdbot: `sudo cp -r /opt/homebrew/lib/node_modules/clawdbot /opt/homebrew/lib/node_modules/clawdbot.backup`
- [ ] Choose solution (Extension or Code Patch)
- [ ] Run: `./fix-chrome-stealth.sh`
- [ ] Test detection: Visit https://bot.sannysoft.com/
- [ ] Test Jupiter: Load wallet and try transaction
- [ ] Document any issues encountered
- [ ] (Optional) File feature request with Clawdbot

---

## 🧪 Testing Resources

### Detection Test Sites:
- https://bot.sannysoft.com/ - Comprehensive
- https://arh.antoinevastel.com/bots/areyouheadless - Headless detection
- https://pixelscan.net/ - Bot detection
- https://abrahamjuliot.github.io/creepjs/ - Fingerprinting

### Expected Results:
- ✅ navigator.webdriver: `undefined` (not `true`)
- ✅ Chrome driver: Not detected
- ✅ Automation: Not detected

---

## 🔧 Key Commands

```bash
# Browser status
clawdbot browser status

# Extension profile (if using Solution 1)
clawdbot browser --browser-profile chrome tabs

# Clawd profile (if using Solution 2)
clawdbot browser --browser-profile clawd start

# Test automation detection
clawdbot browser open https://bot.sannysoft.com/
clawdbot browser screenshot --full-page

# Restart gateway
clawdbot gateway restart

# View logs
clawdbot logs
```

---

## 🆘 Troubleshooting

### Extension won't attach
```bash
# Check relay is running
clawdbot browser status
# Should show: running: true

# Reinstall extension
clawdbot browser extension install
```

### Jupiter still blocks
```bash
# Try combining both solutions
./fix-chrome-stealth.sh  # Run twice, use both options

# Add more flags to launch script
nano ~/launch-chrome-jupiter.sh
# Add: --disable-web-security (testing only)
```

### Code patch lost after update
```bash
# Re-run patcher
./fix-chrome-stealth.sh  # Choose option 2
```

### Rollback if broken
```bash
# Extension method: Just close Chrome, use normal browser
rm ~/launch-chrome-jupiter.sh

# Code patch: Restore backup
sudo cp /opt/homebrew/lib/node_modules/clawdbot/dist/browser/chrome.js.backup-* \
       /opt/homebrew/lib/node_modules/clawdbot/dist/browser/chrome.js
clawdbot gateway restart
```

---

## 📈 Success Metrics

| Metric | Target | How to Verify |
|--------|--------|---------------|
| Detection Pass | 100% | Visit bot.sannysoft.com |
| Jupiter Load | Success | Extension loads without errors |
| Transaction | Success | Can execute test trade |
| Uptime | 95%+ | Monitor for random blocks |

---

## 🔮 Future Enhancements

### Short-term:
- [ ] Create post-update script to auto-reapply patch
- [ ] Document Jupiter-specific edge cases
- [ ] Test with other DeFi platforms

### Long-term:
- [ ] File Clawdbot feature request for `browser.launchOptions.args`
- [ ] Investigate residential proxy integration
- [ ] Build detection monitoring dashboard

---

## 🔗 External Resources

### Clawdbot:
- Docs: `/opt/homebrew/lib/node_modules/clawdbot/docs/`
- Browser tool: `docs/tools/browser.md`
- Extension: `docs/tools/chrome-extension.md`

### Chrome:
- Flags reference: https://peter.sh/experiments/chromium-command-line-switches/
- DevTools Protocol: https://chromedevtools.github.io/devtools-protocol/

### Stealth:
- Playwright stealth: https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-stealth
- Detection techniques: https://bot.sannysoft.com/

---

## 🤝 Contributing

Found an issue or improvement?

1. Document the problem in findings doc
2. Test solution thoroughly
3. Update relevant docs
4. Share findings with team

---

## 📜 License & Disclaimer

**This is a workaround for automation detection.**

- ⚠️ Use responsibly
- ⚠️ Some sites prohibit automation (check ToS)
- ⚠️ Financial sites have fraud protection (understand risks)
- ⚠️ No guarantees (detection methods evolve)

**For legitimate use cases only** (personal trading automation, testing, etc.)

---

## 📞 Support Contacts

- **Technical Issues:** Check troubleshooting section above
- **Clawdbot Issues:** File issue with Clawdbot maintainers
- **Jupiter Issues:** Check Jupiter Discord/support
- **Security Concerns:** Review risk assessment in SUMMARY.md

---

## 🏆 Credits

**Research & Implementation:** Deep dive investigation of Clawdbot's browser automation system  
**Tools Used:** Clawdbot, Chrome DevTools Protocol, Playwright  
**Testing Sites:** bot.sannysoft.com, pixelscan.net  

---

## 📅 Version History

- **2025-01-27:** Initial research and documentation
  - Identified root cause
  - Created two solutions
  - Wrote comprehensive documentation
  - Built automated installer

---

## 🎯 Next Actions

**Immediate (Today):**
1. Run `./fix-chrome-stealth.sh`
2. Choose Extension Profile (safer)
3. Test with Jupiter
4. Document results

**This Week:**
1. If successful, document workflow
2. Create automation scripts
3. Monitor for any blocks

**This Month:**
1. File feature request with Clawdbot
2. Investigate other stealth techniques
3. Build monitoring dashboard

---

**Status:** ✅ Complete and ready for testing  
**Confidence:** High (based on thorough analysis)  
**Timeline:** 15-30 minutes to implement and verify

---

## 🔍 Quick Links

- [Executive Summary](SUMMARY.md)
- [Quick Reference](chrome-stealth-quickref.md)
- [Technical Analysis](chrome-automation-fix-findings.md)
- [Visual Diagrams](architecture-diagram.md)
- [Installer Script](fix-chrome-stealth.sh)

---

**Last Updated:** 2025-01-27  
**Status:** Ready for production use  
**Tested:** No (awaiting user testing)
