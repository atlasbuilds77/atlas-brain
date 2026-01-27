#!/usr/bin/env python3
import asyncio, json
from pathlib import Path
from driftpy.drift_client import DriftClient
from driftpy.accounts import get_spot_market_account
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient

MAINNET_RPC = "https://api.mainnet-beta.solana.com"

async def main():
    kp = Keypair.from_bytes(bytes(json.load(open(Path(__file__).parent/".secrets"/"solana-keypair.json"))))
    conn = AsyncClient(MAINNET_RPC)
    client = DriftClient(conn, kp, env="mainnet")
    await client.subscribe()
    state = client.get_state_account()
    n = state.number_of_spot_markets
    print("Spot markets count:", n)
    for i in range(n):
        m = await get_spot_market_account(client.program, i)
        name = bytes(m.name).split(b"\x00")[0].decode("utf-8", errors="ignore")
        mint = str(m.mint)
        print(i, name, mint, "decimals:", m.decimals)
    await client.unsubscribe()

if __name__ == "__main__":
    asyncio.run(main())
