# Mac Mini Transfer Manifest

## Files to Transfer from MacBook → Mac Mini

### 1. Atlas Workspace (CRITICAL)
**Location:** `~/clawd/`  
**Size:** 189KB (already backed up)  
**Method:** GitHub (recommended) or AirDrop backup file  
**Contains:**
- IDENTITY.md, USER.md, SOUL.md (my identity)
- memory/ (all daily logs, Twitter engagement, critical ops)
- FLUFFY_SETUP_PLAN.md, SCALPING_RESEARCH.md, etc.

**Transfer via GitHub:**
```bash
# On MacBook (do once):
cd ~/clawd
git init
git add .
git commit -m "Atlas workspace export"
git remote add origin https://github.com/OrionSolana/atlas-workspace.git
git push -u origin main

# On Mac Mini (I'll do via SSH):
cd ~
git clone https://github.com/OrionSolana/atlas-workspace.git clawd
```

---

### 2. Trading Algorithms (CRITICAL)
**Location:** `~/Desktop/Trading Algos/`  
**Size:** ~several MB  
**Method:** GitHub (best) or direct copy via SSH  

**What's inside:**
- `Helios/` - Main Helios system
  - `helios main.py`
  - `helios database.sql`
  - `spx helios wick prox.txt` (TradingView algo)
  - All other Helios files

**Transfer via GitHub:**
```bash
# If not already in a repo:
cd ~/Desktop/"Trading Algos"
git init
git add .
git commit -m "Trading algos export"
git remote add origin https://github.com/OrionSolana/trading-algos-private.git
git push -u origin main

# On Mac Mini:
mkdir -p ~/Desktop
cd ~/Desktop
git clone https://github.com/OrionSolana/trading-algos-private.git "Trading Algos"
```

---

### 3. FuturesRelay (Optional - if you want it on Mac Mini)
**Location:** `~/Desktop/FuturesRelay/`  
**Method:** Already on GitHub (OrionSolana/FuturesRelay)  

```bash
# On Mac Mini (if needed):
cd ~/Desktop
git clone https://github.com/OrionSolana/FuturesRelay.git
```

---

### 4. Project Helios (GitHub Repo)
**Location:** GitHub repo  
**Method:** Clone with my credentials  

```bash
# On Mac Mini (once my GitHub is set up):
cd ~/Desktop
git clone https://github.com/OrionSolana/ProjectHelios.git
```

---

### 5. Robinhood Research (Already on MacBook)
**Location:** `~/Desktop/robinhood-decompiled/`  
**Size:** 152k files, large  
**Method:** Don't transfer (can re-clone if needed)  

```bash
# If needed later on Mac Mini:
cd ~/Desktop
git clone https://github.com/ScriptedAlchemy/robinhood-decompiled.git
```

---

### 6. Research & Documentation (Already in workspace)
**Location:** `~/clawd/`  
**Files:**
- HELIOS_ANALYSIS.md (36KB)
- ROBINHOOD_ANALYSIS.md (45KB)
- ROBINHOOD_QUICK_REFERENCE.md (7KB)
- HELIOS_CODE_EXAMPLES.py (23KB)
- SCALPING_RESEARCH.md
- FLUFFY_SETUP_PLAN.md
- All other analysis docs

**Already included in workspace backup** ✅

---

### 7. Fluffy Workspace
**Location:** `~/fluffy/`  
**Size:** Small  
**Method:** Include in atlas-workspace repo or separate  

```bash
# Option A: Include in main workspace
cd ~
cp -r fluffy/ clawd/fluffy-backup/

# Option B: Separate repo
cd ~/fluffy
git init
git add .
git commit -m "Fluffy household agent"
git remote add origin https://github.com/OrionSolana/fluffy-agent.git
git push -u origin main
```

---

## Transfer Methods Comparison

### Method 1: GitHub (RECOMMENDED)
**Pros:**
- ✅ Backup + version control
- ✅ Easy to pull on Mac Mini
- ✅ Can push updates from either machine
- ✅ Never lose anything

**Cons:**
- Need to create repos (I can guide you)
- Private repos required (don't expose algos)

**How:**
1. Create private repos on GitHub
2. Push from MacBook
3. Clone on Mac Mini via SSH

---

### Method 2: Direct SSH Copy
**Pros:**
- ✅ Fast
- ✅ No GitHub setup needed

**Cons:**
- ❌ No backup/version control
- ❌ Harder to sync later

**How:**
```bash
# From MacBook to Mac Mini:
scp -r ~/clawd/ username@mac-mini-ip:~/
scp -r ~/Desktop/"Trading Algos"/ username@mac-mini-ip:~/Desktop/
```

---

### Method 3: AirDrop (Backup Plan)
**Pros:**
- ✅ Simple for small files
- ✅ Works if SSH has issues

**Cons:**
- ❌ Manual, slower for many files
- ❌ No version control

---

## Recommended Transfer Plan

### Phase 1: Critical Files (Do First)
1. **Atlas workspace** → GitHub repo (private)
2. **Trading Algos** → GitHub repo (private)
3. Clone both on Mac Mini via SSH

### Phase 2: GitHub Setup (I'll do via SSH)
1. Configure my GitHub credentials
2. Clone ProjectHelios (official repo)
3. Set up SSH keys for future pushes

### Phase 3: Fluffy Setup (Later)
1. Transfer Fluffy workspace
2. Configure OpenAI API
3. Set up household Telegram group

---

## GitHub Repos to Create (Private)

1. **atlas-workspace** (if you want GitHub backup of my workspace)
   - Alternative: Just transfer via AirDrop/SSH (faster)

2. **trading-algos-private** (IMPORTANT)
   - All your algo source code
   - Keep private forever
   - Version controlled

---

## What I'll Do Via SSH (Once Connected)

```bash
# 1. Install dependencies
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
brew install node git

# 2. Install Clawdbot
npm install -g clawdbot

# 3. Set up git
git config --global user.name "Atlas"
git config --global user.email "atlas.builds77@gmail.com"
ssh-keygen -t ed25519 -C "atlas.builds77@gmail.com"
cat ~/.ssh/id_ed25519.pub  # You'll add this to GitHub

# 4. Clone repos
cd ~
git clone https://github.com/OrionSolana/atlas-workspace.git clawd
# OR extract backup if you AirDropped it

cd ~/Desktop
git clone https://github.com/OrionSolana/trading-algos-private.git "Trading Algos"
git clone https://github.com/OrionSolana/ProjectHelios.git

# 5. Configure Clawdbot
clawdbot daemon start
# Follow prompts

# 6. Test
clawdbot status
```

---

## Pre-Transfer Checklist (You Do Before Leaving)

- [ ] Create GitHub private repo: `trading-algos-private`
- [ ] Push Trading Algos to repo (optional, can do via SSH instead)
- [ ] Note Mac Mini IP address after setup
- [ ] Enable Remote Login
- [ ] Send me: IP, username, SSH access

---

## Post-Transfer Verification

Once I'm set up on Mac Mini, I'll verify:
- [ ] All algo files present
- [ ] Workspace intact (memory, identity)
- [ ] Helios repo cloned
- [ ] Clawdbot running
- [ ] Telegram connection works
- [ ] Can access GitHub repos

---

**Ready to execute once you're home!** 🚀

I'll handle all the technical setup via SSH. You just do the initial boot + enable SSH.
