#!/usr/bin/env python3
"""Open ETH-PERP LONG position on Drift"""
import asyncio
import json
from driftpy.drift_client import DriftClient
from driftpy.account_subscription_config import AccountSubscriptionConfig
from driftpy.types import PositionDirection, MarketType, OrderType, OrderParams
from driftpy.constants.numeric_constants import BASE_PRECISION
from anchorpy import Wallet
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient

RPC = 'https://mainnet.helius-rpc.com/?api-key=54396175-9f9a-418c-b936-2495159cdd0a'

async def open_position():
    # Load keypair
    with open('.secrets/solana-keypair.json') as f:
        kp = Keypair.from_bytes(bytes(json.load(f)))
    
    print(f"Trading wallet: {kp.pubkey()}")
    
    # Connect
    wallet = Wallet(kp)
    connection = AsyncClient(RPC)
    
    # Simple connection without heavy subscription
    drift = DriftClient(
        connection, 
        wallet, 
        "mainnet",
        account_subscription=AccountSubscriptionConfig("cached")
    )
    
    print("Subscribing to Drift...")
    await drift.subscribe()
    
    try:
        # ETH-PERP is market index 2
        market_index = 2
        
        # Get user to check collateral
        user = drift.get_user()
        print(f"User account: {user.user_public_key}")
        
        # Get ETH price from oracle
        perp_market = drift.get_perp_market_account(market_index)
        oracle_data = drift.get_oracle_price_data_and_slot(perp_market.amm.oracle)
        eth_price = oracle_data.data.price / 1e6  # PRICE_PRECISION
        
        print(f"ETH Oracle Price: ${eth_price:.2f}")
        
        # Calculate position size
        # With 3x leverage and ~$93 collateral = ~$279 notional
        # At $2,928/ETH = ~0.095 ETH
        collateral_usd = 93
        leverage = 3
        notional_usd = collateral_usd * leverage
        base_size = notional_usd / eth_price
        base_amount = int(base_size * BASE_PRECISION)
        
        print(f"\nOpening position:")
        print(f"  Collateral: ${collateral_usd}")
        print(f"  Leverage: {leverage}x")
        print(f"  Notional: ${notional_usd:.2f}")
        print(f"  Size: {base_size:.4f} ETH")
        
        # Place market order
        order = OrderParams(
            order_type=OrderType.Market(),
            market_type=MarketType.Perp(),
            direction=PositionDirection.Long(),
            base_asset_amount=base_amount,
            market_index=market_index,
        )
        
        print("\nPlacing order...")
        tx = await drift.place_perp_order(order)
        
        print(f"\n✅ ETH LONG OPENED!")
        print(f"   Tx: {tx}")
        print(f"   Entry: ${eth_price:.2f}")
        print(f"   Target: $3,370 (+15%)")
        print(f"   Stop: $2,635 (-10%)")
        
        return tx
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        await drift.unsubscribe()
        await connection.close()

if __name__ == "__main__":
    asyncio.run(open_position())
