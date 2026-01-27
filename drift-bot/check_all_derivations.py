#!/usr/bin/env python3
from mnemonic import Mnemonic
from solders.keypair import Keypair
from solders.derivation_path import DerivationPath

seed = "sponsor lawsuit stereo observe amused thunder moment perfect fruit gauge emotion firm"
mnemo = Mnemonic("english")
seed_bytes = mnemo.to_seed(seed)

print("Checking different derivation paths:")
print("="*60)

# Default (no derivation)
kp = Keypair.from_seed(seed_bytes[:32])
print(f"Direct seed (no derivation): {kp.pubkey()}")

# Common Solana derivation paths
paths = [
    "m/44'/501'/0'/0'",    # Standard
    "m/44'/501'/0'",       # Phantom/Solflare
    "m/44'/501'/0'/0",     # Alternative
    "m/44'/501'/1'/0'",    # Account 1
]

for path_str in paths:
    try:
        path = DerivationPath(path_str)
        # This won't work with solders directly, need another approach
        print(f"{path_str}: (need different library)")
    except Exception as e:
        print(f"{path_str}: Error - {e}")

print("\nTarget address: 28Gv5ncMyeS5oHYgsBd9r857dpvRKqw5ttc1nKN6UxXj")
