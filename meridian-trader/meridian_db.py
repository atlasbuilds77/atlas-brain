"""
Meridian Database Integration
Pulls trading accounts from PostgreSQL (multi-tenant)
Fallback to hardcoded config if DB unavailable
"""
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from typing import List, Dict, Optional
from pathlib import Path

# Add parent to path for crypto imports
sys.path.insert(0, str(Path(__file__).parent.parent / "meridian-dashboard"))

try:
    from lib.crypto.encryption import decryptApiKey
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logging.warning("Encryption module not available - using fallback mode")

log = logging.getLogger("meridian.db")

# Database connection
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgresql_e5fi_user:moo24YFbny662K6sJvhpJLTAI6DSVlR5@dpg-d48i5r2li9vc739av9cg-a.oregon-postgres.render.com/postgresql_e5fi"
)


def get_db_connection():
    """Get PostgreSQL connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        log.error(f"Database connection failed: {e}")
        return None


def decrypt_api_key_from_db(encrypted_key: str, iv: str) -> Optional[str]:
    """Decrypt API key from database storage"""
    if not CRYPTO_AVAILABLE:
        log.error("Crypto module not available - cannot decrypt keys")
        return None
    
    try:
        # Parse encrypted key and auth tag (stored as "encrypted:authTag")
        parts = encrypted_key.split(':')
        if len(parts) != 2:
            log.error(f"Invalid encrypted key format: {encrypted_key}")
            return None
        
        encrypted, auth_tag = parts
        return decryptApiKey(encrypted, iv, auth_tag)
    except Exception as e:
        log.error(f"Failed to decrypt API key: {e}")
        return None


def get_active_trading_accounts() -> List[Dict]:
    """
    Get active trading accounts from database
    Returns list of dicts compatible with TRADING_ACCOUNTS format:
    [
        {
            "name": "user123",
            "account": "6YB71689",
            "token": "decrypted_token",
            "size_pct": 1.0,
            "fallback_equity": None,
        },
        ...
    ]
    """
    conn = get_db_connection()
    if not conn:
        log.warning("Database unavailable - returning empty list (will use fallback)")
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all active Tradier credentials with user settings
            query = """
            SELECT 
                u.discord_id,
                u.username,
                ac.encrypted_api_key,
                ac.encryption_iv,
                us.trading_enabled,
                us.size_pct,
                us.max_position_size
            FROM api_credentials ac
            JOIN users u ON ac.user_id = u.id
            LEFT JOIN user_trading_settings us ON u.id = us.user_id
            WHERE ac.platform = 'tradier'
              AND ac.is_active = true
              AND ac.verification_status = 'verified'
              AND (us.trading_enabled IS NULL OR us.trading_enabled = true)
            ORDER BY u.username
            """
            
            cur.execute(query)
            rows = cur.fetchall()
            
            if not rows:
                log.info("No active trading accounts in database")
                return []
            
            accounts = []
            for row in rows:
                # Decrypt API key
                decrypted_token = decrypt_api_key_from_db(
                    row['encrypted_api_key'],
                    row['encryption_iv']
                )
                
                if not decrypted_token:
                    log.warning(f"Failed to decrypt key for user {row['username']} - skipping")
                    continue
                
                # TODO: Extract account number from Tradier API
                # For now, we'll need to fetch it or require users to enter it
                account_number = None  # Placeholder
                
                account = {
                    "name": row['username'],
                    "discord_id": row['discord_id'],
                    "account": account_number,  # Will be fetched from Tradier
                    "token": decrypted_token,
                    "size_pct": float(row['size_pct']) if row['size_pct'] else 1.0,
                    "max_position_size": float(row['max_position_size']) if row['max_position_size'] else None,
                }
                
                accounts.append(account)
            
            log.info(f"Loaded {len(accounts)} active trading accounts from database")
            return accounts
            
    except Exception as e:
        log.error(f"Error fetching trading accounts: {e}")
        return []
    finally:
        conn.close()


def get_tradier_account_number(token: str) -> Optional[str]:
    """Fetch account number from Tradier API"""
    import requests
    
    try:
        resp = requests.get(
            "https://api.tradier.com/v1/user/profile",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            timeout=10
        )
        
        if resp.status_code != 200:
            log.error(f"Tradier profile API error: {resp.status_code}")
            return None
        
        data = resp.json()
        profile = data.get("profile", {})
        accounts = profile.get("account", [])
        
        if not accounts:
            log.error("No accounts found in Tradier profile")
            return None
        
        # Return first account number
        if isinstance(accounts, list):
            return accounts[0].get("account_number")
        else:
            return accounts.get("account_number")
            
    except Exception as e:
        log.error(f"Failed to fetch Tradier account number: {e}")
        return None


def get_trading_accounts_with_fallback(hardcoded_accounts: List[Dict]) -> List[Dict]:
    """
    Get trading accounts from DB, fallback to hardcoded if DB empty/unavailable
    
    Args:
        hardcoded_accounts: The original TRADING_ACCOUNTS from meridian_config.py
    
    Returns:
        List of trading accounts (DB or fallback)
    """
    db_accounts = get_active_trading_accounts()
    
    # Fetch account numbers from Tradier for DB accounts
    for acc in db_accounts:
        if not acc["account"]:
            acc["account"] = get_tradier_account_number(acc["token"])
            if not acc["account"]:
                log.warning(f"Could not fetch account number for {acc['name']} - skipping")
                continue
    
    # Filter out accounts without account numbers
    db_accounts = [a for a in db_accounts if a.get("account")]
    
    if db_accounts:
        log.info(f"Using {len(db_accounts)} accounts from database")
        return db_accounts
    else:
        log.info(f"No database accounts available - using {len(hardcoded_accounts)} hardcoded accounts as fallback")
        return hardcoded_accounts


if __name__ == "__main__":
    # Test database connection
    logging.basicConfig(level=logging.INFO)
    
    print("Testing database connection...")
    conn = get_db_connection()
    if conn:
        print("✅ Database connected")
        conn.close()
    else:
        print("❌ Database connection failed")
    
    print("\nFetching active trading accounts...")
    accounts = get_active_trading_accounts()
    print(f"Found {len(accounts)} accounts:")
    for acc in accounts:
        print(f"  - {acc['name']} (size_pct: {acc['size_pct']})")
