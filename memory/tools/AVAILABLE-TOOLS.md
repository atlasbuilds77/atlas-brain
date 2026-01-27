# AVAILABLE TOOLS - Read This Every Session

**Purpose:** Ensure all models (Claude, GPT, DeepSeek, etc.) know what tools exist

---

## BROWSER AUTOMATION

### Peekaboo (macOS UI Automation)
- **Location:** `/opt/homebrew/bin/peekaboo`
- **Purpose:** Control macOS apps, click buttons, fill forms, capture screenshots
- **Use when:** Need to interact with desktop apps, browsers without API
- **Skill:** `memory/../skills/peekaboo/SKILL.md` (if it exists)

### Clawdbot Browser Tool
- **Purpose:** Control Chrome/Firefox via CDP
- **Use when:** Web scraping, form filling, automated browsing
- **Profiles:** `clawd` (isolated), `chrome` (extension relay)

---

## TRADING TOOLS

### Kalshi
- **Location:** `~/clawd/tools/kalshi-trader.py`
- **API Key:** Set via `KALSHI_API_KEY_ID` env var (in ~/.zshrc)
- **Commands:**
  ```bash
  cd ~/clawd && source .venv/bin/activate
  export KALSHI_API_KEY_ID="0007b9f0-89c9-42b4-93bd-f98fbf1596b8"
  python tools/kalshi-trader.py balance
  python tools/kalshi-trader.py positions
  python tools/kalshi-trader.py markets "weather"
  python tools/kalshi-trader.py buy TICKER quantity
  ```

### Alpaca (Paper Trading)
- **Location:** `~/clawd/atlas-trader/cli.js`
- **Account:** PA3ZJ1WMN69R
- **Commands:**
  ```bash
  cd ~/clawd/atlas-trader
  node cli.js account
  node cli.js positions
  node cli.js quote SYMBOL
  node cli.js buy SYMBOL qty [limit] [price]
  node cli.js close SYMBOL
  ```

### Crypto - Solana Wallet
- **Wallet:** `7UKP7mofxSk6mn4z4jQNNE7HZSdXTPkMY8VKypZcrafx`
- **Keypair:** `~/clawd/drift-bot/.secrets/solana-keypair.json`
- **Commands:**
  ```bash
  solana balance 7UKP7mofxSk6mn4z4jQNNE7HZSdXTPkMY8VKypZcrafx
  spl-token accounts --owner 7UKP7mofxSk6mn4z4jQNNE7HZSdXTPkMY8VKypZcrafx
  spl-token balance So11111111111111111111111111111111111111112 --owner [wallet]
  ```

### Jupiter Swap (Solana DEX)
- **Script:** `~/clawd/tools/jupiter-swap.py`
- **Usage:** Swap tokens on Solana
- **Note:** Network issues possible, use Phantom wallet UI as backup

### Drift Protocol (Leverage Trading)
- **Location:** `~/clawd/drift-bot/`
- **Python:** 3.12 (driftpy won't work on 3.14)
- **Purpose:** Perpetual futures on Solana
- **Status:** Setup but not actively trading

---

## FILE OPERATIONS

### Standard Tools
- `read` - Read file contents
- `write` - Create/overwrite files
- `edit` - Precise text replacement
- `exec` - Run shell commands

### CRITICAL: Follow Exact Paths
- If told "write to X file", use that EXACT path
- Confirm file location after writing
- Show tool output, don't paraphrase

---

## MESSAGING

### iMessage
- **Tool:** Built-in `message` tool
- **No Markdown:** iMessage shows literal asterisks - use CAPS, emojis, "quotes"
- **CLI:** `~/clawd/tools/imsg-enhanced.sh` (if needed)

### Telegram
- **Tool:** Built-in `message` tool
- **Markdown:** Supported

---

## VOICE & AUDIO

### OpenAI TTS
- **Location:** `~/clawd/skills/openai-tts/scripts/speak.sh`
- **Usage:**
  ```bash
  bash ~/clawd/skills/openai-tts/scripts/speak.sh "text" --voice onyx --out /tmp/x.mp3
  ```

### Whisper (Transcription)
- **Skill:** `openai-whisper` or `openai-whisper-api`
- **Purpose:** Audio → Text

---

## RESEARCH & WEB

### Web Search
- **Tool:** Built-in `web_search`
- **Provider:** Brave Search API

### Web Fetch
- **Tool:** Built-in `web_fetch`
- **Purpose:** Extract readable content from URLs

### Sparks (Sub-agents)
- **Tool:** `sessions_spawn`
- **Models:** Use `deepseek` for cost-effective research
- **Usage:**
  ```javascript
  sessions_spawn({
    task: "Research XYZ",
    model: "deepseek",
    label: "research-task-name"
  })
  ```

---

## MEMORY & CONTEXT

### Memory Files (READ EVERY SESSION)
1. `CURRENT_STATE.md` - Current status (trading, positions, capital)
2. `CURRENT-TRADING-STATUS.md` - Detailed trading state
3. `SESSION_START_CHECKLIST.md` - Boot sequence
4. `HEARTBEAT.md` - Regular checks

### Memory Search
- **Tool:** `memory_search("query")`
- **Purpose:** Find information in memory files before saying "I don't know"

---

## PHOTOS & IMAGES

### Node Camera
- **Tool:** `nodes` with `camera_snap` action
- **Purpose:** Take photos from paired iOS/Android devices

### Image Analysis
- **Tool:** `image` tool
- **Purpose:** Vision model analysis

---

## REMINDERS & SCHEDULING

### Cron Jobs
- **Tool:** `cron`
- **Actions:** add, list, remove, run
- **Purpose:** Schedule future tasks and reminders

---

## KEY PROTOCOLS

### Anti-Hallucination (TOP PRIORITY)
1. ✅ **Show tool output** - Never claim "done" without proof
2. ✅ **Follow exact paths** - Use specified file locations
3. ✅ **Verify results** - Check output before claiming success
4. ❌ **Don't paraphrase** - Show actual command results
5. ❌ **Don't ignore instructions** - Especially file paths

### Model-Specific Notes
- **GPT:** Often hallucinates, ignores instructions, forgets context
- **DeepSeek:** Good for Sparks/research, cheaper than Claude
- **Claude (Sonnet/Opus):** Most reliable, use for main session

---

## CRITICAL - LIVE PRICE CHECKS

**BEFORE ANY TRADE CALCULATION:**

### Check Live Prices
```bash
# Crypto
curl -s "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"

# Stocks
cd ~/clawd/atlas-trader && node cli.js quote SYMBOL

# Kalshi
python ~/clawd/tools/kalshi-trader.py markets "search"
```

**NEVER assume prices from memory (knowledge cutoff April 2024)**

See: `memory/protocols/live-price-check-protocol.md`

---

## TROUBLESHOOTING

### If a tool isn't working:
1. Check if it exists: `ls -la ~/clawd/tools/`
2. Check venv activation: `source ~/clawd/.venv/bin/activate`
3. Check API keys: `env | grep API`
4. Read skill docs: `memory/tools/[tool]-api.md`

### If you're on a non-Claude model:
- Read this file FIRST
- Follow anti-hallucination protocol STRICTLY
- Ask before assuming tool availability

---

*Last updated: 2026-01-26 12:56 PST*
*Update when new tools are added*
