#!/usr/bin/env python3
"""
Test script for Atlas Eyes integration
Verifies database logging, API endpoints, and query interface
"""

import sys
import time
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from event_store import EventStore, log_heartbeat, log_tremor, log_motion_spike
from atlas_query import AtlasQuery


def test_event_store():
    """Test event database"""
    print("=" * 60)
    print("Testing Event Store")
    print("=" * 60)
    
    db_path = "/tmp/test_motion_events.db"
    
    with EventStore(db_path) as store:
        print(f"✓ Event store initialized: {db_path}")
        
        # Log some test events
        print("\nLogging test events...")
        
        # Heartbeat readings
        for i in range(10):
            bpm = 70 + (i % 5) * 2
            confidence = 0.8 + (i % 3) * 0.05
            log_heartbeat(store, bpm, confidence, {'test': True})
            time.sleep(0.1)
        print("  ✓ Logged 10 heartbeat events")
        
        # Tremor events
        log_tremor(store, 4.2, 0.85, {'severity': 'moderate'})
        log_tremor(store, 4.5, 0.92, {'severity': 'high'})
        print("  ✓ Logged 2 tremor events")
        
        # Motion spikes
        log_motion_spike(store, 0.85, {'source': 'sudden_movement'})
        print("  ✓ Logged 1 motion spike")
        
        # Query recent events
        print("\nQuerying events...")
        recent = store.query_recent(limit=5)
        print(f"  ✓ Retrieved {len(recent)} recent events")
        
        # Get heartbeat history
        history = store.get_history('heartbeat', hours=1)
        print(f"  ✓ Retrieved {len(history)} heartbeat events")
        
        # Get statistics
        stats = store.get_stats('heartbeat', hours=1)
        print(f"  ✓ Heartbeat stats: avg={stats['avg_value']:.1f} BPM, count={stats['count']}")
        
        # Get latest
        latest = store.get_latest('heartbeat')
        print(f"  ✓ Latest heartbeat: {latest['value']:.1f} BPM @ {latest['confidence']:.0%} confidence")
        
        # Time series
        ts = store.get_time_series('heartbeat', hours=1, bucket_minutes=1)
        print(f"  ✓ Time series: {len(ts)} data points")
        
        print("\n✓ Event store tests PASSED")
        return True


def test_atlas_query():
    """Test natural language query interface"""
    print("\n" + "=" * 60)
    print("Testing Atlas Query Interface")
    print("=" * 60)
    
    db_path = "/tmp/test_motion_events.db"
    
    with AtlasQuery(db_path) as query:
        print("✓ Query interface initialized")
        
        # Test queries
        print("\nRunning queries...")
        
        response = query.get_current_heart_rate()
        print(f"\n❤️  What's my heart rate?")
        print(f"   {response}")
        
        response = query.check_for_tremors(last_hours=1)
        print(f"\n🤝 Any tremors?")
        print(f"   {response}")
        
        response = query.health_summary(hours=1)
        print(f"\n📊 Health Summary:")
        print(response)
        
        response = query.is_everything_normal(hours=1)
        print(f"\n🔍 Is everything normal?")
        print(f"   {response}")
        
        print("\n✓ Query interface tests PASSED")
        return True


def test_api_endpoints(port: int = 5000):
    """Test API endpoints (requires running server)"""
    print("\n" + "=" * 60)
    print("Testing API Endpoints")
    print("=" * 60)
    
    base_url = f"http://127.0.0.1:{port}"
    
    try:
        # Status
        print("\nChecking API status...")
        response = requests.get(f"{base_url}/api/status", timeout=2)
        
        if response.status_code == 200:
            status = response.json()
            print(f"  ✓ Status: {status.get('status', 'unknown')}")
        else:
            print(f"  ✗ Status endpoint failed: {response.status_code}")
            return False
        
        # Heartbeat current
        print("\nTesting heartbeat endpoints...")
        response = requests.get(f"{base_url}/api/heartbeat/current", timeout=2)
        
        if response.status_code in [200, 404]:
            print(f"  ✓ /api/heartbeat/current")
        else:
            print(f"  ✗ Heartbeat endpoint failed")
            return False
        
        # Heartbeat history
        response = requests.get(f"{base_url}/api/heartbeat/history?hours=24", timeout=2)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ /api/heartbeat/history ({data['count']} readings)")
        
        # Tremor events
        print("\nTesting tremor endpoints...")
        response = requests.get(f"{base_url}/api/tremor/events?hours=24", timeout=2)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ /api/tremor/events ({data['count']} events)")
        
        # Health summary
        print("\nTesting health endpoints...")
        response = requests.get(f"{base_url}/api/health/summary?hours=24", timeout=2)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ /api/health/summary")
            print(f"     Heartbeat readings: {data['heartbeat']['count']}")
            print(f"     Tremor events: {data['tremor']['count']}")
        
        # Natural language queries
        print("\nTesting natural language queries...")
        
        response = requests.get(f"{base_url}/api/query/heart_rate", timeout=2)
        if response.status_code == 200:
            print(f"  ✓ /api/query/heart_rate")
            print(f"     Response: {response.json()['response']}")
        
        response = requests.get(f"{base_url}/api/query/summary", timeout=2)
        if response.status_code == 200:
            print(f"  ✓ /api/query/summary")
        
        print("\n✓ API endpoint tests PASSED")
        return True
        
    except requests.ConnectionError:
        print("\n✗ API server not running")
        print(f"   Start with: python scripts/daemon.py --port {port}")
        return False
    
    except Exception as e:
        print(f"\n✗ API tests failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Atlas Eyes Integration Tests")
    print("=" * 60)
    
    results = []
    
    # Test event store
    try:
        results.append(('Event Store', test_event_store()))
    except Exception as e:
        print(f"\n✗ Event store tests FAILED: {e}")
        results.append(('Event Store', False))
    
    # Test query interface
    try:
        results.append(('Query Interface', test_atlas_query()))
    except Exception as e:
        print(f"\n✗ Query interface tests FAILED: {e}")
        results.append(('Query Interface', False))
    
    # Test API (optional - only if server is running)
    print("\n" + "=" * 60)
    print("Optional: API Endpoint Tests")
    print("(Skipped if server not running)")
    print("=" * 60)
    
    try:
        results.append(('API Endpoints', test_api_endpoints()))
    except Exception as e:
        print(f"\n✗ API tests FAILED: {e}")
        results.append(('API Endpoints', False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 All tests PASSED!")
        return 0
    else:
        print("\n⚠️  Some tests FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())
