#!/usr/bin/env python3
import json
from solders.keypair import Keypair
from mnemonic import Mnemonic

seed = "sponsor lawsuit stereo observe amused thunder moment perfect fruit gauge emotion firm"
mnemo = Mnemonic("english")
seed_bytes = mnemo.to_seed(seed)
keypair = Keypair.from_seed(seed_bytes[:32])

# Full 64 bytes
secret_bytes = keypair.secret()
pubkey_bytes = bytes(keypair.pubkey())
full_keypair = list(secret_bytes) + list(pubkey_bytes)

with open('.secrets/drift-trading-keypair.json', 'w') as f:
    json.dump(full_keypair, f)

print(f"Address: {keypair.pubkey()}")
print(f"Keypair saved to: .secrets/drift-trading-keypair.json")
