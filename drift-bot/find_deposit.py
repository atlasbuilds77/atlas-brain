#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path

from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient

from driftpy.drift_client import DriftClient

async def main():
    # Load keypair
    secrets_path = Path(__file__).parent / ".secrets" / "solana-keypair.json"
    with open(secrets_path) as f:
        secret_key = json.load(f)
    keypair = Keypair.from_bytes(bytes(secret_key))
    
    # Setup
    connection = AsyncClient("https://api.mainnet-beta.solana.com")
    drift_client = DriftClient(connection, keypair, env="mainnet")
    
    try:
        await drift_client.subscribe()
        
        program = drift_client.program
        
        # Search for deposit instruction
        print("Searching for deposit instruction in IDL...")
        deposit_instr = None
        for instr in program.idl.instructions:
            if instr.name == "deposit":
                deposit_instr = instr
                break
        
        if deposit_instr:
            print(f"\n✅ Found deposit instruction!")
            print(f"Name: {deposit_instr.name}")
            print(f"\nAccounts:")
            for acc in deposit_instr.accounts:
                print(f"  - {acc.name} (is_signer: {acc.is_signer}, is_mut: {acc.is_mut})")
            
            print(f"\nArguments:")
            for arg in deposit_instr.args:
                print(f"  - {arg.name}: {arg}")
        else:
            print("\n❌ Deposit instruction not found")
            print("\nSimilar instructions:")
            for instr in program.idl.instructions:
                if "deposit" in instr.name.lower():
                    print(f"  - {instr.name}")
        
        # Also check for spot_market::deposit or similar
        print("\n\nChecking all instructions for spot market operations:")
        spot_instructions = []
        for instr in program.idl.instructions:
            if any(word in instr.name.lower() for word in ["spot", "deposit", "withdraw"]):
                spot_instructions.append(instr)
        
        for instr in spot_instructions[:20]:  # Show first 20
            print(f"  - {instr.name}")
        
    finally:
        await drift_client.unsubscribe()
        await connection.close()

if __name__ == "__main__":
    asyncio.run(main())