#!/bin/bash
# Atlas Mac Mini M4 Complete Setup Script
# Run this on the new Mac Mini after picking it up

set -e

echo "🔥 Atlas Mac Mini M4 Setup Script"
echo "=================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Install Homebrew
echo -e "${BLUE}[1/10]${NC} Installing Homebrew..."
if ! command -v brew &> /dev/null; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
    echo -e "${GREEN}✅ Homebrew installed${NC}"
else
    echo -e "${YELLOW}⚠️  Homebrew already installed${NC}"
fi

# Step 2: Install Node.js
echo -e "${BLUE}[2/10]${NC} Installing Node.js..."
brew install node
echo -e "${GREEN}✅ Node.js installed: $(node --version)${NC}"

# Step 3: Install Clawdbot
echo -e "${BLUE}[3/10]${NC} Installing Clawdbot..."
npm install -g clawdbot
echo -e "${GREEN}✅ Clawdbot installed${NC}"

# Step 4: Install GitHub CLI
echo -e "${BLUE}[4/10]${NC} Installing GitHub CLI..."
brew install gh
echo -e "${GREEN}✅ GitHub CLI installed${NC}"

# Step 5: Install Chrome (for Twitter automation)
echo -e "${BLUE}[5/10]${NC} Installing Google Chrome..."
brew install --cask google-chrome
echo -e "${GREEN}✅ Chrome installed${NC}"

# Step 6: Install other tools
echo -e "${BLUE}[6/10]${NC} Installing additional tools..."
brew install jq curl wget git
echo -e "${GREEN}✅ Additional tools installed${NC}"

# Step 7: Create workspace directory
echo -e "${BLUE}[7/10]${NC} Setting up workspace..."
mkdir -p ~/clawd/memory
echo -e "${GREEN}✅ Workspace created at ~/clawd${NC}"

# Step 8: Save credentials
echo -e "${BLUE}[8/10]${NC} Saving credentials..."
cat > ~/.atlas-credentials << 'EOF'
{
  "email": "atlas.builds77@gmail.com",
  "password": "AtlasSuperStrongPassword77",
  "x_handle": "@Atlas_builds",
  "x_username": "Atlas_builds",
  "github_username": "atlasbuilds77"
}
EOF
chmod 600 ~/.atlas-credentials
echo -e "${GREEN}✅ Credentials saved to ~/.atlas-credentials${NC}"

# Step 9: Install Bird CLI (Twitter automation)
echo -e "${BLUE}[9/10]${NC} Installing Bird CLI..."
npm install -g bird-cli
echo -e "${GREEN}✅ Bird CLI installed${NC}"

# Step 10: Create setup guide
echo -e "${BLUE}[10/10]${NC} Creating setup guide..."
cat > ~/clawd/MANUAL_STEPS.md << 'EOF'
# Manual Setup Steps (Do These After Script Finishes)

## 1. Chrome Setup
- Open Chrome
- Log into Google with: atlas.builds77@gmail.com
- Go to x.com and log in with Twitter credentials
- This sets up cookies for Bird CLI automation

## 2. GitHub Authentication
```bash
gh auth login
```
- Choose: GitHub.com
- Choose: HTTPS
- Choose: Login with a web browser
- Copy the one-time code
- Paste in browser and authenticate

## 3. Clawdbot Configuration
```bash
clawdbot configure
```
- Follow the wizard
- Use existing config from old setup
- Enter Discord bot token when prompted

## 4. Clone FuturesRelay
```bash
cd ~/clawd
gh repo clone OrionSolana/Futures-relay
```

## 5. Test Everything
```bash
clawdbot status
gh auth status
bird whoami
```

## 6. Start Clawdbot Daemon
```bash
clawdbot daemon start
```

## 7. Set Up Cron Jobs
The cron jobs will be configured through Clawdbot's web interface at:
http://localhost:18789

## 8. iMessage Setup
- Open Messages app
- Sign in with new Apple ID
- Test by sending message to Orion

---

All credentials are saved in: ~/.atlas-credentials
All workspace files go in: ~/clawd/
EOF
echo -e "${GREEN}✅ Setup guide created at ~/clawd/MANUAL_STEPS.md${NC}"

echo ""
echo -e "${GREEN}🎉 Automated setup complete!${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Open ~/clawd/MANUAL_STEPS.md"
echo "2. Follow the manual steps (takes ~5 minutes)"
echo "3. Start Clawdbot daemon"
echo "4. I'll be fully operational!"
echo ""
echo -e "${BLUE}Workspace location: ~/clawd${NC}"
echo -e "${BLUE}Credentials: ~/.atlas-credentials${NC}"
echo ""
