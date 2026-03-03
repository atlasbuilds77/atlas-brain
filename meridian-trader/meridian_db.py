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

try:
    from meridian_crypto import decrypt_api_key
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logging.warning("meridian_crypto module not available - using fallback mode")

log = logging.getLogger("meridian.db")

# Database connection
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://meridian_user:8uOhIfyylf2gExR4yU8z7L9bg1z2kbC3@dpg-d6cfdna4d50c7383a61g-a.oregon-postgres.render.com/meridian_0j0f"
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
            log.error(f"Invalid encrypted key format (expected 'encrypted:authTag')")
            return None
        
        encrypted, auth_tag = parts
        return decrypt_api_key(encrypted, iv, auth_tag)
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
                ac.account_number,
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
                
                # Use stored account number, fallback to API fetch
                account_number = row.get('account_number')
                
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


def _safe_float(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _get_account_liquidity_score(token: str, account_number: str) -> float:
    """
    Return a liquidity score for an account using available Tradier balance fields.
    Higher score means more likely to be the funded account for trading.
    """
    import requests

    try:
        resp = requests.get(
            f"https://api.tradier.com/v1/accounts/{account_number}/balances",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return -1.0

        balances = (resp.json() or {}).get("balances", {}) or {}
        cash = balances.get("cash") or {}
        cash_available = _safe_float(cash.get("cash_available"))
        total_cash = _safe_float(balances.get("total_cash"))
        total_equity = _safe_float(balances.get("total_equity") or balances.get("equity"))
        option_bp = _safe_float(balances.get("option_buying_power"))
        return max(cash_available, total_cash, total_equity, option_bp)
    except Exception:
        return -1.0


def resolve_best_tradier_account_number(token: str, preferred_account: Optional[str]) -> Optional[str]:
    """
    Resolve the best account number for a token.
    If preferred account is unfunded and another linked account has liquidity, switch.
    """
    import requests

    try:
        resp = requests.get(
            "https://api.tradier.com/v1/user/profile",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            timeout=10,
        )
        if resp.status_code != 200:
            log.warning(f"Tradier profile API error while resolving account: {resp.status_code}")
            return preferred_account

        profile = (resp.json() or {}).get("profile", {}) or {}
        accounts = profile.get("account", [])
        if isinstance(accounts, dict):
            accounts = [accounts]

        account_numbers = [a.get("account_number") for a in accounts if a.get("account_number")]
        if not account_numbers:
            return preferred_account

        if preferred_account and preferred_account not in account_numbers:
            log.warning(
                f"Preferred account {preferred_account} not in Tradier profile; "
                f"using discovered account list {account_numbers}"
            )
            preferred_account = None

        best_account = preferred_account or account_numbers[0]
        best_score = _get_account_liquidity_score(token, best_account)

        for candidate in account_numbers:
            score = _get_account_liquidity_score(token, candidate)
            if score > best_score:
                best_account = candidate
                best_score = score

        if preferred_account and best_account != preferred_account:
            preferred_score = _get_account_liquidity_score(token, preferred_account)
            if best_score > max(preferred_score, 0):
                log.warning(
                    f"Account remap: switching {preferred_account} -> {best_account} "
                    f"(liquidity {preferred_score:.2f} -> {best_score:.2f})"
                )
                return best_account
            return preferred_account

        return best_account
    except Exception as e:
        log.warning(f"Failed to resolve best Tradier account number: {e}")
        return preferred_account


def get_trading_accounts_with_fallback(hardcoded_accounts: List[Dict]) -> List[Dict]:
    """
    Get trading accounts from DB, fallback to hardcoded if DB empty/unavailable
    
    Args:
        hardcoded_accounts: The original TRADING_ACCOUNTS from meridian_config.py
    
    Returns:
        List of trading accounts (DB or fallback)
    """
    db_accounts = get_active_trading_accounts()
    
    # Fetch/validate account numbers from Tradier for DB accounts
    for acc in db_accounts:
        account_number = acc.get("account")
        if not account_number:
            account_number = get_tradier_account_number(acc["token"])
            if not account_number:
                log.warning(f"Could not fetch account number for {acc['name']} - skipping")
                continue

        resolved_number = resolve_best_tradier_account_number(acc["token"], account_number)
        if resolved_number:
            acc["account"] = resolved_number

    # Filter out accounts without account numbers
    db_accounts = [a for a in db_accounts if a.get("account")]
    
    if db_accounts:
        log.info(f"Using {len(db_accounts)} accounts from database")
        return db_accounts
    else:
        log.info(f"No database accounts available - using {len(hardcoded_accounts)} hardcoded accounts as fallback")
        return hardcoded_accounts


def get_user_id_by_account(account_number: str) -> Optional[int]:
    """
    Lookup user_id from account number in api_credentials table
    
    Args:
        account_number: Tradier account number (e.g., "6YB71689")
    
    Returns:
        user_id or None if not found
    """
    conn = get_db_connection()
    if not conn:
        log.warning("Database unavailable - cannot lookup user_id")
        return None
    
    try:
        with conn.cursor() as cur:
            query = """
            SELECT user_id 
            FROM api_credentials 
            WHERE account_number = %s 
              AND platform = 'tradier'
              AND is_active = true
            LIMIT 1
            """
            cur.execute(query, (account_number,))
            row = cur.fetchone()
            
            if row:
                return row[0]
            else:
                log.warning(f"No user_id found for account {account_number}")
                return None
                
    except Exception as e:
        log.error(f"Error looking up user_id for account {account_number}: {e}")
        return None
    finally:
        conn.close()


def log_trade_entry(
    account_number: str,
    symbol: str,
    direction: str,
    asset_type: str,
    strike: float,
    expiry: str,
    entry_price: float,
    quantity: int,
    notes: str = None,
    stop_loss: float = None,
    take_profit: float = None,
    entry_reasoning: str = None,
    setup_type: str = None,
    status: str = "open"
) -> Optional[int]:
    """
    Log trade entry to database
    
    Args:
        account_number: Tradier account number
        symbol: Underlying symbol (e.g., "QQQ")
        direction: "bull" or "bear"
        asset_type: Asset type (e.g., "option", "stock", "future", "crypto")
        strike: Strike price
        expiry: Expiration date (YYYY-MM-DD)
        entry_price: Entry price per contract
        quantity: Number of contracts (0 = skipped trade)
        notes: Optional notes (include call/put type here)
        status: Trade status (default: "open", can be "skipped")
    
    Returns:
        trade_id if successful, None otherwise
    """
    conn = get_db_connection()
    if not conn:
        log.warning("Database unavailable - cannot log trade entry")
        return None
    
    try:
        # Get user_id from account number
        user_id = get_user_id_by_account(account_number)
        if not user_id:
            log.warning(f"Cannot log trade - no user_id for account {account_number}")
            return None
        
        # Get account_id from api_credentials
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM api_credentials 
                WHERE account_number = %s AND platform = 'tradier' AND is_active = true
                LIMIT 1
            """, (account_number,))
            row = cur.fetchone()
            account_id = row[0] if row else None
            
            if not account_id:
                log.warning(f"No account_id found for account {account_number}")
                return None
            
            # Insert trade record
            insert_query = """
            INSERT INTO trades (
                user_id, account_id, symbol, direction, asset_type,
                strike, expiry, entry_price, quantity, entry_date,
                status, notes, stop_loss, take_profit, entry_reasoning, setup_type,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, NOW(),
                %s, %s, %s, %s, %s, %s,
                NOW(), NOW()
            )
            RETURNING id
            """
            
            cur.execute(insert_query, (
                user_id, account_id, symbol, direction, asset_type,
                strike, expiry, entry_price, quantity, status,
                notes, stop_loss, take_profit, entry_reasoning, setup_type
            ))
            
            trade_id = cur.fetchone()[0]
            conn.commit()
            
            log.info(f"Trade entry logged: trade_id={trade_id}, account={account_number}, "
                    f"status={status}, {direction} {quantity}x {symbol} ${strike} {asset_type}")
            
            return trade_id
            
    except Exception as e:
        log.error(f"Error logging trade entry for account {account_number}: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def log_trade_exit(
    account_number: str,
    symbol: str,
    strike: float,
    expiry: str,
    exit_price: float,
    notes: str = None
) -> bool:
    """
    Update trade record with exit data
    
    Args:
        account_number: Tradier account number
        symbol: Underlying symbol
        strike: Strike price
        expiry: Expiration date (YYYY-MM-DD)
        exit_price: Exit price per contract
        notes: Optional exit notes (e.g., "STOP (-50%)")
    
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    if not conn:
        log.warning("Database unavailable - cannot log trade exit")
        return False
    
    try:
        with conn.cursor() as cur:
            # Find the most recent open trade matching criteria
            update_query = """
            UPDATE trades
            SET exit_price = %s,
                exit_date = NOW(),
                pnl = ((%s - entry_price) * quantity * 100),
                pnl_percent = ((%s - entry_price) / NULLIF(entry_price, 0)),
                commission = (quantity * 2.06 * 2),
                net_pnl = ((%s - entry_price) * quantity * 100) - (quantity * 2.06 * 2),
                status = 'closed',
                notes = CASE 
                    WHEN notes IS NULL THEN %s
                    ELSE notes || ' | Exit: ' || %s
                END,
                updated_at = NOW()
            WHERE id = (
                SELECT t.id 
                FROM trades t
                JOIN api_credentials ac ON t.account_id::integer = ac.id
                WHERE ac.account_number = %s
                  AND t.symbol = %s
                  AND t.strike = %s
                  AND t.expiry = %s
                  AND t.status = 'open'
                ORDER BY t.entry_date DESC
                LIMIT 1
            )
            RETURNING id, pnl, pnl_percent
            """
            
            cur.execute(update_query, (
                exit_price, exit_price, exit_price, exit_price, notes, notes,
                account_number, symbol, strike, expiry
            ))
            
            result = cur.fetchone()
            
            if result:
                trade_id, pnl, pnl_pct = result
                conn.commit()
                log.info(f"Trade exit logged: trade_id={trade_id}, account={account_number}, "
                        f"P&L=${pnl:.2f} ({pnl_pct:+.1%})")
                return True
            else:
                log.warning(f"No open trade found to update for account {account_number}, "
                           f"{symbol} ${strike} exp {expiry}")
                return False
                
    except Exception as e:
        log.error(f"Error logging trade exit for account {account_number}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def save_order(
    trade_id: int,
    order_id: str,
    account_number: str,
    symbol: str,
    option_symbol: str,
    side: str,
    qty_requested: int,
    order_type: str = "market"
) -> bool:
    """
    Save order to database for tracking
    
    Args:
        trade_id: Trade ID from trades table
        order_id: Tradier order ID
        account_number: Tradier account number
        symbol: Underlying symbol (e.g., "QQQ")
        option_symbol: Full option symbol
        side: buy_to_open, sell_to_close, etc.
        qty_requested: Number of contracts requested
        order_type: market, limit, etc.
    
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    if not conn:
        log.warning("Database unavailable - cannot save order")
        return False
    
    try:
        with conn.cursor() as cur:
            insert_query = """
            INSERT INTO orders (
                trade_id, order_id, account_number, symbol, option_symbol,
                side, order_type, qty_requested, status, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, 'pending', NOW(), NOW()
            )
            ON CONFLICT (order_id) DO NOTHING
            RETURNING id
            """
            
            cur.execute(insert_query, (
                trade_id, order_id, account_number, symbol, option_symbol,
                side, order_type, qty_requested
            ))
            
            result = cur.fetchone()
            conn.commit()
            
            if result:
                log.info(f"Order saved to DB: order_id={order_id}, trade_id={trade_id}, "
                        f"{side} {qty_requested}x {option_symbol}")
                return True
            else:
                log.warning(f"Order already exists: order_id={order_id}")
                return False
                
    except Exception as e:
        log.error(f"Error saving order {order_id}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def check_existing_order(
    trade_id: int,
    option_symbol: str,
    side: str
) -> Optional[dict]:
    """
    Check if order already exists for this trade + symbol + side
    
    Args:
        trade_id: Trade ID from trades table
        option_symbol: Full option symbol
        side: buy_to_open, sell_to_close, etc.
    
    Returns:
        Order dict if exists, None otherwise
    """
    conn = get_db_connection()
    if not conn:
        log.warning("Database unavailable - cannot check existing order")
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
            SELECT 
                id, order_id, status, qty_requested, qty_filled,
                avg_fill_price, created_at
            FROM orders
            WHERE trade_id = %s
              AND option_symbol = %s
              AND side = %s
            ORDER BY created_at DESC
            LIMIT 1
            """
            
            cur.execute(query, (trade_id, option_symbol, side))
            row = cur.fetchone()
            
            if row:
                log.info(f"Existing order found: order_id={row['order_id']}, "
                        f"status={row['status']}, filled={row['qty_filled']}/{row['qty_requested']}")
                return dict(row)
            else:
                return None
                
    except Exception as e:
        log.error(f"Error checking existing order: {e}")
        return None
    finally:
        conn.close()


def update_order_fill(
    order_id: str,
    qty_filled: int,
    avg_fill_price: float,
    status: str = "filled"
) -> bool:
    """
    Update order fill status
    
    Args:
        order_id: Tradier order ID
        qty_filled: Number of contracts filled
        avg_fill_price: Average fill price
        status: filled, partial, rejected, etc.
    
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    if not conn:
        log.warning("Database unavailable - cannot update order fill")
        return False
    
    try:
        with conn.cursor() as cur:
            update_query = """
            UPDATE orders
            SET qty_filled = %s,
                avg_fill_price = %s,
                status = %s,
                filled_at = NOW(),
                updated_at = NOW()
            WHERE order_id = %s
            RETURNING qty_requested
            """
            
            cur.execute(update_query, (qty_filled, avg_fill_price, status, order_id))
            result = cur.fetchone()
            conn.commit()
            
            if result:
                qty_requested = result[0]
                log.info(f"Order fill updated: order_id={order_id}, "
                        f"filled {qty_filled}/{qty_requested} @ ${avg_fill_price:.2f}, "
                        f"status={status}")
                return True
            else:
                log.warning(f"Order not found: order_id={order_id}")
                return False
                
    except Exception as e:
        log.error(f"Error updating order fill for {order_id}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_trade_orders(trade_id: int) -> List[Dict]:
    """
    Get all orders for a trade
    
    Args:
        trade_id: Trade ID from trades table
    
    Returns:
        List of order dicts
    """
    conn = get_db_connection()
    if not conn:
        log.warning("Database unavailable - cannot get trade orders")
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
            SELECT 
                id, order_id, account_number, symbol, option_symbol,
                side, order_type, qty_requested, qty_filled,
                avg_fill_price, status, created_at, filled_at
            FROM orders
            WHERE trade_id = %s
            ORDER BY created_at ASC
            """
            
            cur.execute(query, (trade_id,))
            rows = cur.fetchall()
            
            return [dict(row) for row in rows]
            
    except Exception as e:
        log.error(f"Error fetching trade orders for trade_id={trade_id}: {e}")
        return []
    finally:
        conn.close()


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
