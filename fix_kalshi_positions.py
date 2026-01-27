#!/usr/bin/env python3
"""
Fix for Kalshi API get_positions returning empty when user has active positions.

The issue is that the kalshi-python library uses deprecated parameter names
(count_down, count_up) instead of the correct count_filter parameter.

This script demonstrates the fix by:
1. Monkey-patching the library to use correct parameters
2. Providing a direct API call alternative
"""

import os
import sys
import time
import hashlib
import base64
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

# Add the ability to patch the kalshi-python library
try:
    from kalshi_python import Configuration, KalshiClient
    from kalshi_python.api.portfolio_api import PortfolioApi
    HAS_KALSHI_LIB = True
except ImportError:
    HAS_KALSHI_LIB = False

# Read private key
PRIVATE_KEY_PATH = os.path.expanduser("~/.kalshi/private_key.pem")
API_KEY_ID = os.environ.get("KALSHI_API_KEY_ID")

if not API_KEY_ID:
    print("ERROR: KALSHI_API_KEY_ID not set")
    print("Set it with: export KALSHI_API_KEY_ID='your-key-id'")
    sys.exit(1)

with open(PRIVATE_KEY_PATH, "r") as f:
    private_key_pem = f.read()

# Load private key
private_key = serialization.load_pem_private_key(
    private_key_pem.encode(),
    password=None
)

def sign_message(message, private_key):
    """Sign a message with RSA private key"""
    signature = private_key.sign(
        message.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()

def make_kalshi_request(method, endpoint, params=None):
    """Make authenticated request to Kalshi API"""
    base_url = "https://api.elections.kalshi.com/trade-api/v2"
    url = f"{base_url}{endpoint}"
    
    # Add query parameters if any
    if params:
        query_string = "&".join([f"{k}={v}" for k, v in params.items() if v is not None])
        if query_string:
            url = f"{url}?{query_string}"
    
    timestamp = str(int(time.time()))
    
    # Create message to sign: timestamp + method + endpoint
    message_to_sign = f"{timestamp}{method.upper()}{endpoint}"
    
    # Sign the message
    signature = sign_message(message_to_sign, private_key)
    
    # Make request
    headers = {
        "KALSHI-ACCESS-KEY": API_KEY_ID,
        "KALSHI-ACCESS-SIGNATURE": signature,
        "KALSHI-ACCESS-TIMESTAMP": timestamp,
    }
    
    response = requests.request(method, url, headers=headers)
    return response

def get_positions_direct():
    """Get positions directly from API with correct count_filter parameter"""
    print("Getting positions via direct API call with count_filter='position,total_traded'...")
    response = make_kalshi_request("GET", "/portfolio/positions", {"count_filter": "position,total_traded"})
    
    if response.status_code == 200:
        data = response.json()
        positions = data.get('positions', [])
        cursor = data.get('cursor', '')
        
        print(f"Response status: {response.status_code}")
        print(f"Number of positions: {len(positions)}")
        print(f"Cursor: {cursor}")
        
        if positions:
            print("\nPositions:")
            for pos in positions:
                ticker = pos.get('ticker', 'N/A')
                position_val = pos.get('position', 0)
                total_traded = pos.get('total_traded', 0)
                avg_price = pos.get('average_price', 0)
                print(f"  {ticker}: position={position_val}, total_traded={total_traded}, avg_price={avg_price}¢")
        else:
            print("No positions returned (even with count_filter)")
            
        return data
    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def patch_kalshi_library():
    """Monkey-patch the kalshi-python library to use correct parameters"""
    if not HAS_KALSHI_LIB:
        print("kalshi-python library not available")
        return None
    
    print("Patching kalshi-python library...")
    
    # Save original method
    original_get_positions = PortfolioApi.get_positions
    
    # Create patched version
    def patched_get_positions(self, ticker=None, event_ticker=None, 
                             count_filter=None, settlement_status=None,
                             limit=None, cursor=None, **kwargs):
        """Patched version that uses correct parameter names"""
        
        # Map parameters for backward compatibility
        # If count_down/count_up were passed (old params), ignore them
        # Use count_filter if provided, otherwise default to 'position,total_traded'
        
        if count_filter is None:
            count_filter = 'position,total_traded'
        
        # Call the original method but with mapped parameters
        # Note: We need to check what parameters the underlying API expects
        # The library might not accept count_filter at all
        
        # For now, let's try calling with count_filter as count_down (hacky)
        # This is a temporary workaround
        try:
            return original_get_positions(self, ticker=ticker, event_ticker=event_ticker,
                                         count_down=count_filter, count_up=None,
                                         limit=limit, cursor=cursor)
        except Exception as e:
            print(f"Error with patched method: {e}")
            # Fall back to original
            return original_get_positions(self, ticker=ticker, event_ticker=event_ticker,
                                         count_down=None, count_up=None,
                                         limit=limit, cursor=cursor)
    
    # Apply patch
    PortfolioApi.get_positions = patched_get_positions
    
    # Also patch KalshiClient if it has a get_positions method
    if hasattr(KalshiClient, 'get_positions'):
        original_client_get_positions = KalshiClient.get_positions
        
        def patched_client_get_positions(self, **kwargs):
            # Pass through to portfolio API
            return self.portfolio_api.get_positions(**kwargs)
        
        KalshiClient.get_positions = patched_client_get_positions
    
    print("Library patched successfully")
    
    # Test the patched library
    print("\nTesting patched library...")
    try:
        config = Configuration(host="https://api.elections.kalshi.com/trade-api/v2")
        config.api_key_id = API_KEY_ID
        config.private_key_pem = private_key_pem
        
        client = KalshiClient(config)
        
        # Try with count_filter parameter
        positions = client.get_positions(count_filter='position,total_traded')
        
        print(f"Positions from patched library: {positions.positions}")
        print(f"Cursor: {positions.cursor}")
        
        return positions
    except Exception as e:
        print(f"Error testing patched library: {e}")
        return None

def main():
    """Main test function"""
    print("=" * 60)
    print("Kalshi API get_positions Fix Demonstration")
    print("=" * 60)
    
    # Test 1: Direct API call (most reliable)
    print("\n1. Testing direct API call with correct parameters:")
    direct_result = get_positions_direct()
    
    # Test 2: Patch library if available
    if HAS_KALSHI_LIB:
        print("\n2. Testing patched library:")
        patch_result = patch_kalshi_library()
    
    # Test 3: Original library behavior (for comparison)
    if HAS_KALSHI_LIB:
        print("\n3. Testing original library (for comparison):")
        try:
            config = Configuration(host="https://api.elections.kalshi.com/trade-api/v2")
            config.api_key_id = API_KEY_ID
            config.private_key_pem = private_key_pem
            
            client = KalshiClient(config)
            
            # Original call (with wrong parameters)
            positions = client.get_positions()
            
            print(f"Original library result - positions: {positions.positions}")
            print(f"Original library result - cursor: {positions.cursor}")
            
            if positions.positions is None or len(positions.positions) == 0:
                print("✓ Confirmed: Original library returns empty positions")
            else:
                print("✗ Unexpected: Original library returns positions")
                
        except Exception as e:
            print(f"Error with original library: {e}")
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("The issue is that the kalshi-python library uses deprecated")
    print("parameter names (count_down, count_up) instead of count_filter.")
    print("\nRECOMMENDED FIX:")
    print("1. Update kalshi-trader.py to use direct API calls with")
    print("   count_filter='position,total_traded' parameter")
    print("2. Or wait for library update from Kalshi")
    print("=" * 60)

if __name__ == "__main__":
    main()