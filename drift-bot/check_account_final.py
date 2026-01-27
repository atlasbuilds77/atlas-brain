#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from driftpy.drift_client import DriftClient
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient

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
        
        # Get user account
        user = drift_client.get_user()
        
        # Check if user is initialized
        user_account = user.get_user_account()
        
        if user_account:
            print("✅ Drift user account already initialized!")
            print(f"User authority: {user_account.authority}")
            
            # Get free collateral
            free_collateral = user.get_free_collateral()
            print(f"Free collateral: ${free_collateral/1e6:.2f}")  # Assuming 6 decimals for USD
            
            # Check spot positions
            print("\nChecking spot positions (market 0-4):")
            for market_index in range(5):  # Check first 5 spot markets
                spot_position = user.get_spot_position(market_index)
                if spot_position and hasattr(spot_position, 'scaled_balance') and spot_position.scaled_balance > 0:
                    print(f"  Market {market_index}: {spot_position.scaled_balance / 1e9:.6f} SOL")
            
            # Check perp positions
            print("\nChecking perp positions (market 0-4):")
            for market_index in range(5):  # Check first 5 perp markets
                perp_position = user.get_perp_position(market_index)
                if perp_position and hasattr(perp_position, 'base_asset_amount') and abs(perp_position.base_asset_amount) > 0:
                    print(f"  Market {market_index}: {perp_position.base_asset_amount / 1e9:.4f} contracts")
                    
        else:
            print("❌ No Drift user account found.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await drift_client.unsubscribe()

if __name__ == "__main__":
    asyncio.run(main())