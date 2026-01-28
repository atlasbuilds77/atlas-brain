#!/usr/bin/env python3
"""
Test Atlas Eyes API heartbeat endpoints
"""

import requests
import time
import sys


def test_api():
    """Test API endpoints"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Atlas Eyes API")
    print("=" * 60)
    
    # Check status
    print("\n1. Checking API status...")
    try:
        resp = requests.get(f"{base_url}/api/status", timeout=2)
        status = resp.json()
        print(f"   Status: {status.get('status')}")
        
        if status.get('status') != 'running':
            # Start extraction
            print("\n2. Starting motion extraction...")
            resp = requests.post(f"{base_url}/api/start", 
                                json={'algorithm': 'frame_diff'})
            if resp.status_code == 200:
                print("   ✓ Started")
            else:
                print(f"   ❌ Failed: {resp.text}")
                return
            
            time.sleep(2)
    except requests.exceptions.ConnectionError:
        print("   ❌ API not running. Start with:")
        print("      cd ~/clawd/atlas-eyes/src && python3 atlas_api.py")
        return
    
    print("\n3. Testing heartbeat detection...")
    print("   (Collecting data for 15 seconds...)")
    
    for i in range(15):
        time.sleep(1)
        try:
            resp = requests.get(f"{base_url}/api/heartbeat")
            data = resp.json()
            
            buffer_fill = data.get('buffer_fill', 0) * 100
            ready = data.get('ready', False)
            detected = data.get('detected', False)
            
            print(f"   [{i+1:2d}s] Buffer: {buffer_fill:5.1f}% | ", end="")
            
            if ready:
                if detected:
                    bpm = data.get('bpm')
                    conf = data.get('confidence', 0)
                    print(f"❤️  BPM: {bpm:.1f} (confidence: {conf:.2f})")
                else:
                    print("No heartbeat detected")
            else:
                print("Collecting samples...")
        
        except Exception as e:
            print(f"   Error: {e}")
    
    # Final check
    print("\n4. Final heartbeat check...")
    resp = requests.get(f"{base_url}/api/heartbeat")
    data = resp.json()
    
    print(f"   Detected: {data.get('detected')}")
    print(f"   BPM: {data.get('bpm')}")
    print(f"   Confidence: {data.get('confidence')}")
    
    # Test frequency spectrum endpoint
    print("\n5. Testing frequency spectrum endpoint...")
    resp = requests.get(f"{base_url}/api/frequency")
    spectrum = resp.json()
    
    print(f"   Ready: {spectrum.get('ready')}")
    print(f"   Samples: {spectrum.get('sample_count')}")
    print(f"   Frequency bins: {len(spectrum.get('frequencies', []))}")
    
    if len(spectrum.get('frequencies', [])) > 0:
        print(f"   Frequency range: {spectrum['frequencies'][0]:.2f} - {spectrum['frequencies'][-1]:.2f} Hz")
    
    print("\n✓ API test complete")


if __name__ == '__main__':
    test_api()
