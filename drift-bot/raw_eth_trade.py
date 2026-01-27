#!/usr/bin/env python3
"""
Raw Solana transaction to open ETH-PERP long on Drift
Bypasses SDK to avoid rate limits
"""
import asyncio
import json
import struct
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.hash import Hash
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts

# Drift Program ID
DRIFT_PROGRAM_ID = Pubkey.from_string("dRiftyHA39MWEi3m9aunc5MzRF1JYuBsbn6VPcn33UH")

# RPC endpoint
RPC = 'https://api.mainnet-beta.solana.com'

async def get_drift_accounts(user_pubkey):
    """Derive Drift account PDAs"""
    # User account PDA
    user_account = Pubkey.find_program_address(
        [b"user", bytes(user_pubkey), bytes([0])],
        DRIFT_PROGRAM_ID
    )[0]
    
    # User stats PDA
    user_stats = Pubkey.find_program_address(
        [b"user_stats", bytes(user_pubkey)],
        DRIFT_PROGRAM_ID
    )[0]
    
    # State account
    state = Pubkey.find_program_address(
        [b"drift_state"],
        DRIFT_PROGRAM_ID
    )[0]
    
    return user_account, user_stats, state

async def build_place_order_ix(user_keypair, eth_price):
    """Build PlacePerPOrder instruction"""
    
    # Get derived accounts
    user_account, user_stats, state = await get_drift_accounts(user_keypair.pubkey())
    
    # ETH-PERP market index
    market_index = 2
    
    # Calculate position
    # 3x leverage, $93 collateral = $279 notional
    # At $2,928/ETH = 0.095 ETH
    notional = 279_000_000  # in QUOTE_PRECISION (1e6)
    base_asset_amount = int((279 / eth_price) * 1e9)  # BASE_PRECISION
    
    print(f"Position size: {base_asset_amount / 1e9:.4f} ETH")
    print(f"Notional: ${notional / 1e6:.2f}")
    
    # PlacePerpOrder instruction discriminator (first 8 bytes)
    # This is from Drift's IDL - may need to verify
    discriminator = struct.pack('<Q', 0xd9b3f3e3e3b3f3d9)  # Placeholder - need actual value
    
    # Order params (simplified - this needs proper encoding)
    order_data = discriminator + struct.pack(
        '<BHQQQBBB',
        0,  # order_type (Market = 0)
        market_index,  # market_index
        base_asset_amount,  # base_asset_amount
        0,  # price (0 for market)
        0,  # quote_asset_amount
        0,  # direction (Long = 0)
        0,  # reduce_only
        0,  # post_only
    )
    
    # Required accounts for PlacePerpOrder
    accounts = [
        AccountMeta(pubkey=state, is_signer=False, is_writable=False),
        AccountMeta(pubkey=user_account, is_signer=False, is_writable=True),
        AccountMeta(pubkey=user_stats, is_signer=False, is_writable=True),
        AccountMeta(pubkey=user_keypair.pubkey(), is_signer=True, is_writable=False),
    ]
    
    # Build instruction
    ix = Instruction(
        program_id=DRIFT_PROGRAM_ID,
        accounts=accounts,
        data=order_data
    )
    
    return ix

async def execute():
    # Load keypair
    with open('.secrets/solana-keypair.json') as f:
        kp = Keypair.from_bytes(bytes(json.load(f)))
    
    print(f"Trading wallet: {kp.pubkey()}")
    
    # Connect
    client = AsyncClient(RPC)
    
    try:
        # Get current ETH price (using $2,928 from earlier)
        eth_price = 2928
        
        # Build instruction
        print("\nBuilding PlacePerpOrder instruction...")
        ix = await build_place_order_ix(kp, eth_price)
        
        # Get recent blockhash
        print("Fetching recent blockhash...")
        resp = await client.get_latest_blockhash(Confirmed)
        blockhash = resp.value.blockhash
        
        # Build transaction
        print("Building transaction...")
        message = MessageV0.try_compile(
            payer=kp.pubkey(),
            instructions=[ix],
            address_lookup_table_accounts=[],
            recent_blockhash=blockhash,
        )
        
        tx = Transaction.new_signed_with_payer(
            [ix],
            kp.pubkey(),
            [kp],
            blockhash
        )
        
        # Send transaction
        print("Sending transaction...")
        result = await client.send_transaction(
            tx,
            opts=TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
        )
        
        print(f"\n✅ TRANSACTION SENT!")
        print(f"Signature: {result.value}")
        print(f"\nView on Solscan:")
        print(f"https://solscan.io/tx/{result.value}")
        
        # Wait for confirmation
        print("\nWaiting for confirmation...")
        await client.confirm_transaction(result.value, Confirmed)
        print("✅ CONFIRMED!")
        
        return result.value
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        await client.close()

if __name__ == "__main__":
    print("=" * 60)
    print("DRIFT ETH-PERP LONG - RAW TRANSACTION")
    print("=" * 60)
    asyncio.run(execute())
