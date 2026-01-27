#!/usr/bin/env python3
"""
Script to check token usage across all sessions and alert if approaching limits.
"""

import subprocess
import json
import re
from datetime import datetime
import os

def get_sessions():
    """Get session data from clawdbot sessions command."""
    try:
        result = subprocess.run(
            ["clawdbot", "sessions", "--json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error running clawdbot sessions: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print("Timeout running clawdbot sessions")
        return None
    except Exception as e:
        print(f"Exception running clawdbot sessions: {e}")
        return None

def parse_token_usage(session_data):
    """Parse token usage from session data."""
    if not session_data or "sessions" not in session_data:
        return []
    
    sessions = []
    for session in session_data["sessions"]:
        # Extract token info from the formatted string
        tokens_str = session.get("tokens", "")
        model = session.get("model", "")
        key = session.get("key", "")
        
        # Parse token string like "73k/1000k (7%)" or "44k/64k (68%)"
        current = None
        limit = None
        percentage = None
        
        match = re.search(r'(\d+(?:\.\d+)?k?)/(\d+(?:\.\d+)?k?)\s*\((\d+)%\)', tokens_str)
        if match:
            current_str = match.group(1).replace('k', '000').replace('.', '')
            limit_str = match.group(2).replace('k', '000').replace('.', '')
            percentage = int(match.group(3))
            
            current = int(current_str)
            limit = int(limit_str)
        
        sessions.append({
            "key": key,
            "model": model,
            "tokens_str": tokens_str,
            "current_tokens": current,
            "limit_tokens": limit,
            "percentage": percentage,
            "age": session.get("age", ""),
            "kind": session.get("kind", "")
        })
    
    return sessions

def check_thresholds(sessions, warning_threshold=150000, critical_threshold=200000):
    """Check sessions against token thresholds."""
    warnings = []
    criticals = []
    
    for session in sessions:
        if session["current_tokens"] and session["limit_tokens"]:
            # Check if approaching limit (percentage-based)
            if session["percentage"] and session["percentage"] >= 80:
                criticals.append({
                    "session": session["key"],
                    "model": session["model"],
                    "current": session["current_tokens"],
                    "limit": session["limit_tokens"],
                    "percentage": session["percentage"],
                    "reason": f"High token usage: {session['percentage']}%"
                })
            # Check if approaching warning threshold (absolute)
            elif session["current_tokens"] >= warning_threshold:
                warnings.append({
                    "session": session["key"],
                    "model": session["model"],
                    "current": session["current_tokens"],
                    "limit": session["limit_tokens"],
                    "percentage": session["percentage"],
                    "reason": f"Approaching warning threshold: {session['current_tokens']} tokens"
                })
    
    return warnings, criticals

def main():
    print(f"=== Token Monitor Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    # Get session data
    session_data = get_sessions()
    if not session_data:
        print("Failed to get session data")
        return
    
    # Parse token usage
    sessions = parse_token_usage(session_data)
    
    print(f"\nFound {len(sessions)} sessions with token data:")
    for session in sessions:
        if session["tokens_str"] and session["tokens_str"] != "-":
            print(f"  {session['key'][:30]}...: {session['tokens_str']} ({session['model']})")
    
    # Check thresholds
    # Using 150K as warning threshold as mentioned in HEARTBEAT.md
    warnings, criticals = check_thresholds(sessions, warning_threshold=150000)
    
    # Report findings
    if criticals:
        print(f"\n❌ CRITICAL ALERTS ({len(criticals)}):")
        for alert in criticals:
            print(f"  • {alert['session'][:30]}...: {alert['reason']}")
            print(f"    Model: {alert['model']}, Tokens: {alert['current']}/{alert['limit']} ({alert['percentage']}%)")
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for alert in warnings:
            print(f"  • {alert['session'][:30]}...: {alert['reason']}")
            print(f"    Model: {alert['model']}, Tokens: {alert['current']}/{alert['limit']} ({alert['percentage']}%)")
    
    if not criticals and not warnings:
        print(f"\n✅ All sessions within safe limits")
    
    # Check for sessions that might need /compact
    print(f"\n=== Compact Recommendations ===")
    for session in sessions:
        if session["percentage"] and session["percentage"] >= 60:
            print(f"  • Consider /compact for {session['key'][:30]}... ({session['percentage']}% full)")
    
    # Save report to file
    report_file = "token_monitor_report.txt"
    with open(report_file, "w") as f:
        f.write(f"Token Monitor Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n")
        if criticals:
            f.write(f"CRITICAL ALERTS ({len(criticals)}):\n")
            for alert in criticals:
                f.write(f"  • {alert['session']}: {alert['reason']}\n")
        if warnings:
            f.write(f"WARNINGS ({len(warnings)}):\n")
            for alert in warnings:
                f.write(f"  • {alert['session']}: {alert['reason']}\n")
        if not criticals and not warnings:
            f.write("All sessions within safe limits\n")
    
    print(f"\nReport saved to {report_file}")

if __name__ == "__main__":
    main()