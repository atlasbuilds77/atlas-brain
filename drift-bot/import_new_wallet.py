#!/usr/bin/env python3
import json
from solders.keypair import Keypair
from mnemonic import Mnemonic

seed = "sponsor lawsuit stereo observe amused thunder moment perfect fruit gauge emotion firm"
mnemo = Mnemonic("english")
seed_bytes = mnemo.to_seed(seed)
keypair = Keypair.from_seed(seed_bytes[:32])

# Need full 64 bytes: 32 secret + 32 pubkey
secret_bytes = keypair.secret()
pubkey_bytes = bytes(keypair.pubkey())
full_keypair = list(secret_bytes) + list(pubkey_bytes)

with open('.secrets/drift-keypair-new.json', 'w') as f:
    json.dump(full_keypair, f)

with open('.secrets/drift-wallet-new.json', 'w') as f:
    json.dump({
        "address": str(keypair.pubkey()),
        "seed_phrase": seed,
        "network": "solana-mainnet",
        "created": "2026-01-26",
        "purpose": "Drift Protocol - Orion's main trading account"
    }, f, indent=2)

print(f"New Drift Wallet: {keypair.pubkey()}")
print(f"Keypair saved to: .secrets/drift-keypair-new.json")
