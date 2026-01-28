#!/usr/bin/env python3
"""
Example: How Atlas can query health data from Atlas Eyes

This script demonstrates the simplest way for Atlas to access health monitoring data.
Can be called directly or imported as a module.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from atlas_query import (
    get_current_heart_rate,
    check_for_tremors,
    health_summary,
    is_everything_normal,
    AtlasQuery
)


def demo_quick_functions():
    """Demo: Using quick convenience functions (simplest approach)"""
    print("=" * 60)
    print("Atlas Eyes - Quick Query Examples")
    print("=" * 60)
    print()
    
    # These functions handle everything internally - just call them!
    
    print("❤️  What's my heart rate?")
    print(f"   {get_current_heart_rate()}")
    print()
    
    print("🤝 Any tremors in the last 24 hours?")
    print(f"   {check_for_tremors(last_hours=24)}")
    print()
    
    print("🔍 Is everything normal?")
    print(f"   {is_everything_normal(hours=1)}")
    print()
    
    print("📊 Health Summary (last 24 hours)")
    print(health_summary(hours=24))


def demo_query_interface():
    """Demo: Using the query interface (more control)"""
    print("\n" + "=" * 60)
    print("Atlas Eyes - Advanced Query Examples")
    print("=" * 60)
    print()
    
    # Use context manager for automatic cleanup
    with AtlasQuery() as query:
        
        # Current status with custom age threshold
        print("Current heart rate (max 30s old):")
        print(f"  {query.get_current_heart_rate(max_age_seconds=30)}")
        print()
        
        # Tremor check with custom confidence
        print("High-confidence tremors (last 12 hours):")
        # Note: min_confidence is set in check_for_tremors (default 0.7)
        print(f"  {query.check_for_tremors(last_hours=12)}")
        print()
        
        # Detailed heart rate history
        print("Detailed heart rate history:")
        print(query.get_heart_rate_history(hours=1, format='detailed'))
        print()
        
        # Get time series data for plotting/analysis
        print("Time series data (for graphs):")
        ts_data = query.get_time_series_data('heartbeat', hours=1, bucket_minutes=5)
        print(f"  {len(ts_data)} data points")
        if ts_data:
            latest = ts_data[-1]
            print(f"  Latest 5-min bucket: {latest['avg_value']:.1f} BPM avg, {latest['count']} readings")


def demo_direct_database_access():
    """Demo: Direct database access (maximum flexibility)"""
    print("\n" + "=" * 60)
    print("Atlas Eyes - Direct Database Access")
    print("=" * 60)
    print()
    
    from event_store import EventStore
    
    with EventStore() as store:
        
        # Count events
        heartbeat_count = store.count_events('heartbeat', hours=24)
        tremor_count = store.count_events('tremor', hours=24)
        
        print(f"Database stats (last 24 hours):")
        print(f"  Heartbeat readings: {heartbeat_count}")
        print(f"  Tremor detections: {tremor_count}")
        print()
        
        # Get latest event
        latest_hr = store.get_latest('heartbeat', min_confidence=0.5)
        if latest_hr:
            print(f"Latest heartbeat reading:")
            print(f"  {latest_hr['value']:.1f} BPM")
            print(f"  Confidence: {latest_hr['confidence']:.0%}")
            print(f"  Timestamp: {latest_hr['timestamp']}")
            print()
        
        # Get statistics
        stats = store.get_stats('heartbeat', hours=24)
        print(f"24-hour heartbeat statistics:")
        print(f"  Average: {stats['avg_value']:.1f} BPM")
        print(f"  Range: {stats['min_value']:.1f} - {stats['max_value']:.1f} BPM")
        print(f"  Readings: {stats['count']}")
        print(f"  Avg confidence: {stats['avg_confidence']:.0%}")
        print()
        
        # Query recent events
        recent = store.query_recent('heartbeat', limit=5, min_confidence=0.6)
        print(f"Last 5 high-confidence heartbeat readings:")
        for i, event in enumerate(recent, 1):
            print(f"  {i}. {event['value']:.1f} BPM @ {event['confidence']:.0%} confidence")


def atlas_voice_command(command: str) -> str:
    """
    Process a voice command from Atlas
    
    Args:
        command: Natural language command
    
    Returns:
        Human-readable response
    """
    command_lower = command.lower()
    
    # Heart rate queries
    if any(word in command_lower for word in ['heart rate', 'bpm', 'pulse', 'heartbeat']):
        return get_current_heart_rate()
    
    # Tremor queries
    elif any(word in command_lower for word in ['tremor', 'shaking', 'shake']):
        return check_for_tremors(last_hours=24)
    
    # Health summary
    elif any(word in command_lower for word in ['summary', 'how am i', 'health status', 'report']):
        return health_summary(hours=24)
    
    # Quick health check
    elif any(word in command_lower for word in ['normal', 'okay', 'ok', 'fine']):
        return is_everything_normal(hours=1)
    
    # Unknown command
    else:
        return "I can tell you about your heart rate, tremors, and overall health status. What would you like to know?"


def main():
    """Run all examples"""
    
    # Quick functions demo
    demo_quick_functions()
    
    # Query interface demo
    demo_query_interface()
    
    # Direct database demo
    demo_direct_database_access()
    
    # Voice command examples
    print("\n" + "=" * 60)
    print("Atlas Eyes - Voice Command Examples")
    print("=" * 60)
    print()
    
    test_commands = [
        "What's my heart rate?",
        "Have there been any tremors?",
        "Am I okay?",
        "Give me a health summary"
    ]
    
    for command in test_commands:
        print(f"Atlas: '{command}'")
        response = atlas_voice_command(command)
        print(f"Eyes: {response}")
        print()


if __name__ == '__main__':
    main()
