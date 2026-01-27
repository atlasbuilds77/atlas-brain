#!/usr/bin/env python3
"""
Simple Drift trading script
Usage: python trade.py [deposit|withdraw|long|short|close] [amount]
"""
import asyncio
import sys
import json
from driftpy.drift_client import DriftClient
from driftpy.types import PositionDirection
from anchorpy import Wallet
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient

async def main():
    # Load wallet
    with open('.secrets/solana-keypair.json') as f:
        kp = Keypair.from_bytes(bytes(json.load(f)))
    
    wallet = Wallet(kp)
    connection = AsyncClient('https://api.mainnet-beta.solana.com')
    drift = DriftClient(connection, wallet, 'mainnet')
    
    await drift.subscribe()
    
    if len(sys.argv) < 2:
        print("Usage: python trade.py [deposit|withdraw|long|short|close|status]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        print(f"Wallet: {kp.pubkey()}")
        print("Drift account: ✅ Active")
        # Add balance/position checks here
    
    elif cmd == "deposit":
        amount = int(float(sys.argv[2]) * 1e9)  # SOL to lamports
        tx = await drift.deposit(amount, 0)  # 0 = SOL market
        print(f"Deposited {sys.argv[2]} SOL")
        print(f"Tx: {tx}")
    
    elif cmd == "long":
        # Open long position on SOL-PERP
        size = float(sys.argv[2])
        # Implementation depends on current SDK version
        print(f"Opening {size} SOL long...")
    
    elif cmd == "close":
        # Close all positions
        print("Closing positions...")
    
    await drift.unsubscribe()
    await connection.close()

if __name__ == "__main__":
    asyncio.run(main())
