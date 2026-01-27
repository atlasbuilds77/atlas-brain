#!/usr/bin/env python3
import json
from solders.keypair import Keypair
from mnemonic import Mnemonic

seed = "vapor fetch ribbon gold inside pledge glimpse person chapter source talent ready"
mnemo = Mnemonic("english")
seed_bytes = mnemo.to_seed(seed)
keypair = Keypair.from_seed(seed_bytes[:32])

# Need full 64 bytes: 32 secret + 32 pubkey
secret_bytes = keypair.secret()
pubkey_bytes = bytes(keypair.pubkey())
full_keypair = list(secret_bytes) + list(pubkey_bytes)

with open('.secrets/solana-keypair.json', 'w') as f:
    json.dump(full_keypair, f)

print(f"Generated keypair for: {keypair.pubkey()}")
print(f"Saved to: .secrets/solana-keypair.json")
