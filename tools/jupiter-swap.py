#!/usr/bin/env python3
"""
Jupiter Swap Tool - Swap tokens via Jupiter aggregator
Usage: python jupiter-swap.py <from_token> <to_token> <amount>
Example: python jupiter-swap.py So11111111111111111111111111111111111111112 EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 0.4
"""

import sys
import json
import requests
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.api import Client

# Token addresses
WSOL = "So11111111111111111111111111111111111111112"
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

def get_quote(input_mint, output_mint, amount_lamports):
    """Get quote from Jupiter"""
    url = "https://quote-api.jup.ag/v6/quote"
    params = {
        "inputMint": input_mint,
        "outputMint": output_mint,
        "amount": amount_lamports,
        "slippageBps": 50  # 0.5% slippage
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_swap_transaction(quote, user_public_key):
    """Get swap transaction from Jupiter"""
    url = "https://quote-api.jup.ag/v6/swap"
    payload = {
        "quoteResponse": quote,
        "userPublicKey": str(user_public_key),
        "wrapAndUnwrapSol": True,
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 4:
        print("Usage: python jupiter-swap.py <from_token> <to_token> <amount>")
        print(f"Example: python jupiter-swap.py {WSOL} {USDC} 0.4")
        sys.exit(1)
    
    from_token = sys.argv[1]
    to_token = sys.argv[2]
    amount_sol = float(sys.argv[3])
    
    # Convert SOL to lamports (1 SOL = 1e9 lamports)
    amount_lamports = int(amount_sol * 1e9)
    
    # Load keypair
    with open('/Users/atlasbuilds/clawd/drift-bot/.secrets/solana-keypair.json') as f:
        keypair_data = json.load(f)
    
    keypair = Keypair.from_bytes(bytes(keypair_data))
    
    print(f"Wallet: {keypair.pubkey()}")
    print(f"Swapping {amount_sol} {from_token[:8]}... → {to_token[:8]}...")
    
    # Get quote
    print("\n1. Getting quote from Jupiter...")
    quote = get_quote(from_token, to_token, amount_lamports)
    
    out_amount = int(quote['outAmount']) / 1e6  # USDC has 6 decimals
    print(f"   Expected output: ~${out_amount:.2f} USDC")
    print(f"   Price impact: {quote.get('priceImpactPct', 0)}%")
    
    # Get swap transaction
    print("\n2. Building swap transaction...")
    swap_response = get_swap_transaction(quote, keypair.pubkey())
    
    # Deserialize and sign transaction
    print("\n3. Signing transaction...")
    tx_bytes = bytes(swap_response['swapTransaction'], 'utf-8')
    import base64
    tx_data = base64.b64decode(tx_bytes)
    tx = VersionedTransaction.deserialize(tx_data)
    tx.sign([keypair])
    
    # Send transaction
    print("\n4. Sending to Solana...")
    client = Client("https://api.mainnet-beta.solana.com")
    result = client.send_raw_transaction(bytes(tx))
    
    print(f"\n✅ Swap submitted!")
    print(f"   Signature: {result.value}")
    print(f"   Explorer: https://solscan.io/tx/{result.value}")

if __name__ == "__main__":
    main()
