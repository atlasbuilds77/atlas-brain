#!/usr/bin/env python3
"""
Drift Protocol Scalping Bot - Atlas Edition
Quick in/out trades on Solana perpetuals
Much cheaper than Arbitrum!
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Optional

# Drift imports (will work after pip install driftpy)
try:
    from driftpy.drift_client import DriftClient
    from driftpy.drift_user import DriftUser
    from driftpy.accounts import get_perp_market_account, get_spot_market_account
    from driftpy.constants.numeric_constants import BASE_PRECISION, PRICE_PRECISION
    from driftpy.types import OrderType, OrderParams, PositionDirection, MarketType
    from driftpy.keypair import load_keypair
    from solana.rpc.async_api import AsyncClient
    from solders.keypair import Keypair
    DRIFT_AVAILABLE = True
except ImportError:
    DRIFT_AVAILABLE = False
    print("⚠️  driftpy not installed yet. Run: pip install driftpy")

# === CONFIG ===
SYMBOL = "SOL-PERP"   # Trading pair (SOL, BTC, ETH available)
MARKET_INDEX = 0       # 0=SOL-PERP, 1=BTC-PERP, 2=ETH-PERP
LEVERAGE = 3           # User-specified
POSITION_SIZE_USD = 50 # Notional size per trade
TAKE_PROFIT_PCT = 3.0  # 3% profit target
STOP_LOSS_PCT = 1.5    # 1.5% stop loss
PAPER_TRADE = False    # LIVE: Use mainnet

# Risk controls
DAILY_MAX_LOSS_USD = 100   # User-specified daily loss cap
LOSS_SCALE_TRIGGER = -50   # If PnL <= -$50, scale size down
SCALED_POSITION_SIZE_USD = 25

# Entry logic (simple momentum)
LOOKBACK = 10          # seconds
ENTRY_MOMENTUM_PCT = 0.20  # % move over lookback to trigger entry
TIME_STOP_SEC = 180

# RPC endpoints
MAINNET_RPC = "https://api.mainnet-beta.solana.com"
DEVNET_RPC = "https://api.devnet.solana.com"

# === LOAD WALLET ===
def load_keypair_from_file():
    """Load Solana keypair from secrets file"""
    secrets_path = Path(__file__).parent / ".secrets" / "solana-keypair.json"
    with open(secrets_path) as f:
        secret_key = json.load(f)
    return Keypair.from_bytes(bytes(secret_key))

# === SETUP CLIENT ===
async def setup_drift_client(paper=True):
    """Initialize Drift client"""
    rpc_url = DEVNET_RPC if paper else MAINNET_RPC
    env = "devnet" if paper else "mainnet"
    
    connection = AsyncClient(rpc_url)
    keypair = load_keypair_from_file()
    
    drift_client = DriftClient(
        connection,
        keypair,
        env=env
    )
    
    await drift_client.subscribe()
    
    return drift_client, keypair.pubkey()

# === GET PRICE ===
async def get_oracle_price(drift_client, market_index):
    """Get current oracle price for perp market"""
    perp_market = await get_perp_market_account(
        drift_client.program,
        market_index
    )
    oracle_price = perp_market.amm.historical_oracle_data.last_oracle_price
    return oracle_price / PRICE_PRECISION

# === GET POSITION ===
async def get_position(drift_client, market_index):
    """Get current position for market"""
    user = drift_client.get_user()
    position = user.get_perp_position(market_index)
    
    if position is None:
        return 0, 0
    
    base_amount = position.base_asset_amount / BASE_PRECISION
    entry_price = position.entry_price / PRICE_PRECISION if position.entry_price else 0
    
    return base_amount, entry_price

# === PLACE ORDER ===
async def place_market_order(drift_client, market_index, is_long, size_usd, current_price):
    """Place a market order"""
    # Calculate size in base units
    size = size_usd / current_price
    base_amount = int(size * BASE_PRECISION)
    
    direction = PositionDirection.Long() if is_long else PositionDirection.Short()
    
    order_params = OrderParams(
        order_type=OrderType.Market(),
        market_type=MarketType.Perp(),
        direction=direction,
        base_asset_amount=base_amount,
        market_index=market_index,
    )
    
    result = await drift_client.place_perp_order(order_params)
    return result

# === CLOSE POSITION ===
async def close_position(drift_client, market_index):
    """Close any open position"""
    position, _ = await get_position(drift_client, market_index)
    
    if abs(position) < 0.001:
        return False
    
    is_long = position > 0
    # Close by taking opposite direction
    await drift_client.close_position(market_index)
    return True

# === MAIN SCALPER ===
async def run_scalper():
    """
    Simple momentum scalper for Drift
    """
    print("=" * 50)
    print("DRIFT PROTOCOL SCALPING BOT - ATLAS EDITION")
    print("=" * 50)
    print(f"Mode: {'PAPER (Devnet)' if PAPER_TRADE else 'LIVE (Mainnet)'}")
    print(f"Symbol: {SYMBOL}")
    print(f"Leverage: {LEVERAGE}x")
    print(f"Position Size: ${POSITION_SIZE_USD}")
    print(f"Take Profit: {TAKE_PROFIT_PCT}%")
    print(f"Stop Loss: {STOP_LOSS_PCT}%")
    print("=" * 50)
    
    if not DRIFT_AVAILABLE:
        print("\n❌ driftpy not installed!")
        print("Run: pip install driftpy")
        return
    
    print("\nConnecting to Drift...")
    
    try:
        drift_client, pubkey = await setup_drift_client(paper=PAPER_TRADE)
        print(f"✅ Connected!")
        print(f"Wallet: {pubkey}")
        
        # Get current price
        price = await get_oracle_price(drift_client, MARKET_INDEX)
        print(f"\n{SYMBOL} Price: ${price:,.2f}")
        
        # Get current position
        position, entry = await get_position(drift_client, MARKET_INDEX)
        if abs(position) > 0.001:
            print(f"Current Position: {position:.4f} @ ${entry:,.2f}")
        else:
            print("No open position")
        
        print("\n✅ Bot initialized!")
        print("\nMonitoring price for scalp opportunities...")
        
        # Simple price tracking + trade loop
        prices = []
        session_pnl = 0.0
        position_open = False
        entry_price = 0.0
        entry_time = None
        position_side = None  # "long" or "short"
        
        while True:
            try:
                current_price = await get_oracle_price(drift_client, MARKET_INDEX)
                prices.append(current_price)
                
                if len(prices) > LOOKBACK:
                    prices.pop(0)
                
                if len(prices) >= LOOKBACK:
                    momentum = (prices[-1] - prices[0]) / prices[0] * 100
                    direction = "📈" if momentum > 0 else "📉"
                    print(f"{SYMBOL}: ${current_price:,.2f} | Mom: {momentum:+.3f}% {direction} | PnL: ${session_pnl:+.2f}", end="\r")

                    # Daily loss cap
                    if session_pnl <= -DAILY_MAX_LOSS_USD:
                        print("\n\n❌ Daily loss cap hit. Stopping trading.")
                        break

                    # Determine size (scale down after drawdown)
                    size_usd = POSITION_SIZE_USD if session_pnl > LOSS_SCALE_TRIGGER else SCALED_POSITION_SIZE_USD

                    if not position_open:
                        if momentum >= ENTRY_MOMENTUM_PCT:
                            await place_market_order(drift_client, MARKET_INDEX, True, size_usd, current_price)
                            position_open = True
                            position_side = "long"
                            entry_price = current_price
                            entry_time = asyncio.get_event_loop().time()
                            print(f"\n\n✅ LONG @ ${entry_price:,.2f} size ${size_usd}")
                        elif momentum <= -ENTRY_MOMENTUM_PCT:
                            await place_market_order(drift_client, MARKET_INDEX, False, size_usd, current_price)
                            position_open = True
                            position_side = "short"
                            entry_price = current_price
                            entry_time = asyncio.get_event_loop().time()
                            print(f"\n\n✅ SHORT @ ${entry_price:,.2f} size ${size_usd}")
                    else:
                        # Manage open position
                        if position_side == "long":
                            tp = entry_price * (1 + TAKE_PROFIT_PCT/100)
                            sl = entry_price * (1 - STOP_LOSS_PCT/100)
                            hit_tp = current_price >= tp
                            hit_sl = current_price <= sl
                            pnl = (current_price - entry_price) / entry_price * size_usd
                        else:
                            tp = entry_price * (1 - TAKE_PROFIT_PCT/100)
                            sl = entry_price * (1 + STOP_LOSS_PCT/100)
                            hit_tp = current_price <= tp
                            hit_sl = current_price >= sl
                            pnl = (entry_price - current_price) / entry_price * size_usd

                        time_in = asyncio.get_event_loop().time() - entry_time if entry_time else 0
                        hit_time = time_in >= TIME_STOP_SEC

                        if hit_tp or hit_sl or hit_time:
                            await close_position(drift_client, MARKET_INDEX)
                            session_pnl += pnl
                            print(f"\n\n✅ Closed {position_side.upper()} @ ${current_price:,.2f} | PnL: ${pnl:+.2f}")
                            position_open = False
                            position_side = None
                            entry_price = 0.0
                            entry_time = None
                
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                print("\n\nStopping bot...")
                break
            except Exception as e:
                print(f"\nError: {e}")
                await asyncio.sleep(5)
        
        await drift_client.unsubscribe()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. Wallet is funded with SOL (for gas)")
        print("2. USDC deposited to Drift")
        print("3. Using correct network (devnet/mainnet)")

def main():
    asyncio.run(run_scalper())

if __name__ == "__main__":
    main()
