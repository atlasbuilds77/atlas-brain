#!/bin/bash
# Token Monitor Script
# Checks token usage across all sessions and alerts when approaching limits
# Can be run via cron or manually

set -e

# Configuration
WARNING_THRESHOLD=150000  # 150K tokens as mentioned in HEARTBEAT.md
CRITICAL_PERCENTAGE=80    # 80% of context window
LOG_FILE="/tmp/token_monitor.log"
REPORT_FILE="/tmp/token_monitor_report.txt"
ALERT_CHANNEL="imessage"  # Channel to send alerts to
ALERT_TARGET="+14245157194"  # Orion's number

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

alert() {
    local message="$1"
    local level="$2"
    
    log "[$level] $message"
    
    # Send alert via iMessage if critical
    if [ "$level" = "CRITICAL" ]; then
        log "Sending alert to $ALERT_TARGET"
        # Uncomment to actually send alerts
        # clawdbot message send --channel "$ALERT_CHANNEL" --target "$ALERT_TARGET" --message "$message" || true
    fi
}

check_sessions() {
    log "Checking token usage across all sessions..."
    
    # Get session data in JSON format
    if ! SESSION_DATA=$(clawdbot sessions --json 2>/dev/null); then
        alert "Failed to get session data from clawdbot" "ERROR"
        return 1
    fi
    
    # Parse the JSON (simplified parsing - in production would use jq)
    echo "$SESSION_DATA" > "/tmp/sessions_raw.json"
    
    # Use Python for proper JSON parsing
    python3 << EOF
import json
import re
import sys
from datetime import datetime

try:
    with open('/tmp/sessions_raw.json', 'r') as f:
        data = json.load(f)
    
    sessions = data.get('sessions', [])
    
    critical_alerts = []
    warnings = []
    compact_recommendations = []
    
    for session in sessions:
        key = session.get('key', '')
        model = session.get('model', '')
        tokens_str = session.get('tokens', '')
        age = session.get('age', '')
        
        if tokens_str == '-' or not tokens_str:
            continue
            
        # Parse token string like "73k/1000k (7%)" or "44k/64k (68%)"
        match = re.search(r'(\d+(?:\.\d+)?k?)/(\d+(?:\.\d+)?k?)\s*\((\d+)%\)', tokens_str)
        if not match:
            continue
            
        current_str = match.group(1).replace('k', '000').replace('.', '')
        limit_str = match.group(2).replace('k', '000').replace('.', '')
        percentage = int(match.group(3))
        
        try:
            current = int(current_str)
            limit = int(limit_str)
        except:
            continue
        
        # Check thresholds
        if percentage >= $CRITICAL_PERCENTAGE:
            critical_alerts.append({
                'key': key,
                'model': model,
                'current': current,
                'limit': limit,
                'percentage': percentage,
                'age': age
            })
        elif current >= $WARNING_THRESHOLD:
            warnings.append({
                'key': key,
                'model': model,
                'current': current,
                'limit': limit,
                'percentage': percentage,
                'age': age
            })
        
        # Compact recommendations
        if percentage >= 60:
            compact_recommendations.append({
                'key': key,
                'percentage': percentage
            })
    
    # Generate report
    report = f"Token Monitor Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n"
    report += "=" * 50 + "\\n"
    
    if critical_alerts:
        report += f"CRITICAL ALERTS ({len(critical_alerts)}):\\n"
        for alert in critical_alerts:
            report += f"  • {alert['key'][:40]}...\\n"
            report += f"    Model: {alert['model']}, Tokens: {alert['current']:,}/{alert['limit']:,} ({alert['percentage']}%)\\n"
            report += f"    Age: {alert['age']}\\n"
    
    if warnings:
        report += f"WARNINGS ({len(warnings)}):\\n"
        for alert in warnings:
            report += f"  • {alert['key'][:40]}...\\n"
            report += f"    Model: {alert['model']}, Tokens: {alert['current']:,}/{alert['limit']:,} ({alert['percentage']}%)\\n"
            report += f"    Age: {alert['age']}\\n"
    
    if not critical_alerts and not warnings:
        report += "All sessions within safe limits\\n"
    
    if compact_recommendations:
        report += f"\\nCOMPACT RECOMMENDATIONS ({len(compact_recommendations)}):\\n"
        for rec in compact_recommendations:
            report += f"  • Consider /compact for {rec['key'][:40]}... ({rec['percentage']}% full)\\n"
    
    # Write report
    with open('$REPORT_FILE', 'w') as f:
        f.write(report)
    
    # Print summary for shell script
    print(f"CRITICAL:{len(critical_alerts)}:WARNINGS:{len(warnings)}:COMPACT:{len(compact_recommendations)}")
    
    # Print alerts to stderr for immediate visibility
    if critical_alerts:
        for alert in critical_alerts:
            print(f"CRITICAL: {alert['key'][:30]}... at {alert['percentage']}% ({alert['current']:,}/{alert['limit']:,} tokens)", file=sys.stderr)
    if warnings:
        for alert in warnings:
            print(f"WARNING: {alert['key'][:30]}... at {alert['current']:,} tokens (threshold: {$WARNING_THRESHOLD:,})", file=sys.stderr)
            
except Exception as e:
    print(f"ERROR:PARSING:{str(e)}", file=sys.stderr)
    sys.exit(1)
EOF
}

main() {
    log "Starting token monitor..."
    
    # Check if clawdbot is available
    if ! command -v clawdbot &> /dev/null; then
        alert "clawdbot command not found" "ERROR"
        return 1
    fi
    
    # Run the check
    check_result=$(check_sessions 2>&1)
    
    # Parse the result
    if [[ "$check_result" == ERROR:* ]]; then
        alert "Token check failed: $check_result" "ERROR"
        return 1
    fi
    
    # Extract counts from Python output
    if [[ "$check_result" == CRITICAL:* ]]; then
        IFS=':' read -r _ critical_count _ warning_count _ compact_count <<< "$check_result"
        
        if [ "$critical_count" -gt 0 ]; then
            alert "Found $critical_count session(s) at critical token levels" "CRITICAL"
            # Read first line of report for alert message
            if [ -f "$REPORT_FILE" ]; then
                first_alert=$(grep -A2 "CRITICAL ALERTS" "$REPORT_FILE" | head -3 | tr '\n' ' ')
                alert "Critical token alert: $first_alert" "CRITICAL"
            fi
        fi
        
        if [ "$warning_count" -gt 0 ]; then
            alert "Found $warning_count session(s) approaching token limits" "WARNING"
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