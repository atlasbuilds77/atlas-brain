# Kalshi API Access

## Credentials Location
- **API Key ID:** Set via `KALSHI_API_KEY_ID` env var
- **Private Key:** `~/.kalshi/private_key.pem`
- **Alternative:** Can also be at `~/clawd/.kalshi/private_key.pem`

## Trading Tool
- **Location:** `~/clawd/tools/kalshi-trader.py`
- **Venv:** `~/clawd/.venv` (kalshi-python installed here)

## Usage
```bash
cd ~/clawd && source .venv/bin/activate

# Set API key (or add to ~/.zshrc)
export KALSHI_API_KEY_ID="your-key-id"

# Commands
python tools/kalshi-trader.py balance
python tools/kalshi-trader.py markets "chicago temperature"
python tools/kalshi-trader.py buy TICKER 10
python tools/kalshi-trader.py positions
```

## Demo vs Production
- Set `KALSHI_USE_DEMO=true` for paper trading
- Default is production (real money)

## API Docs
- https://docs.kalshi.com/python-sdk
- https://help.kalshi.com/kalshi-api

## Setup Steps
1. Go to https://kalshi.com/account/api
2. Generate API key
3. Download private key
4. Save to ~/.kalshi/private_key.pem
5. Export KALSHI_API_KEY_ID

---
*Created: 2026-01-25*
