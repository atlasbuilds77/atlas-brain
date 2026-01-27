#!/usr/bin/env python3
"""
Withdraw SOL from Drift back to wallet
"""
import asyncio
import json
from driftpy.drift_client import DriftClient
from driftpy.account_subscription_config import AccountSubscriptionConfig
from anchorpy import Wallet
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient

RPC = 'https://api.mainnet-beta.solana.com'

async def withdraw_all():
    # Load keypair
    with open('.secrets/solana-keypair.json') as f:
        kp = Keypair.from_bytes(bytes(json.load(f)))
    
    print(f"Wallet: {kp.pubkey()}")
    
    # Connect (minimal config to avoid rate limits)
    wallet = Wallet(kp)
    connection = AsyncClient(RPC)
    
    try:
        # Simple connection
        drift = DriftClient(
            connection,
            wallet,
            "mainnet",
            account_subscription=AccountSubscriptionConfig("cached")
        )
        
        await drift.subscribe()
        print("✅ Connected to Drift")
        
        user = drift.get_user()
        
        # Get spot positions (collateral)
        spot_positions = user.get_spot_positions()
        
        # Find SOL position (market index 1)
        sol_balance = 0
        for pos in spot_positions:
            if pos.market_index == 1 and pos.scaled_balance > 0:
                sol_balance = pos.scaled_balance / 1e9  # Convert from lamports
                print(f"SOL in Drift: {sol_balance:.4f}")
                break
        
        if sol_balance == 0:
            print("No SOL to withdraw")
            return
        
        # Withdraw all SOL
        print(f"\nWithdrawing {sol_balance:.4f} SOL...")
        amount_lamports = int(sol_balance * 1e9)
        
        tx = await drift.withdraw(
            amount_lamports,
            1  # market_index for SOL
        )
        
        print(f"✅ WITHDRAWAL COMPLETE!")
        print(f"   Amount: {sol_balance:.4f} SOL")
        print(f"   Tx: {tx}")
        
        return tx
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await drift.unsubscribe()
        await connection.close()

if __name__ == "__main__":
    print("=" * 60)
    print("DRIFT WITHDRAWAL - SOL → WALLET")
    print("=" * 60)
    asyncio.run(withdraw_all())
