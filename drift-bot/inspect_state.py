#!/usr/bin/env python3
import asyncio, json
from pathlib import Path
from driftpy.drift_client import DriftClient
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient

MAINNET_RPC = "https://api.mainnet-beta.solana.com"

async def main():
    kp = Keypair.from_bytes(bytes(json.load(open(Path(__file__).parent/".secrets"/"solana-keypair.json"))))
    conn = AsyncClient(MAINNET_RPC)
    client = DriftClient(conn, kp, env="mainnet")
    await client.subscribe()
    state = client.get_state_account()
    print("State fields:", dir(state))
    try:
        print("Spot markets len:", len(state.spot_markets))
    except Exception as e:
        print("no spot_markets attr:", e)
    try:
        print("Perp markets len:", len(state.perp_markets))
    except Exception as e:
        print("no perp_markets attr:", e)
    await client.unsubscribe()

if __name__ == "__main__":
    asyncio.run(main())
