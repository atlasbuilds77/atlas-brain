#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from driftpy.drift_client import DriftClient

async def main():
    # Load keypair
    with open(Path(__file__).parent / ".secrets" / "solana-keypair.json", 'r') as f:
        secret = json.load(f)
    keypair = Keypair.from_bytes(bytes(secret))
    
    print(f"Wallet: {keypair.pubkey()}")
    
    # Connect to Drift
    connection = AsyncClient("https://api.mainnet-beta.solana.com")
    drift_client = DriftClient(connection, keypair, env="mainnet")
    
    try:
        await drift_client.subscribe()
        print("✅ Connected to Drift")
        
        # Check current SOL balance
        balance = await connection.get_balance(keypair.pubkey())
        sol_balance = balance.value / 1e9
        print(f"SOL Balance: {sol_balance:.6f} SOL")
        
        # WSOL mint and ATA
        WSOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
        
        # Get WSOL ATA
        from spl.token.instructions import get_associated_token_address
        wsol_ata = get_associated_token_address(
            owner=keypair.pubkey(),
            mint=WSOL_MINT
        )
        print(f"WSOL ATA: {wsol_ata}")
        
        # Check WSOL balance
        account_info = await connection.get_account_info(wsol_ata)
        current_wsol = 0
        if account_info.value:
            from spl.token._layouts import ACCOUNT_LAYOUT
            data = account_info.value.data
            parsed = ACCOUNT_LAYOUT.parse(data)
            current_wsol = parsed.amount / 1e9
            print(f"Current WSOL Balance: {current_wsol:.6f} WSOL")
        
        # Amount to deposit (0.4 SOL)
        deposit_amount_sol = 0.4
        deposit_amount_native = int(deposit_amount_sol * 1e9)
        
        if current_wsol < deposit_amount_sol:
            print(f"\n❌ Need {deposit_amount_sol} WSOL but only have {current_wsol:.6f}")
            print("You need to wrap SOL to WSOL first.")
            print("Run: python wrap_sol.py")
            return
        
        print(f"\nDepositing {deposit_amount_sol} SOL to Drift...")
        
        # SOL spot market index is 1
        SOL_SPOT_INDEX = 1
        
        # Get deposit instruction
        print("Getting deposit instruction...")
        deposit_ixs = await drift_client.get_deposit_collateral_ix(
            deposit_amount_native,
            SOL_SPOT_INDEX,
            wsol_ata,
            sub_account_id=0,
            reduce_only=False,
            user_initialized=True
        )
        
        print(f"Got {len(deposit_ixs)} instructions")
        
        # Send transaction
        print("Sending deposit transaction...")
        tx_sig_and_slot = await drift_client.send_ixs(deposit_ixs)
        
        print(f"✅ Deposit submitted!")
        print(f"Transaction: {tx_sig_and_slot.tx_sig}")
        print(f"Slot: {tx_sig_and_slot.slot}")
        
        # Wait a bit and check new collateral
        await asyncio.sleep(5)
        
        print("\nChecking new collateral balance...")
        user = drift_client.get_user()
        free_collateral = user.get_free_collateral()
        print(f"Free collateral: ${free_collateral/1e6:.2f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await drift_client.unsubscribe()
        await connection.close()

if __name__ == "__main__":
    asyncio.run(main())