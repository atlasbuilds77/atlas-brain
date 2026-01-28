#!/usr/bin/env python3
"""
Test script for Atlas Eyes API
Verifies all endpoints are working correctly
"""

import requests
import socketio
import time
import sys
from colorama import init, Fore, Style

init(autoreset=True)

API_URL = "http://localhost:5001"

def print_success(msg):
    print(f"{Fore.GREEN}✅ {msg}{Style.RESET_ALL}")

def print_error(msg):
    print(f"{Fore.RED}❌ {msg}{Style.RESET_ALL}")

def print_info(msg):
    print(f"{Fore.CYAN}ℹ️  {msg}{Style.RESET_ALL}")

def test_endpoint(name, url, expected_keys=None):
    """Test a REST endpoint"""
    print_info(f"Testing {name}...")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"{name} returned 200 OK")
            
            if expected_keys:
                missing = [k for k in expected_keys if k not in data]
                if missing:
                    print_error(f"Missing keys: {missing}")
                    return False
                else:
                    print_success(f"All expected keys present: {expected_keys}")
            
            print(f"   Response: {data}")
            return True
        else:
            print_error(f"{name} returned {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Connection failed - is the server running on {API_URL}?")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_websocket():
    """Test WebSocket connection"""
    print_info("Testing WebSocket connection...")
    
    connected = False
    data_received = False
    
    sio = socketio.Client()
    
    @sio.on('connect')
    def on_connect():
        nonlocal connected
        connected = True
        print_success("WebSocket connected")
    
    @sio.on('data')
    def on_data(data):
        nonlocal data_received
        data_received = True
        print_success(f"Received data update: {list(data.keys())}")
    
    @sio.on('disconnect')
    def on_disconnect():
        print_info("WebSocket disconnected")
    
    try:
        sio.connect(API_URL, wait_timeout=5)
        
        # Wait for data
        print_info("Waiting for data stream (5 seconds)...")
        time.sleep(5)
        
        sio.disconnect()
        
        if connected and data_received:
            print_success("WebSocket test passed")
            return True
        elif connected:
            print_error("WebSocket connected but no data received")
            return False
        else:
            print_error("WebSocket connection failed")
            return False
            
    except Exception as e:
        print_error(f"WebSocket error: {e}")
        return False

def main():
    print(f"\n{Fore.YELLOW}{'='*60}")
    print(f"Atlas Eyes API Test Suite")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    results = {}
    
    # Test REST endpoints
    print(f"\n{Fore.YELLOW}Testing REST Endpoints:{Style.RESET_ALL}\n")
    
    results['status'] = test_endpoint(
        "GET /api/status",
        f"{API_URL}/api/status",
        expected_keys=['status']
    )
    
    print()
    results['motion'] = test_endpoint(
        "GET /api/motion",
        f"{API_URL}/api/motion"
    )
    
    print()
    results['heartbeat'] = test_endpoint(
        "GET /api/heartbeat",
        f"{API_URL}/api/heartbeat",
        expected_keys=['detected', 'bpm', 'confidence']
    )
    
    print()
    results['tremor'] = test_endpoint(
        "GET /api/tremor",
        f"{API_URL}/api/tremor",
        expected_keys=['detected', 'frequency_hz', 'confidence']
    )
    
    print()
    results['roi'] = test_endpoint(
        "GET /api/roi",
        f"{API_URL}/api/roi"
    )
    
    print()
    results['frequency'] = test_endpoint(
        "GET /api/frequency",
        f"{API_URL}/api/frequency",
        expected_keys=['frequencies', 'amplitudes']
    )
    
    # Test WebSocket
    print(f"\n{Fore.YELLOW}Testing WebSocket:{Style.RESET_ALL}\n")
    results['websocket'] = test_websocket()
    
    # Summary
    print(f"\n{Fore.YELLOW}{'='*60}")
    print(f"Test Summary")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = f"{Fore.GREEN}PASS" if result else f"{Fore.RED}FAIL"
        print(f"  {name:20s} {status}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Total: {passed}/{total} tests passed{Style.RESET_ALL}\n")
    
    if passed == total:
        print(f"{Fore.GREEN}🎉 All tests passed! API is fully functional.{Style.RESET_ALL}\n")
        return 0
    else:
        print(f"{Fore.RED}⚠️  Some tests failed. Check the errors above.{Style.RESET_ALL}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
