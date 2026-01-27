#!/bin/bash
# Token Monitor Script
# Checks token usage across all sessions and alerts when approaching limits

set -e

# Configuration
WARNING_THRESHOLD=150000  # 150K tokens as mentioned in HEARTBEAT.md
CRITICAL_PERCENTAGE=80    # 80% of context window
LOG_FILE="/tmp/token_monitor.log"
REPORT_FILE="/tmp/token_monitor_report.txt"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_sessions() {
    log "Checking token usage across all sessions..."
    
    # Get session data in JSON format
    if ! SESSION_JSON=$(clawdbot sessions --json 2>/dev/null); then
        log "ERROR: Failed to get session data from clawdbot"
        return 1
    fi
    
    # Save raw JSON for debugging
    echo "$SESSION_JSON" > "/tmp/sessions_raw.json"
    
    # Use Python for proper JSON parsing
    python3 << EOF
import json
import sys
from datetime import datetime

try:
    data = json.loads('''$SESSION_JSON''')
    sessions = data.get('sessions', [])
    
    critical_alerts = []
    warnings = []
    compact_recommendations = []
    
    for session in sessions:
        key = session.get('key', '')
        model = session.get('model', '')
        total_tokens = session.get('totalTokens')
        context_tokens = session.get('contextTokens')
        
        # Skip if no token data
        if total_tokens is None or context_tokens is None:
            continue
        
        # Calculate percentage
        percentage = (total_tokens / context_tokens) * 100 if context_tokens > 0 else 0
        
        # Check thresholds
        if percentage >= $CRITICAL_PERCENTAGE:
            critical_alerts.append({
                'key': key,
                'model': model,
                'current': total_tokens,
                'limit': context_tokens,
                'percentage': round(percentage, 1)
            })
        elif total_tokens >= $WARNING_THRESHOLD:
            warnings.append({
                'key': key,
                'model': model,
                'current': total_tokens,
                'limit': context_tokens,
                'percentage': round(percentage, 1)
            })
        
        # Compact recommendations (60% or higher)
        if percentage >= 60:
            compact_recommendations.append({
                'key': key,
                'percentage': round(percentage, 1)
            })
    
    # Generate report
    report = f"Token Monitor Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n"
    report += "=" * 50 + "\\n"
    report += f"Total sessions checked: {len(sessions)}\\n"
    report += f"Sessions with token data: {len([s for s in sessions if s.get('totalTokens')])}\\n\\n"
    
    if critical_alerts:
        report += f"❌ CRITICAL ALERTS ({len(critical_alerts)}):\\n"
        for alert in critical_alerts:
            report += f"  • {alert['key'][:50]}...\\n"
            report += f"    Model: {alert['model']}, Tokens: {alert['current']:,}/{alert['limit']:,} ({alert['percentage']}%)\\n"
            report += f"    ACTION: Run /compact command immediately!\\n"
    
    if warnings:
        report += f"⚠️  WARNINGS ({len(warnings)}):\\n"
        for alert in warnings:
            report += f"  • {alert['key'][:50]}...\\n"
            report += f"    Model: {alert['model']}, Tokens: {alert['current']:,}/{alert['limit']:,} ({alert['percentage']}%)\\n"
            report += f"    Note: Approaching {${WARNING_THRESHOLD}:,} token threshold\\n"
    
    if not critical_alerts and not warnings:
        report += "✅ All sessions within safe limits\\n"
    
    if compact_recommendations:
        report += f"\\n📋 COMPACT RECOMMENDATIONS ({len(compact_recommendations)}):\\n"
        for rec in compact_recommendations:
            report += f"  • Consider /compact for {rec['key'][:50]}... ({rec['percentage']}% full)\\n"
    
    # Write report
    with open('$REPORT_FILE', 'w') as f:
        f.write(report)
    
    # Print summary for shell script
    print(f"CRITICAL:{len(critical_alerts)}:WARNINGS:{len(warnings)}:COMPACT:{len(compact_recommendations)}")
    
    # Print alerts to stderr for immediate visibility
    if critical_alerts:
        for alert in critical_alerts:
            print(f"CRITICAL: {alert['key'][:40]}... at {alert['percentage']}% ({alert['current']:,}/{alert['limit']:,} tokens)", file=sys.stderr)
    if warnings:
        for alert in warnings:
            print(f"WARNING: {alert['key'][:40]}... at {alert['current']:,} tokens (threshold: ${WARNING_THRESHOLD:,})", file=sys.stderr)
            
except Exception as e:
    print(f"ERROR:PARSING:{str(e)}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
EOF
}

main() {
    log "Starting token monitor..."
    
    # Check if clawdbot is available
    if ! command -v clawdbot &> /dev/null; then
        log "ERROR: clawdbot command not found"
        return 1
    fi
    
    # Run the check
    check_result=$(check_sessions 2>&1)
    
    # Parse the result
    if [[ "$check_result" == ERROR:* ]]; then
        log "Token check failed: $check_result"
        return 1
    fi
    
    # Extract counts from Python output
    if [[ "$check_result" == CRITICAL:* ]]; then
        IFS=':' read -r _ critical_count _ warning_count _ compact_count <<< "$check_result"
        
        if [ "$critical_count" -gt 0 ]; then
            log "❌ Found $critical_count session(s) at critical token levels"
        fi
        
        if [ "$warning_count" -gt 0 ]; then
            log "⚠️  Found $warning_count session(s) approaching token limits"
        fi
        
        log "Check complete: $critical_count critical, $warning_count warnings, $compact_count compact recommendations"
        
        # Show report
        if [ -f "$REPORT_FILE" ]; then
            log "Report saved to $REPORT_FILE"
            echo ""
            cat "$REPORT_FILE"
        fi
    else
        log "No token data found or all sessions within limits"
    fi
    
    log "Token monitor finished"
}

# Run main function
main "$@"