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
        
        # Find deposit instruction
        for instr in program.idl.instructions:
            if instr.name == "deposit":
                print(f"Found deposit instruction")
                print(f"Accounts:")
                for acc in instr.accounts:
                    print(f"  - {acc.name} (Python name: {acc.name})")
                break
        
    finally:
        await drift_client.unsubscribe()
        await connection.close()

if __name__ == "__main__":
    asyncio.run(main())