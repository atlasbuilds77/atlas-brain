#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from driftpy.drift_client import DriftClient
from driftpy.drift_user import DriftUser
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
        
        # Check if user account exists
        user = drift_client.get_user()
        user_account = user.get_user_account()
        
        if user_account:
            print("✅ Drift user account already initialized!")
            print(f"User Account Public Key: {user.get_user_account_public_key()}")
            
            # Check collateral
            spot_positions = user.get_spot_positions()
            print(f"\nSpot Positions:")
            for i, pos in enumerate(spot_positions):
                if pos.scaled_balance > 0:
                    print(f"  Market {i}: {pos.scaled_balance / 1e9} SOL")
            
            # Check perp positions
            perp_positions = user.get_perp_positions()
            print(f"\nPerp Positions:")
            for i, pos in enumerate(perp_positions):
                if abs(pos.base_asset_amount) > 0:
                    print(f"  Market {i}: {pos.base_asset_amount / 1e9} contracts")
        else:
            print("❌ No Drift user account found. Need to initialize.")
            
    except Exception as e:
        print(f"Error checking user account: {e}")
    finally:
        await drift_client.unsubscribe()

if __name__ == "__main__":
    asyncio.run(main())