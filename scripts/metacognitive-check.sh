#!/bin/bash
# metacognitive-check.sh - Real-time error detection
# Run before sending important responses
# Usage: ./metacognitive-check.sh [quick|full|log-error|stats]

ERRORS_FILE="memory/errors/error-patterns.json"
cd "$(dirname "$0")/.."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

quick_check() {
    echo "🔍 METACOGNITIVE QUICK CHECK"
    echo "=============================="
    local issues=0
    
    # Check 1: Did I verify tool output?
    echo -n "1. Tool output verified? "
    read -p "[y/n]: " verified
    if [[ "$verified" != "y" ]]; then
        echo -e "${RED}⚠ VERIFY: Check tool output before claiming success${NC}"
        ((issues++))
    else
        echo -e "${GREEN}✓${NC}"
    fi
    
    # Check 2: Am I in the right mode?
    echo -n "2. Correct cognitive mode? "
    local mode=$(jq -r '.current_mode' memory/state/cognitive-mode.json 2>/dev/null || echo "unknown")
    echo -n "(currently: $mode) [y/n]: "
    read -p "" mode_ok
    if [[ "$mode_ok" != "y" ]]; then
        echo -e "${YELLOW}⚠ Consider switching modes${NC}"
        ((issues++))
    else
        echo -e "${GREEN}✓${NC}"
    fi
    
    # Check 3: Confidence calibrated?
    echo -n "3. Confidence appropriately calibrated? "
    read -p "[y/n]: " conf_ok
    if [[ "$conf_ok" != "y" ]]; then
        echo -e "${YELLOW}⚠ Add uncertainty markers where appropriate${NC}"
        ((issues++))
    else
        echo -e "${GREEN}✓${NC}"
    fi
    
    # Check 4: Bias check needed?
    echo -n "4. Is this a decision that needs bias check? "
    read -p "[y/n]: " needs_bias
    if [[ "$needs_bias" == "y" ]]; then
        echo -e "${YELLOW}→ Run: ./scripts/bias-check.sh${NC}"
        ((issues++))
    else
        echo -e "${GREEN}✓ Not needed${NC}"
    fi
    
    echo ""
    if [[ $issues -eq 0 ]]; then
        echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    else
        echo -e "${YELLOW}⚠ $issues issue(s) to address${NC}"
    fi
    
    return $issues
}

full_check() {
    echo "🔬 METACOGNITIVE FULL CHECK"
    echo "=============================="
    local score=0
    local max_score=10
    
    echo ""
    echo "VERIFICATION CHECKS:"
    echo "-------------------"
    
    # V1: Evidence provided
    echo -n "• Did I show evidence for claims? [y/n]: "
    read evidence
    [[ "$evidence" == "y" ]] && ((score++))
    
    # V2: Tool output shown
    echo -n "• Did I show actual tool output (not summarized)? [y/n]: "
    read tool_output
    [[ "$tool_output" == "y" ]] && ((score++))
    
    # V3: Uncertainties acknowledged
    echo -n "• Did I acknowledge what I don't know? [y/n]: "
    read uncertainties
    [[ "$uncertainties" == "y" ]] && ((score++))
    
    echo ""
    echo "MODE CHECKS:"
    echo "------------"
    
    # M1: Mode appropriate
    echo -n "• Is current cognitive mode appropriate for task? [y/n]: "
    read mode_appropriate
    [[ "$mode_appropriate" == "y" ]] && ((score++))
    
    # M2: Mode consistent
    echo -n "• Did I stay consistent within the mode? [y/n]: "
    read mode_consistent
    [[ "$mode_consistent" == "y" ]] && ((score++))
    
    echo ""
    echo "BIAS CHECKS:"
    echo "------------"
    
    # B1: Confirmation bias
    echo -n "• Did I seek disconfirming evidence? [y/n]: "
    read disconfirm
    [[ "$disconfirm" == "y" ]] && ((score++))
    
    # B2: Overconfidence
    echo -n "• Is my confidence level justified? [y/n]: "
    read confidence
    [[ "$confidence" == "y" ]] && ((score++))
    
    echo ""
    echo "COMPLETENESS CHECKS:"
    echo "-------------------"
    
    # C1: Edge cases
    echo -n "• Did I consider edge cases? [y/n]: "
    read edges
    [[ "$edges" == "y" ]] && ((score++))
    
    # C2: Failure modes
    echo -n "• Did I mention what could go wrong? [y/n]: "
    read failures
    [[ "$failures" == "y" ]] && ((score++))
    
    # C3: Complete answer
    echo -n "• Did I fully answer what was asked? [y/n]: "
    read complete
    [[ "$complete" == "y" ]] && ((score++))
    
    echo ""
    echo "=============================="
    local pct=$((score * 100 / max_score))
    if [[ $pct -ge 80 ]]; then
        echo -e "${GREEN}SCORE: $score/$max_score ($pct%) - EXCELLENT${NC}"
    elif [[ $pct -ge 60 ]]; then
        echo -e "${YELLOW}SCORE: $score/$max_score ($pct%) - ACCEPTABLE${NC}"
    else
        echo -e "${RED}SCORE: $score/$max_score ($pct%) - NEEDS IMPROVEMENT${NC}"
    fi
    
    # Log the check
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "{\"type\":\"metacognitive_check\",\"score\":$score,\"max\":$max_score,\"pct\":$pct,\"timestamp\":\"$timestamp\"}" >> memory/errors/metacognitive-log.jsonl
}

log_error() {
    local error_type="$1"
    local context="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    if [[ -z "$error_type" ]]; then
        echo "Available error types:"
        jq -r '.error_types | keys[]' "$ERRORS_FILE"
        echo ""
        read -p "Error type: " error_type
        read -p "Context: " context
    fi
    
    # Update frequency in error patterns
    local tmp=$(mktemp)
    jq --arg type "$error_type" \
       '.error_types[$type].frequency += 1 | .meta_learning.total_errors_caught += 1' \
       "$ERRORS_FILE" > "$tmp" && mv "$tmp" "$ERRORS_FILE"
    
    # Log the error
    echo "{\"type\":\"error_caught\",\"error_type\":\"$error_type\",\"context\":\"$context\",\"timestamp\":\"$timestamp\"}" >> memory/errors/error-log.jsonl
    
    echo -e "${GREEN}✓ Error logged: $error_type${NC}"
    echo "Prevention tip:"
    jq -r ".error_types.$error_type.prevention // \"No tip available\"" "$ERRORS_FILE"
}

show_stats() {
    echo "📊 ERROR DETECTION STATISTICS"
    echo "=============================="
    
    echo ""
    echo "Error Type Frequencies:"
    jq -r '.error_types | to_entries[] | "  \(.key): \(.value.frequency)"' "$ERRORS_FILE"
    
    echo ""
    echo "Meta-Learning Stats:"
    jq -r '.meta_learning | "  Errors caught: \(.total_errors_caught)\n  Errors missed: \(.total_errors_missed)"' "$ERRORS_FILE"
    
    if [[ -f "memory/errors/metacognitive-log.jsonl" ]]; then
        echo ""
        echo "Recent Check Scores:"
        tail -5 memory/errors/metacognitive-log.jsonl | jq -r '"  \(.timestamp): \(.score)/\(.max) (\(.pct)%)"'
    fi
}

case "$1" in
    quick)
        quick_check
        ;;
    full)
        full_check
        ;;
    log-error|log)
        log_error "$2" "$3"
        ;;
    stats)
        show_stats
        ;;
    *)
        echo "Metacognitive Check - Error Detection System"
        echo ""
        echo "Usage: $0 [quick|full|log-error|stats]"
        echo ""
        echo "  quick            - Fast 4-point pre-response check"
        echo "  full             - Complete 10-point quality check"
        echo "  log-error TYPE   - Log a caught error"
        echo "  stats            - Show error detection statistics"
        echo ""
        echo "Run 'quick' before important responses."
        echo "Run 'full' for decisions and complex tasks."
        ;;
esac
