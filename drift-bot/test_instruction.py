#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient

from driftpy.drift_client import DriftClient
from driftpy.accounts import get_spot_market_account

MAINNET_RPC = "https://api.mainnet-beta.solana.com"

async def main():
    # Load keypair
    secrets_path = Path(__file__).parent / ".secrets" / "solana-keypair.json"
    with open(secrets_path) as f:
        secret_key = json.load(f)
    keypair = Keypair.from_bytes(bytes(secret_key))
    
    # Setup
    connection = AsyncClient(MAINNET_RPC)
    drift_client = DriftClient(connection, keypair, env="mainnet")
    await drift_client.subscribe()
    
    # Try to see how deposit is built
    print("Checking DriftClient deposit method...")
    
    # Look at the drift_client object
    print(f"DriftClient type: {type(drift_client)}")
    
    # Check if there's a _build_deposit_ix method
    methods = [m for m in dir(drift_client) if 'deposit' in m.lower()]
    print(f"Methods with 'deposit': {methods}")
    
    # Try to access the program
    program = drift_client.program
    print(f"Program type: {type(program)}")
    
    # Check program methods
    if hasattr(program, 'instruction'):
        print("Program has 'instruction' attribute")
        if hasattr(program.instruction, 'deposit'):
            print("Program.instruction has 'deposit' method")
    
    # Check IDL
    if hasattr(program, 'idl'):
        print(f"IDL has {len(program.idl.instructions)} instructions")
        for i, instr in enumerate(program.idl.instructions[:10]):
            print(f"  {i}: {instr.name}")
    
    await drift_client.unsubscribe()
    await connection.close()

if __name__ == "__main__":
    asyncio.run(main())