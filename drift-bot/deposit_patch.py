#!/usr/bin/env python3
"""
Manual deposit instruction for Drift Protocol when client.deposit() fails.
Constructs deposit instruction directly using anchorpy.
"""
import asyncio
import json
from pathlib import Path
from typing import Optional

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction import Transaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed

# Drift imports
from driftpy.drift_client import DriftClient
from driftpy.accounts import get_spot_market_account, get_state_account
from driftpy.constants.numeric_constants import QUOTE_PRECISION, SPOT_BALANCE_PRECISION

# Anchorpy for instruction building
from anchorpy import Program, Context
from anchorpy.provider import Wallet

# Constants
MAINNET_RPC = "https://api.mainnet-beta.solana.com"
SOL_SPOT_INDEX = 1  # SOL spot market index
WSOL_ATA = "99LwbLt1HLLBeW83i2vSXxQpUijPdzCHr5EThCT7Jrdc"
AMOUNT_SOL = 0.6
AMOUNT_NATIVE = int(AMOUNT_SOL * 10**9)  # 9 decimals for SOL

async def load_keypair() -> Keypair:
    """Load Solana keypair from secrets file"""
    secrets_path = Path(__file__).parent / ".secrets" / "solana-keypair.json"
    with open(secrets_path) as f:
        secret_key = json.load(f)
    return Keypair.from_bytes(bytes(secret_key))

async def check_wsol_balance(connection: AsyncClient, wsol_ata: Pubkey) -> bool:
    """Check if WSOL ATA has sufficient balance"""
    try:
        balance_resp = await connection.get_token_account_balance(wsol_ata)
        if balance_resp.value:
            balance = int(balance_resp.value.amount)
            print(f"WSOL ATA balance: {balance / 10**9:.6f} SOL")
            if balance >= AMOUNT_NATIVE:
                print(f"✅ Sufficient balance for deposit ({AMOUNT_SOL} SOL)")
                return True
            else:
                print(f"❌ Insufficient balance. Need {AMOUNT_SOL} SOL, have {balance / 10**9:.6f} SOL")
                return False
    except Exception as e:
        print(f"❌ Error checking WSOL balance: {e}")
        return False
    return False

async def fetch_drift_state(drift_client: DriftClient):
    """Fetch and display Drift state information"""
    print("\n=== Drift State ===")
    
    # Get state account
    state = drift_client.get_state_account()
    print(f"Number of spot markets: {state.number_of_spot_markets}")
    
    # Get SOL spot market
    sol_market = await get_spot_market_account(drift_client.program, SOL_SPOT_INDEX)
    market_name = bytes(sol_market.name).split(b"\x00")[0].decode("utf-8", errors="ignore")
    print(f"SOL spot market ({SOL_SPOT_INDEX}): {market_name}")
    print(f"  Mint: {sol_market.mint}")
    print(f"  Decimals: {sol_market.decimals}")
    
    return state, sol_market

async def initialize_user_if_needed(
    drift_client: DriftClient,
    keypair: Keypair
) -> bool:
    """Initialize user account if it doesn't exist"""
    print("\n=== Checking User Account ===")
    
    try:
        # Try to get user account
        user_account = drift_client.get_user_account()
        print("✅ User account already initialized")
        return True
    except Exception as e:
        print("User account not initialized, initializing with drift_client.initialize_user()...")
        
        try:
            # Use drift_client's initialize_user method
            tx_sig = await drift_client.initialize_user(sub_account_id=0)
            print(f"✅ User initialized successfully! Transaction: {tx_sig}")
            return True
            
        except Exception as init_e:
            print(f"❌ Error initializing user: {init_e}")
            return False

async def build_deposit_instruction(
    drift_client: DriftClient,
    keypair: Keypair,
    wsol_ata: Pubkey,
    amount_native: int,
    market_index: int
) -> Optional[Transaction]:
    """
    Manually construct deposit instruction using anchorpy
    """
    print("\n=== Building Deposit Instruction ===")
    
    # Get program and provider
    program = drift_client.program
    provider = program.provider
    
    # Get required accounts
    state = drift_client.get_state_account()
    spot_market = await get_spot_market_account(program, market_index)
    
    # Derive PDAs
    authority = keypair.pubkey()
    
    # Spot market vault PDA
    spot_market_vault = Pubkey.find_program_address(
        [b"spot_market_vault", market_index.to_bytes(1, "little")],
        program.program_id
    )[0]
    
    # Drift signer PDA
    drift_signer = Pubkey.find_program_address(
        [b"drift_signer"],
        program.program_id
    )[0]
    
    # User stats PDA (using drift_client method)
    user_stats_pk = drift_client.get_user_stats_public_key()
    
    # User account PDA (using drift_client method for subaccount 0)
    user_account = drift_client.get_user_account_public_key()
    
    # Token program
    token_program = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    
    print(f"Authority: {authority}")
    print(f"WSOL ATA: {wsol_ata}")
    print(f"Spot Market Vault: {spot_market_vault}")
    print(f"Drift Signer: {drift_signer}")
    print(f"User Stats: {user_stats_pk}")
    print(f"User Account: {user_account}")
    print(f"Amount: {amount_native} native units ({amount_native / 10**9:.6f} SOL)")
    
    # Build the instruction
    try:
        # Build accounts dict - based on driftpy source code
        # Get state account pubkey
        state_account_pubkey = drift_client.get_state_public_key()
        
        # Get spot market public key
        from driftpy.addresses import get_spot_market_public_key
        spot_market_pk = get_spot_market_public_key(drift_client.program_id, market_index)
        
        # Get user stats public key
        user_stats_pk = drift_client.get_user_stats_public_key()
        
        accounts_dict = {
            "state": state_account_pubkey,
            "spot_market": spot_market_pk,  # Note: from driftpy source
            "spot_market_vault": spot_market_vault,
            "user": user_account,
            "user_stats": user_stats_pk,  # Note: from driftpy source
            "user_token_account": wsol_ata,
            "authority": authority,
            "token_program": token_program,
        }
        
        print(f"\nBuilding deposit instruction with:")
        print(f"  marketIndex: {market_index}")
        print(f"  amount: {amount_native}")
        print(f"  reduceOnly: False")
        
        # Create instruction using program.instruction (no await needed)
        ix = program.instruction["deposit"](
            market_index,  # marketIndex (u16)
            amount_native,  # amount (u64)  
            False,  # reduceOnly (bool)
            ctx=Context(accounts=accounts_dict)
        )
        
        print("✅ Instruction built successfully")
        return ix
        
    except Exception as e:
        print(f"❌ Error building instruction: {e}")
        import traceback
        traceback.print_exc()
        return None

async def send_deposit_tx(
    drift_client: DriftClient,
    instruction
) -> bool:
    """Send and confirm the deposit transaction using drift_client"""
    print("\n=== Sending Deposit Transaction ===")
    
    try:
        print("Sending transaction via drift_client.send_ixs...")
        
        # Use drift_client to send the instruction
        # This handles transaction building, signing, and sending
        tx_sig_and_slot = await drift_client.send_ixs(instruction)
        
        print(f"Transaction signature: {tx_sig_and_slot.tx_sig}")
        print(f"Slot: {tx_sig_and_slot.slot}")
        
        # The transaction is already confirmed by send_ixs
        print("✅ Deposit transaction submitted successfully!")
        
        # We can check if it was successful
        # send_ixs should raise an exception if the transaction fails
        return True
            
    except Exception as e:
        print(f"❌ Error sending transaction: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function to execute manual deposit"""
    print("=" * 60)
    print("DRIFT MANUAL DEPOSIT PATCH")
    print("=" * 60)
    print(f"Depositing: {AMOUNT_SOL} SOL ({AMOUNT_NATIVE} native units)")
    print(f"WSOL ATA: {WSOL_ATA}")
    print(f"Spot Market Index: {SOL_SPOT_INDEX}")
    print("=" * 60)
    
    # Load keypair
    print("\nLoading keypair...")
    keypair = await load_keypair()
    print(f"Wallet: {keypair.pubkey()}")
    
    # Setup connection and client
    print("\nConnecting to Solana...")
    connection = AsyncClient(MAINNET_RPC)
    drift_client = DriftClient(connection, keypair, env="mainnet")
    
    try:
        await drift_client.subscribe()
        print("✅ Connected to Drift")
        
        # Check WSOL balance
        wsol_ata_pubkey = Pubkey.from_string(WSOL_ATA)
        if not await check_wsol_balance(connection, wsol_ata_pubkey):
            print("❌ Cannot proceed without sufficient WSOL balance")
            return
        
        # Fetch Drift state
        state, sol_market = await fetch_drift_state(drift_client)
        
        # Initialize user if needed
        if not await initialize_user_if_needed(drift_client, keypair):
            print("❌ Cannot proceed without user initialization")
            return
        
        # Try to get deposit instruction using drift_client's method
        print("\n=== Getting Deposit Instruction from drift_client ===")
        try:
            # Use drift_client's method to get the deposit instruction
            # This should handle all account initialization
            deposit_ixs = await drift_client.get_deposit_collateral_ix(
                AMOUNT_NATIVE,
                SOL_SPOT_INDEX,
                wsol_ata_pubkey,
                sub_account_id=0,
                reduce_only=False,
                user_initialized=True  # We just initialized it
            )
            
            print(f"✅ Got {len(deposit_ixs)} deposit instructions")
            
            # Send transaction
            print("\n=== Sending Deposit Transaction ===")
            tx_sig_and_slot = await drift_client.send_ixs(deposit_ixs)
            print(f"✅ Deposit transaction submitted successfully!")
            print(f"Transaction signature: {tx_sig_and_slot.tx_sig}")
            print(f"Slot: {tx_sig_and_slot.slot}")
            
            success = True
            
        except Exception as e:
            print(f"❌ Error getting or sending deposit instruction: {e}")
            import traceback
            traceback.print_exc()
            success = False
        
        if success:
            print("\n" + "=" * 60)
            print("✅ DEPOSIT SUCCESSFUL!")
            print("=" * 60)
            
            # Run scalper.py if deposit was successful
            print("\nStarting scalper bot...")
            await run_scalper(drift_client)
        else:
            print("\n❌ Deposit failed")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await drift_client.unsubscribe()
        await connection.close()

async def run_scalper(drift_client: DriftClient):
    """Run the scalper bot after successful deposit"""
    print("\n=== Starting Scalper Bot ===")
    
    # Import scalper module
    import sys
    sys.path.append(str(Path(__file__).parent))
    
    try:
        # We'll run scalper in a separate process to avoid async conflicts
        print("Launching scalper.py...")
        
        # Use subprocess to run scalper
        import subprocess
        process = subprocess.Popen(
            [str(Path(__file__).parent / "bin" / "python"), "scalper.py"],
            cwd=str(Path(__file__).parent)
        )
        
        print(f"Scalper started with PID: {process.pid}")
        print("Scalper is now running live. Check terminal for output.")
        
        # Wait a bit to ensure it starts
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"Error starting scalper: {e}")
        print("You can manually run: python scalper.py")

if __name__ == "__main__":
    asyncio.run(main())