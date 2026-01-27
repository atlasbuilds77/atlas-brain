#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solders.instruction import Instruction
from spl.token.instructions import (
    create_associated_token_account,
    get_associated_token_address,
    sync_native,
)
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID

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
    sol_balance = balance.value / 1e9
    print(f"SOL Balance: {sol_balance:.6f} SOL")
    
    # WSOL mint address
    WSOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
    
    # Find or create WSOL ATA
    wsol_ata = get_associated_token_address(
        owner=keypair.pubkey(),
        mint=WSOL_MINT
    )
    
    print(f"\nWSOL Associated Token Account (ATA): {wsol_ata}")
    
    # Check if ATA exists
    account_info = await connection.get_account_info(wsol_ata)
    if not account_info.value:
        print("Creating WSOL ATA...")
        # Create ATA instruction
        create_ata_ix = create_associated_token_account(
            payer=keypair.pubkey(),
            owner=keypair.pubkey(),
            mint=WSOL_MINT
        )
        
        # Send transaction
        recent_blockhash = (await connection.get_latest_blockhash()).value.blockhash
        tx = Transaction(
            fee_payer=keypair.pubkey(),
            recent_blockhash=recent_blockhash,
            instructions=[create_ata_ix]
        )
        tx.sign(keypair)
        
        tx_sig = await connection.send_transaction(tx)
        print(f"Created WSOL ATA: {tx_sig.value}")
        await connection.confirm_transaction(tx_sig.value)
    
    # Amount to wrap (0.5 SOL, leaving some for gas)
    wrap_amount_sol = 0.5
    wrap_amount_lamports = int(wrap_amount_sol * 1e9)
    
    if sol_balance < wrap_amount_sol + 0.01:  # Need extra for gas
        print(f"❌ Insufficient SOL. Need {wrap_amount_sol + 0.01:.2f} SOL, have {sol_balance:.6f} SOL")
        return
    
    print(f"\nWrapping {wrap_amount_sol} SOL to WSOL...")
    
    # Create transfer instruction to send SOL to WSOL ATA
    transfer_ix = transfer(
        TransferParams(
            from_pubkey=keypair.pubkey(),
            to_pubkey=wsol_ata,
            lamports=wrap_amount_lamports
        )
    )
    
    # Create sync_native instruction to update token account balance
    sync_ix = sync_native(
        TOKEN_PROGRAM_ID,
        wsol_ata
    )
    
    # Send transaction
    recent_blockhash = (await connection.get_latest_blockhash()).value.blockhash
    tx = Transaction(
        fee_payer=keypair.pubkey(),
        recent_blockhash=recent_blockhash,
        instructions=[transfer_ix, sync_ix]
    )
    tx.sign(keypair)
    
    tx_sig = await connection.send_transaction(tx)
    print(f"Wrap transaction sent: {tx_sig.value}")
    
    # Confirm
    await connection.confirm_transaction(tx_sig.value)
    print("✅ SOL wrapped to WSOL!")
    
    # Check new balances
    balance = await connection.get_balance(keypair.pubkey())
    print(f"\nNew SOL Balance: {balance.value / 1e9:.6f} SOL")
    
    # Check WSOL balance
    account_info = await connection.get_account_info(wsol_ata)
    if account_info.value:
        from spl.token._layouts import ACCOUNT_LAYOUT
        data = account_info.value.data
        parsed = ACCOUNT_LAYOUT.parse(data)
        wsol_balance = parsed.amount / 1e9
        print(f"WSOL Balance: {wsol_balance:.6f} WSOL")
    
    await connection.close()

if __name__ == "__main__":
    asyncio.run(main())