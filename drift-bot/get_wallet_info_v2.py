#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.core import get_associated_token_address

async def main():
    # Load keypair
    with open(Path(__file__).parent / ".secrets" / "solana-keypair.json", 'r') as f:
        secret = json.load(f)
    keypair = Keypair.from_bytes(bytes(secret))
    
    # Connect to Solana
    connection = AsyncClient("https://api.mainnet-beta.solana.com")
    
    print(f"Wallet: {keypair.pubkey()}")
    
    # Get SOL balance
    balance = await connection.get_balance(keypair.pubkey())
    print(f"SOL Balance: {balance.value / 1e9:.6f} SOL")
    
    # WSOL mint address
    WSOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
    
    # Find WSOL ATA for this wallet
    wsol_ata = get_associated_token_address(
        owner=keypair.pubkey(),
        mint=WSOL_MINT
    )
    
    print(f"\nWSOL Associated Token Account (ATA): {wsol_ata}")
    
    # Check WSOL balance
    try:
        account_info = await connection.get_account_info(wsol_ata)
        if account_info.value:
            from spl.token.instructions import get_associated_token_address
            # Parse token account data
            from spl.token._layouts import ACCOUNT_LAYOUT
            import struct
            
            data = account_info.value.data
            parsed = ACCOUNT_LAYOUT.parse(data)
            balance = parsed.amount
            print(f"WSOL Balance: {balance / 1e9:.6f} WSOL")
        else:
            print("WSOL ATA doesn't exist")
    except Exception as e:
        print(f"Error checking WSOL balance: {e}")
    
    await connection.close()

if __name__ == "__main__":
    asyncio.run(main())