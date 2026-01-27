#!/usr/bin/env python3
"""
Token Monitor - Checks session token usage and alerts when approaching limits.
"""

import subprocess
import json
import sys
from datetime import datetime
import os

# Configuration
WARNING_THRESHOLD = 150000  # 150K tokens as mentioned in HEARTBEAT.md
CRITICAL_PERCENTAGE = 80    # 80% of context window
LOG_FILE = "/tmp/token_monitor.log"
REPORT_FILE = "/tmp/token_monitor_report.txt"

def log(message):
    """Log message with timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    with open(LOG_FILE, 'a') as f:
        f.write(log_line + '\n')

def get_sessions():
    """Get session data from clawdbot."""
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
            log(f"ERROR: Failed to get session data: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        log("ERROR: Timeout running clawdbot sessions")
        return None
    except Exception as e:
        log(f"ERROR: Exception running clawdbot sessions: {e}")
        return None

def analyze_sessions(session_data):
    """Analyze token usage and generate alerts."""
    if not session_data or "sessions" not in session_data:
        return [], [], []
    
    sessions = session_data["sessions"]
    critical_alerts = []
    warnings = []
    compact_recommendations = []
    
    for session in sessions:
        key = session.get("key", "")
        model = session.get("model", "")
        total_tokens = session.get("totalTokens")
        context_tokens = session.get("contextTokens")
        
        # Skip if no token data
        if total_tokens is None or context_tokens is None:
            continue
        
        # Calculate percentage
        percentage = (total_tokens / context_tokens) * 100 if context_tokens > 0 else 0
        
        # Check thresholds
        if percentage >= CRITICAL_PERCENTAGE:
            critical_alerts.append({
                "key": key,
                "model": model,
                "current": total_tokens,
                "limit": context_tokens,
                "percentage": round(percentage, 1)
            })
        elif total_tokens >= WARNING_THRESHOLD:
            warnings.append({
                "key": key,
                "model": model,
                "current": total_tokens,
                "limit": context_tokens,
                "percentage": round(percentage, 1)
            })
        
        # Compact recommendations (60% or higher)
        if percentage >= 60:
            compact_recommendations.append({
                "key": key,
                "percentage": round(percentage, 1)
            })
    
    return critical_alerts, warnings, compact_recommendations

def generate_report(critical_alerts, warnings, compact_recommendations, total_sessions, sessions_with_data):
    """Generate a formatted report."""
    report = f"Token Monitor Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += "=" * 50 + "\n"
    report += f"Total sessions checked: {total_sessions}\n"
    report += f"Sessions with token data: {sessions_with_data}\n\n"
    
    if critical_alerts:
        report += f"❌ CRITICAL ALERTS ({len(critical_alerts)}):\n"
        for alert in critical_alerts:
            report += f"  • {alert['key'][:50]}...\n"
            report += f"    Model: {alert['model']}, Tokens: {alert['current']:,}/{alert['limit']:,} ({alert['percentage']}%)\n"
            report += f"    ACTION: Run /compact command immediately!\n"
    
    if warnings:
        report += f"⚠️  WARNINGS ({len(warnings)}):\n"
        for alert in warnings:
            report += f"  • {alert['key'][:50]}...\n"
            report += f"    Model: {alert['model']}, Tokens: {alert['current']:,}/{alert['limit']:,} ({alert['percentage']}%)\n"
            report += f"    Note: Approaching {WARNING_THRESHOLD:,} token threshold\n"
    
    if not critical_alerts and not warnings:
        report += "✅ All sessions within safe limits\n"
    
    if compact_recommendations:
        report += f"\n📋 COMPACT RECOMMENDATIONS ({len(compact_recommendations)}):\n"
        for rec in compact_recommendations:
            report += f"  • Consider /compact for {rec['key'][:50]}... ({rec['percentage']}% full)\n"
    
    return report

def main():
    """Main function."""
    log("Starting token monitor...")
    
    # Get session data
    session_data = get_sessions()
    if not session_data:
        log("Failed to get session data")
        sys.exit(1)
    
    # Analyze sessions
    critical_alerts, warnings, compact_recommendations = analyze_sessions(session_data)
    
    # Count sessions with token data
    total_sessions = len(session_data.get("sessions", []))
    sessions_with_data = len([s for s in session_data.get("sessions", []) if s.get("totalTokens") is not None])
    
    # Generate report
    report = generate_report(critical_alerts, warnings, compact_recommendations, total_sessions, sessions_with_data)
    
    # Save report
    with open(REPORT_FILE, 'w') as f:
        f.write(report)
    
    # Print summary
    if critical_alerts:
        log(f"❌ Found {len(critical_alerts)} session(s) at critical token levels")
        for alert in critical_alerts:
            log(f"  CRITICAL: {alert['key'][:40]}... at {alert['percentage']}% ({alert['current']:,}/{alert['limit']:,} tokens)")
    
    if warnings:
        log(f"⚠️  Found {len(warnings)} session(s) approaching token limits")
        for alert in warnings:
            log(f"  WARNING: {alert['key'][:40]}... at {alert['current']:,} tokens (threshold: {WARNING_THRESHOLD:,})")
    
    if not critical_alerts and not warnings:
        log("✅ All sessions within safe limits")
    
    # Print full report
    print("\n" + report)
    log(f"Report saved to {REPORT_FILE}")
    log("Token monitor finished")
    
    # Exit with error code if critical alerts found
    if critical_alerts:
        sys.exit(2)
    elif warnings:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()