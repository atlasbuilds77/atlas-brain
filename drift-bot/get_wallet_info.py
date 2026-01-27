#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.async_client import AsyncToken

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
    wsol_ata = AsyncToken.get_associated_token_address(
        owner=keypair.pubkey(),
        mint=WSOL_MINT
    )
    
    print(f"\nWSOL Associated Token Account (ATA): {wsol_ata}")
    
    # Check WSOL balance
    try:
        token_client = AsyncToken(
            connection,
            WSOL_MINT,
            TOKEN_PROGRAM_ID,
            keypair
        )
        
        wsol_balance = await token_client.get_balance(wsol_ata)
        print(f"WSOL Balance: {wsol_balance.value.ui_amount:.6f} WSOL")
    except:
        print("WSOL ATA doesn't exist or has no balance")
    
    await connection.close()

if __name__ == "__main__":
    asyncio.run(main())