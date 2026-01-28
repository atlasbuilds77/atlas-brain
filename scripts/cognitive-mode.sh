#!/bin/bash
# cognitive-mode.sh - DMN/ECN Mode Management
# Usage: ./cognitive-mode.sh [get|set|validate|log]

MODE_FILE="memory/state/cognitive-mode.json"
cd "$(dirname "$0")/.."

get_mode() {
    if [[ -f "$MODE_FILE" ]]; then
        local mode=$(jq -r '.current_mode' "$MODE_FILE")
        local context=$(jq -r '.task_context' "$MODE_FILE")
        local start=$(jq -r '.mode_start_time' "$MODE_FILE")
        echo "Current Mode: $mode"
        echo "Context: $context"
        echo "Started: $start"
        
        # Show reminder
        local reminder=$(jq -r ".mode_definitions.$mode.reminder // empty" "$MODE_FILE")
        [[ -n "$reminder" ]] && echo -e "\n$reminder"
    else
        echo "Mode file not found"
        exit 1
    fi
}

set_mode() {
    local new_mode="${1:-ECN}"
    local context="${2:-default}"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Validate mode
    if [[ "$new_mode" != "DMN" && "$new_mode" != "ECN" && "$new_mode" != "MIXED" ]]; then
        echo "Invalid mode: $new_mode (use DMN, ECN, or MIXED)"
        exit 1
    fi
    
    # Update mode file
    local tmp=$(mktemp)
    jq --arg mode "$new_mode" \
       --arg ctx "$context" \
       --arg ts "$timestamp" \
       '.current_mode = $mode | .task_context = $ctx | .mode_start_time = $ts | .last_updated = $ts | .session_history += [{mode: $mode, context: $ctx, time: $ts}]' \
       "$MODE_FILE" > "$tmp" && mv "$tmp" "$MODE_FILE"
    
    echo "✅ Mode set to: $new_mode"
    echo "Context: $context"
    
    # Show mode rules
    echo -e "\n--- MODE RULES ---"
    jq -r ".mode_definitions.$new_mode.rules[]" "$MODE_FILE" | while read rule; do
        echo "• $rule"
    done
    
    # Show reminder
    local reminder=$(jq -r ".mode_definitions.$new_mode.reminder // empty" "$MODE_FILE")
    [[ -n "$reminder" ]] && echo -e "\n$reminder"
}

validate_mode() {
    local current=$(jq -r '.current_mode' "$MODE_FILE")
    local input="${1:-}"
    
    echo "Validating input against $current mode..."
    
    # Check for mode violations
    local violations=()
    
    if [[ "$current" == "DMN" ]]; then
        # Check for evaluation language in DMN mode
        if echo "$input" | grep -qiE "(won't work|bad idea|not feasible|impossible|too hard|can't)"; then
            violations+=("Evaluative language detected in DMN mode")
        fi
        if echo "$input" | grep -qiE "(rank|best|worst|choose|decide)"; then
            violations+=("Decision/ranking language in DMN mode")
        fi
    elif [[ "$current" == "ECN" ]]; then
        # Check for unfocused generation in ECN mode
        if echo "$input" | grep -qiE "(what if we|imagine|maybe we could|random idea)"; then
            violations+=("Unfocused ideation detected in ECN mode")
        fi
    fi
    
    if [[ ${#violations[@]} -gt 0 ]]; then
        echo "⚠️ MODE VIOLATIONS DETECTED:"
        for v in "${violations[@]}"; do
            echo "  • $v"
        done
        echo ""
        echo "Consider switching modes or separating creative/analytical phases."
        return 1
    else
        echo "✅ No mode violations detected"
        return 0
    fi
}

log_switch() {
    local from_mode="$1"
    local to_mode="$2"
    local reason="$3"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    echo "{\"type\":\"mode_switch\",\"from\":\"$from_mode\",\"to\":\"$to_mode\",\"reason\":\"$reason\",\"timestamp\":\"$timestamp\"}" >> memory/state/mode-switches.jsonl
    echo "Logged mode switch: $from_mode → $to_mode"
}

case "$1" in
    get)
        get_mode
        ;;
    set)
        set_mode "$2" "$3"
        ;;
    validate)
        validate_mode "$2"
        ;;
    log)
        log_switch "$2" "$3" "$4"
        ;;
    *)
        echo "Usage: $0 [get|set|validate|log]"
        echo "  get              - Show current mode"
        echo "  set MODE [CTX]   - Set mode (DMN/ECN/MIXED)"
        echo "  validate TEXT    - Check text for mode violations"
        echo "  log FROM TO WHY  - Log a mode switch"
        ;;
esac
