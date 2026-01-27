#!/usr/bin/env python3
"""
Simple Drift Position Checker
Uses simpler API calls to avoid subscription issues
"""
import asyncio
import json
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from anchorpy import Wallet
from driftpy.drift_client import DriftClient
from driftpy.account_subscription_config import AccountSubscriptionConfig

# Try multiple RPC endpoints
RPC_URLS = [
    'https://api.mainnet-beta.solana.com',
    'https://solana-api.projectserum.com',
    'https://rpc.ankr.com/solana',
]

async def get_client_simple():
    """Get client with simpler subscription"""
    with open('.secrets/solana-keypair.json') as f:
        kp = Keypair.from_bytes(bytes(json.load(f)))
    
    wallet = Wallet(kp)
    
    # Try each RPC endpoint
    for rpc_url in RPC_URLS:
        try:
            print(f"Trying RPC: {rpc_url}")
            connection = AsyncClient(rpc_url)
            
            # Use websocket mode (simpler than cached)
            config = AccountSubscriptionConfig("websocket")
            drift = DriftClient(connection, wallet, "mainnet", account_subscription=config)
            
            # Try to subscribe with timeout
            await asyncio.wait_for(drift.subscribe(), timeout=10.0)
            
            print(f"✅ Connected via {rpc_url}")
            return drift, connection
            
        except asyncio.TimeoutError:
            print(f"❌ Timeout on {rpc_url}")
            try:
                await drift.unsubscribe()
                await connection.close()
            except:
                pass
            continue
        except Exception as e:
            print(f"❌ Error on {rpc_url}: {e}")
            try:
                await connection.close()
            except:
                pass
            continue
    
    raise Exception("All RPC endpoints failed")

async def check_positions():
    """Check Drift positions"""
    print("=" * 60)
    print("DRIFT POSITION CHECKER")
    print("=" * 60)
    
    drift = None
    conn = None
    
    try:
        drift, conn = await get_client_simple()
        
        # Get user account
        user = drift.get_user()
        print(f"\n✅ Account: {user.user_public_key}")
        
        # Check spot balances (collateral)
        print(f"\n💰 SPOT BALANCES:")
        spot_positions = user.get_spot_positions()
        total_collateral = 0
        
        for pos in spot_positions:
            if pos.scaled_balance > 0:
                balance = pos.scaled_balance / 1e9  # Convert to SOL/USDC
                market_index = pos.market_index
                print(f"   Market {market_index}: {balance:.4f}")
                total_collateral += balance
        
        print(f"   Total Collateral: ${total_collateral:.2f}")
        
        # Check perp positions
        print(f"\n📊 PERP POSITIONS:")
        perp_positions = user.get_perp_positions()
        has_positions = False
        
        for pos in perp_positions:
            if pos.base_asset_amount != 0:
                has_positions = True
                market_index = pos.market_index
                size = pos.base_asset_amount / 1e9
                side = "LONG" if size > 0 else "SHORT"
                
                # Get market info
                try:
                    market = drift.get_perp_market_account(market_index)
                    oracle_price_data = drift.get_oracle_price_data_and_slot(market.amm.oracle)
                    price = oracle_price_data.data.price / 1e6
                    
                    notional = abs(size) * price
                    
                    print(f"\n   Market {market_index} ({side}):")
                    print(f"     Size: {abs(size):.4f}")
                    print(f"     Entry Price: ${pos.quote_entry_amount / abs(pos.base_asset_amount) / 1e6:.2f}")
                    print(f"     Current Price: ${price:.2f}")
                    print(f"     Notional: ${notional:.2f}")
                    
                    # Calculate unrealized PnL
                    entry_value = abs(pos.quote_entry_amount) / 1e6
                    current_value = notional
                    if size > 0:  # LONG
                        pnl = current_value - entry_value
                    else:  # SHORT
                        pnl = entry_value - current_value
                    
                    print(f"     Unrealized P&L: ${pnl:+.2f}")
                    
                except Exception as e:
                    print(f"   Market {market_index}: Size {size:.4f} (error getting details: {e})")
        
        if not has_positions:
            print("   No open positions")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if drift:
            try:
                await drift.unsubscribe()
            except:
                pass
        if conn:
            try:
                await conn.close()
            except:
                pass

if __name__ == "__main__":
    asyncio.run(check_positions())
