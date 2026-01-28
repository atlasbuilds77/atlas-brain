#!/usr/bin/env bash
# Brain Monitor - Instrumentation for cognitive events
# Logs cognitive events to be visualized in Jarvis mode

set -euo pipefail

BRAIN_LOG="logs/brain-events.jsonl"
mkdir -p "$(dirname "$BRAIN_LOG")"

# Function to log cognitive events
log_event() {
    local event_type="$1"
    local message="$2"
    local intensity="${3:-0.5}"
    local metadata_json="${4:-{}}"
    
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Build JSON directly to avoid jq issues
    cat >> "$BRAIN_LOG" << EOF
{"timestamp":"$timestamp","event_type":"$event_type","message":"$message","intensity":$intensity,"metadata":$metadata_json}
EOF
}

# Export function for use in other scripts
export -f log_event

# Usage examples (for documentation):
# log_event "pattern_match" "Pattern 'FOMO' detected" 0.8 '{"pattern_id": "fomo_001", "valence": "negative"}'
# log_event "mode_switch" "DMN MODE: Creative exploration" 1.0 '{"old_mode": "ECN", "new_mode": "DMN"}'
# log_event "emotion" "Anxiety response triggered" 0.7 '{"marker": "loss_aversion"}'
# log_event "bias_detection" "Confirmation bias detected" 0.6 '{"context": "trade_decision"}'
# log_event "metacognition" "Verifying source credibility" 0.8 '{"check_type": "source_verification"}'
# log_event "memory" "Retrieved pattern: successful_trade" 0.5 '{"memory_type": "episodic", "date": "2024-12-15"}'
# log_event "decision" "Execute protective stop-loss" 0.9 '{"decision_type": "risk_management"}'

# Command-line interface
if [ $# -gt 0 ]; then
    case "$1" in
        log)
            shift
            log_event "$@"
            ;;
        test)
            # Generate test events
            log_event "pattern_match" "Test: Pattern recognition active" 0.7 '{"test": true}'
            log_event "emotion" "Test: Emotional processing" 0.5 '{"test": true}'
            log_event "mode_switch" "Test: Mode switch ECN→DMN" 0.9 '{"test": true}'
            echo "✓ Test events logged to $BRAIN_LOG"
            ;;
        watch)
            # Watch events in real-time
            echo "Watching brain events (Ctrl+C to stop)..."
            tail -f "$BRAIN_LOG" | jq -r '"\(.timestamp) [\(.event_type)] \(.message)"'
            ;;
        clear)
            # Clear event log
            > "$BRAIN_LOG"
            echo "✓ Brain event log cleared"
            ;;
        *)
            echo "Usage: $0 {log|test|watch|clear} [args...]"
            echo ""
            echo "Commands:"
            echo "  log EVENT_TYPE MESSAGE [INTENSITY] [METADATA]  - Log a cognitive event"
            echo "  test                                            - Generate test events"
            echo "  watch                                           - Watch events in real-time"
            echo "  clear                                           - Clear event log"
            exit 1
            ;;
    esac
else
    echo "Brain Monitor - Instrumentation for Atlas cognitive events"
    echo "Usage: $0 {log|test|watch|clear} [args...]"
    echo "Run '$0 help' for more information"
fi
