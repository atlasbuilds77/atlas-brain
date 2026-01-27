#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from driftpy.drift_client import DriftClient
from driftpy.drift_user import DriftUser
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from driftpy.constants.numeric_constants import BASE_PRECISION, QUOTE_PRECISION

async def main():
    # Load keypair
    with open(Path(__file__).parent / ".secrets" / "solana-keypair.json", 'r') as f:
        secret = json.load(f)
    keypair = Keypair.from_bytes(bytes(secret))
    
    # Connect to Drift
    connection = AsyncClient("https://api.mainnet-beta.solana.com")
    drift_client = DriftClient(connection, keypair, env="mainnet")
    
    print(f"Wallet: {keypair.pubkey()}")
    
    try:
        await drift_client.subscribe()
        
        # Check if user account exists
        user = drift_client.get_user()
        
        # Get user account data
        user_account_data = await user.get_user_account()
        
        if user_account_data:
            print("✅ Drift user account already initialized!")
            print(f"User Account: {user_account_data.authority}")
            
            # Check collateral
            print(f"\nChecking collateral...")
            
            # Get spot positions
            spot_positions = user.get_spot_positions()
            total_collateral = 0
            
            for i, pos in enumerate(spot_positions):
                if hasattr(pos, 'scaled_balance') and pos.scaled_balance > 0:
                    balance = pos.scaled_balance / 1e9  # Assuming SOL has 9 decimals
                    print(f"  Spot Market {i}: {balance:.6f} SOL")
                    total_collateral += balance
            
            if total_collateral == 0:
                print("  No collateral deposited yet")
            else:
                print(f"\nTotal SOL Collateral: {total_collateral:.6f} SOL")
            
            # Check perp positions
            print(f"\nChecking perp positions...")
            perp_positions = user.get_perp_positions()
            has_perp_position = False
            
            for i, pos in enumerate(perp_positions):
                if hasattr(pos, 'base_asset_amount') and abs(pos.base_asset_amount) > 0:
                    position_size = pos.base_asset_amount / BASE_PRECISION
                    entry_price = pos.entry_price / QUOTE_PRECISION if hasattr(pos, 'entry_price') else 0
                    print(f"  Perp Market {i}: {position_size:.4f} contracts @ ${entry_price:.2f}")
                    has_perp_position = True
            
            if not has_perp_position:
                print("  No open perp positions")
                
        else:
            print("❌ No Drift user account found. Need to initialize.")
            
    except Exception as e:
        print(f"Error checking user account: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await drift_client.unsubscribe()

if __name__ == "__main__":
    asyncio.run(main())