#!/usr/bin/env python3
"""
Drift ETH Perp Trading Bot
"""
import asyncio
import sys
import json
from decimal import Decimal
from driftpy.drift_client import DriftClient
from driftpy.account_subscription_config import AccountSubscriptionConfig
from driftpy.types import PositionDirection, MarketType, OrderType, OrderParams
from driftpy.constants.numeric_constants import PRICE_PRECISION, BASE_PRECISION, QUOTE_PRECISION
from anchorpy import Wallet
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey

RPC_URL = 'https://mainnet.helius-rpc.com/?api-key=54396175-9f9a-418c-b936-2495159cdd0a'

async def get_client():
    with open('.secrets/solana-keypair.json') as f:
        kp = Keypair.from_bytes(bytes(json.load(f)))
    
    wallet = Wallet(kp)
    connection = AsyncClient(RPC_URL)
    
    # Use cached mode with retries
    config = AccountSubscriptionConfig("cached")
    drift = DriftClient(connection, wallet, "mainnet", account_subscription=config)
    
    # Subscribe with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await drift.subscribe()
            break
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    return drift, connection

async def check_account():
    """Check if Drift account exists, initialize if needed"""
    drift, conn = await get_client()
    
    try:
        user = drift.get_user()
        print(f"✅ Drift account found: {user.user_public_key}")
        
        # Get spot positions (collateral)
        spot_positions = user.get_spot_positions()
        for pos in spot_positions:
            if pos.scaled_balance > 0:
                market = drift.get_spot_market_account(pos.market_index)
                balance = pos.scaled_balance / QUOTE_PRECISION
                print(f"   Spot balance: {balance:.4f} (market {pos.market_index})")
        
        # Get perp positions
        perp_positions = user.get_perp_positions()
        for pos in perp_positions:
            if pos.base_asset_amount != 0:
                print(f"   Perp position: market {pos.market_index}, size {pos.base_asset_amount}")
        
        return True
    except Exception as e:
        print(f"⚠️  No Drift account found: {e}")
        print("Creating Drift account...")
        
        try:
            tx = await drift.initialize_user()
            print(f"✅ Account created: {tx}")
            return True
        except Exception as init_err:
            print(f"❌ Failed to initialize: {init_err}")
            return False
    finally:
        await drift.unsubscribe()
        await conn.close()

async def deposit_collateral(amount_sol):
    """Deposit SOL as collateral"""
    drift, conn = await get_client()
    
    try:
        amount_lamports = int(float(amount_sol) * 1e9)
        print(f"Depositing {amount_sol} SOL as collateral...")
        
        # Market index 1 is typically SOL spot
        tx = await drift.deposit(amount_lamports, 1)
        print(f"✅ Deposited {amount_sol} SOL")
        print(f"   Tx: {tx}")
        
    finally:
        await drift.unsubscribe()
        await conn.close()

async def open_perp_position(market_symbol, direction, size_usd, leverage):
    """Open leveraged perp position"""
    drift, conn = await get_client()
    
    try:
        # ETH-PERP is market index 2
        market_index = 2 if market_symbol == "ETH" else 0
        
        # Get current price
        oracle_price = drift.get_oracle_price_data_and_slot(
            drift.get_perp_market_account(market_index).amm.oracle
        ).data.price / PRICE_PRECISION
        
        print(f"ETH Oracle Price: ${oracle_price:.2f}")
        
        # Calculate position size
        # size_usd with leverage / price = base amount
        notional = float(size_usd) * leverage
        base_size = notional / oracle_price
        base_amount = int(base_size * BASE_PRECISION)
        
        dir = PositionDirection.Long() if direction.lower() == "long" else PositionDirection.Short()
        
        print(f"Opening {leverage}x {direction} on {market_symbol}")
        print(f"  Collateral: ${size_usd}")
        print(f"  Notional: ${notional:.2f}")
        print(f"  Base amount: {base_size:.4f} ETH")
        
        order_params = OrderParams(
            order_type=OrderType.Market(),
            market_type=MarketType.Perp(),
            direction=dir,
            base_asset_amount=base_amount,
            market_index=market_index,
        )
        
        tx = await drift.place_perp_order(order_params)
        print(f"✅ Position opened!")
        print(f"   Tx: {tx}")
        
    except Exception as e:
        print(f"❌ Error opening position: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await drift.unsubscribe()
        await conn.close()

async def close_position(market_symbol):
    """Close all positions for a market"""
    drift, conn = await get_client()
    
    try:
        market_index = 2 if market_symbol == "ETH" else 0
        user = drift.get_user()
        
        # Find position
        for pos in user.get_perp_positions():
            if pos.market_index == market_index and pos.base_asset_amount != 0:
                # Close by placing opposite order
                is_long = pos.base_asset_amount > 0
                dir = PositionDirection.Short() if is_long else PositionDirection.Long()
                
                order_params = OrderParams(
                    order_type=OrderType.Market(),
                    market_type=MarketType.Perp(),
                    direction=dir,
                    base_asset_amount=abs(pos.base_asset_amount),
                    market_index=market_index,
                    reduce_only=True
                )
                
                tx = await drift.place_perp_order(order_params)
                print(f"✅ Position closed: {tx}")
                return
        
        print("No position found to close")
        
    finally:
        await drift.unsubscribe()
        await conn.close()

async def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage:")
        print("  python drift_trade.py status")
        print("  python drift_trade.py deposit 0.25")
        print("  python drift_trade.py long ETH 80 5     # 5x leverage, $80 collateral")
        print("  python drift_trade.py close ETH")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        await check_account()
    elif cmd == "deposit":
        await deposit_collateral(sys.argv[2])
    elif cmd in ["long", "short"]:
        symbol = sys.argv[2]
        size = sys.argv[3]
        leverage = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        await open_perp_position(symbol, cmd, size, leverage)
    elif cmd == "close":
        await close_position(sys.argv[2])
    else:
        print("Unknown command")

if __name__ == "__main__":
    asyncio.run(main())
