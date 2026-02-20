"""
MERIDIAN V1 Configuration
"""
import json
import os
from pathlib import Path

# ── Paths ──
CREDS_PATH = Path("/Users/atlasbuilds/clawd/credentials.json")
BASE_DIR = Path(__file__).parent

# ── Load credentials ──
with open(CREDS_PATH) as f:
    _creds = json.load(f)

# ── Tradier ──
TRADIER_TOKEN = _creds["tradier"]["token"]
TRADIER_BASE_URL = _creds["tradier"].get("base_url", "https://api.tradier.com")
TRADIER_ACCOUNT = "6YB58399"  # Hunter — excluded ($0 balance)

# ── Multi-Account Copy Trading ──
TRADING_ACCOUNTS = [
    {
        "name": "aman",
        "account": _creds["tradier_clients"]["aman"]["account"],   # 6YB71689
        "token":   _creds["tradier_clients"]["aman"]["token"],
        "size_pct": 1.0,    # FULL PORT — Aman approved 2026-02-19
        "fallback_equity": 3714.91,  # hardwired — cash account, equity field always 0
    },
    {
        "name": "carlos",
        "account": _creds["tradier_clients"]["carlos"]["account"],  # 6YB71747
        "token":   _creds["tradier_clients"]["carlos"]["token"],
        "size_pct": 0.25,
        "fallback_equity": 365.00,   # hardwired — small account, 1 contract minimum
    },
]

# ── Telegram ──
# Telegram alerts — pull from credentials.json
TELEGRAM_BOT_TOKEN = os.environ.get("TITAN_TG_TOKEN", _creds.get("telegram_meridian", {}).get("bot_token", ""))
TELEGRAM_CHAT_ID = os.environ.get("TITAN_TG_CHAT", _creds.get("telegram_meridian", {}).get("chat_id", ""))

# ── Trading Parameters ──
SYMBOL = "QQQ"
MIN_PM_RANGE = 3.0            # Skip if PM range < $3 (weak levels)
MAX_RECLAIM_BARS = 5          # Must reclaim within 5 bars
OTM_OFFSET = 3.0              # $3 OTM strikes
POSITION_0DTE_PCT = 0.80      # 80% in 0DTE
POSITION_1DTE_PCT = 0.20      # 20% in 1DTE
MAX_LOSS_PCT = -0.50          # -50% stop loss
TRAIL_LEVELS = [
    (0.30, 0.00),             # At +30%, trail to breakeven (sell 1/3)
    (0.50, 0.15),             # At +50%, trail to +15% (sell half)
    (0.75, 0.35),             # At +75%, trail to +35% (sell 2/3)
]
SCALE_LEVELS = [
    (0.30, 1/3),              # +30% → sell 1/3
    (0.50, 0.50),             # +50% → sell half
    (0.75, 2/3),              # +75% → sell 2/3
    (1.00, 1.00),             # +100% → SELL ALL
]
SWEEP_COOLDOWN_SEC = 900      # 15 min cooldown per level
MAX_POSITION_SIZE = 5000      # Max $ per trade (configurable)

# ── Time Windows (ET) ──
PM_START_HOUR = 4             # Pre-market scan starts
PM_END_HOUR = 9
PM_END_MIN = 30
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MIN = 30
TRADE_END_HOUR = 10
TRADE_END_MIN = 30

# ── Cluster Detection ──
CLUSTER_LOOKBACK_DAYS = 15
CLUSTER_PROXIMITY_PCT = 0.002  # 0.2% proximity for clustering

# ── Logging ──
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ── Database Integration (Multi-Tenant) ──
# Query database for active Singularity user accounts
# Falls back to hardcoded TRADING_ACCOUNTS if DB unavailable/empty
try:
    from meridian_db import get_trading_accounts_with_fallback
    
    # Store original hardcoded accounts as fallback
    _HARDCODED_ACCOUNTS = TRADING_ACCOUNTS.copy()
    
    # Attempt to load from database (with fallback)
    TRADING_ACCOUNTS = get_trading_accounts_with_fallback(_HARDCODED_ACCOUNTS)
    
    # Log which source is being used
    if TRADING_ACCOUNTS == _HARDCODED_ACCOUNTS:
        import logging
        logging.getLogger("meridian.config").info("Using hardcoded trading accounts (DB unavailable or empty)")
    else:
        import logging
        logging.getLogger("meridian.config").info(f"Loaded {len(TRADING_ACCOUNTS)} trading accounts from database")
        
except Exception as e:
    import logging
    logging.getLogger("meridian.config").warning(f"Database integration failed: {e}. Using hardcoded accounts.")
    # TRADING_ACCOUNTS already set to hardcoded values above
