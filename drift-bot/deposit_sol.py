#!/usr/bin/env python3
import asyncio, json
from pathlib import Path
from driftpy.drift_client import DriftClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient

MAINNET_RPC = "https://api.mainnet-beta.solana.com"
SOL_SPOT_INDEX = 1  # SOL spot index on Drift
WSOL_ATA = "99LwbLt1HLLBeW83i2vSXxQpUijPdzCHr5EThCT7Jrdc"

async def main():
    kp = Keypair.from_bytes(bytes(json.load(open(Path(__file__).parent/".secrets"/"solana-keypair.json"))))
    conn = AsyncClient(MAINNET_RPC)
    client = DriftClient(conn, kp, env="mainnet")
    await client.subscribe()

    amount_sol = 0.6
    amount_native = int(amount_sol * 10**9)  # 9 decimals
    ata_pk = Pubkey.from_string(WSOL_ATA)
    print(f"Depositing {amount_sol} SOL (native {amount_native}) from {WSOL_ATA} to Drift spot index {SOL_SPOT_INDEX}...")
    try:
        tx = await client.deposit(amount_native, SOL_SPOT_INDEX, ata_pk)
        print("✅ Deposit submitted:", tx)
    except Exception as e:
        print("❌ Deposit failed:", e)
    finally:
        await client.unsubscribe()

if __name__ == "__main__":
    asyncio.run(main())
