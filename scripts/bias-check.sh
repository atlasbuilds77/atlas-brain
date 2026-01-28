#!/bin/bash
# bias-check.sh - Pre-Decision Bias Mitigation
# Run before making important decisions
# Usage: ./bias-check.sh [quick|full|trading|log]

BIAS_LOG="memory/biases/bias-log.jsonl"
cd "$(dirname "$0")/.."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# The 7 major biases to check
BIASES=(
    "confirmation:Am I only seeking evidence that confirms what I already believe?"
    "anchoring:Am I over-relying on the first piece of information I received?"
    "overconfidence:Am I more certain than the evidence supports?"
    "loss_aversion:Am I avoiding a good decision just to prevent a potential loss?"
    "recency:Am I giving too much weight to recent events?"
    "status_quo:Am I preferring the current state just because it's familiar?"
    "sunk_cost:Am I continuing because of past investment rather than future value?"
)

quick_check() {
    echo -e "${BLUE}⚖️  BIAS QUICK CHECK${NC}"
    echo "===================="
    echo ""
    
    local biases_detected=0
    local biases_checked=0
    
    for bias_entry in "${BIASES[@]}"; do
        local bias_name="${bias_entry%%:*}"
        local bias_question="${bias_entry#*:}"
        
        ((biases_checked++))
        echo -e "${YELLOW}$bias_name:${NC}"
        echo "  $bias_question"
        echo -n "  Risk present? [y/n/maybe]: "
        read response
        
        if [[ "$response" == "y" ]]; then
            ((biases_detected++))
            echo -e "  ${RED}⚠ BIAS DETECTED - Apply mitigation${NC}"
            show_mitigation "$bias_name"
        elif [[ "$response" == "maybe" ]]; then
            echo -e "  ${YELLOW}⚡ Uncertain - Consider more carefully${NC}"
        else
            echo -e "  ${GREEN}✓ Clear${NC}"
        fi
        echo ""
    done
    
    # Summary
    echo "===================="
    local score=$((biases_checked - biases_detected))
    echo -e "Score: ${GREEN}$score${NC}/$biases_checked biases mitigated"
    
    if [[ $biases_detected -gt 0 ]]; then
        echo -e "${YELLOW}⚠ $biases_detected bias(es) detected - address before deciding${NC}"
    else
        echo -e "${GREEN}✅ No obvious biases detected${NC}"
    fi
    
    # Log the check
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "{\"type\":\"bias_check\",\"context\":\"quick\",\"detected\":$biases_detected,\"total\":$biases_checked,\"timestamp\":\"$timestamp\"}" >> "$BIAS_LOG"
    
    return $biases_detected
}

trading_check() {
    echo -e "${BLUE}📈 TRADING BIAS CHECK${NC}"
    echo "======================"
    echo ""
    echo "Trading-specific biases to watch for:"
    echo ""
    
    local issues=0
    
    # T1: FOMO
    echo -e "${YELLOW}1. FOMO (Fear of Missing Out):${NC}"
    echo "   Am I entering because I'm afraid of missing gains?"
    echo -n "   Risk present? [y/n]: "
    read fomo
    [[ "$fomo" == "y" ]] && ((issues++)) && echo -e "   ${RED}⚠ Wait for your setup, not the crowd${NC}"
    
    # T2: Revenge Trading
    echo -e "\n${YELLOW}2. Revenge Trading:${NC}"
    echo "   Am I trying to recover a recent loss quickly?"
    echo -n "   Risk present? [y/n]: "
    read revenge
    [[ "$revenge" == "y" ]] && ((issues++)) && echo -e "   ${RED}⚠ Step away. Losses don't require revenge${NC}"
    
    # T3: Overtrading
    echo -e "\n${YELLOW}3. Overtrading:${NC}"
    echo "   Am I trading out of boredom or action-seeking?"
    echo -n "   Risk present? [y/n]: "
    read overtrade
    [[ "$overtrade" == "y" ]] && ((issues++)) && echo -e "   ${RED}⚠ No trade is also a position${NC}"
    
    # T4: Position Size Bias
    echo -e "\n${YELLOW}4. Position Size Bias:${NC}"
    echo "   Am I sizing based on conviction rather than risk?"
    echo -n "   Risk present? [y/n]: "
    read size_bias
    [[ "$size_bias" == "y" ]] && ((issues++)) && echo -e "   ${RED}⚠ Size for what you can lose, not what you might gain${NC}"
    
    # T5: Anchoring to Entry
    echo -e "\n${YELLOW}5. Entry Price Anchoring:${NC}"
    echo "   Am I holding because of my entry price rather than current value?"
    echo -n "   Risk present? [y/n]: "
    read anchor
    [[ "$anchor" == "y" ]] && ((issues++)) && echo -e "   ${RED}⚠ The market doesn't care about your entry${NC}"
    
    # T6: Confirmation from CT
    echo -e "\n${YELLOW}6. CT/Social Confirmation:${NC}"
    echo "   Am I influenced by what others are saying on Twitter/Discord?"
    echo -n "   Risk present? [y/n]: "
    read social
    [[ "$social" == "y" ]] && ((issues++)) && echo -e "   ${RED}⚠ They're not managing your risk${NC}"
    
    # T7: Recency of Wins/Losses
    echo -e "\n${YELLOW}7. Recent P&L Influence:${NC}"
    echo "   Are recent wins making me overconfident or losses making me timid?"
    echo -n "   Risk present? [y/n]: "
    read recency
    [[ "$recency" == "y" ]] && ((issues++)) && echo -e "   ${RED}⚠ Each trade is independent${NC}"
    
    echo ""
    echo "======================"
    if [[ $issues -eq 0 ]]; then
        echo -e "${GREEN}✅ CLEAR TO TRADE - No obvious biases${NC}"
    elif [[ $issues -le 2 ]]; then
        echo -e "${YELLOW}⚠ CAUTION - $issues bias(es) detected${NC}"
        echo "   Address these before executing."
    else
        echo -e "${RED}🛑 STOP - $issues biases detected${NC}"
        echo "   Strongly consider NOT trading right now."
    fi
    
    # Log
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "{\"type\":\"bias_check\",\"context\":\"trading\",\"issues\":$issues,\"timestamp\":\"$timestamp\"}" >> "$BIAS_LOG"
}

show_mitigation() {
    local bias="$1"
    case "$bias" in
        confirmation)
            echo -e "  ${BLUE}Mitigation: Actively seek disconfirming evidence${NC}"
            echo "  Ask: What would prove me wrong?"
            ;;
        anchoring)
            echo -e "  ${BLUE}Mitigation: Generate estimate BEFORE looking at reference${NC}"
            echo "  Ask: What would I think with fresh eyes?"
            ;;
        overconfidence)
            echo -e "  ${BLUE}Mitigation: Widen confidence intervals${NC}"
            echo "  Ask: What's my track record on similar predictions?"
            ;;
        loss_aversion)
            echo -e "  ${BLUE}Mitigation: Frame as opportunity cost${NC}"
            echo "  Ask: What am I giving up by not acting?"
            ;;
        recency)
            echo -e "  ${BLUE}Mitigation: Look at longer time series${NC}"
            echo "  Ask: What does the base rate say?"
            ;;
        status_quo)
            echo -e "  ${BLUE}Mitigation: Imagine you're starting fresh${NC}"
            echo "  Ask: Would I choose this if starting over?"
            ;;
        sunk_cost)
            echo -e "  ${BLUE}Mitigation: Ignore past investment${NC}"
            echo "  Ask: Based only on future prospects, would I start this today?"
            ;;
    esac
}

log_bias() {
    local bias_type="$1"
    local outcome="$2"
    local notes="$3"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    echo "{\"type\":\"bias_incident\",\"bias\":\"$bias_type\",\"outcome\":\"$outcome\",\"notes\":\"$notes\",\"timestamp\":\"$timestamp\"}" >> "$BIAS_LOG"
    echo -e "${GREEN}✓ Bias incident logged${NC}"
}

show_stats() {
    echo -e "${BLUE}📊 BIAS TRACKING STATISTICS${NC}"
    echo "============================"
    
    if [[ ! -f "$BIAS_LOG" ]]; then
        echo "No bias log found"
        return
    fi
    
    echo ""
    echo "Check Counts:"
    grep -c '"type":"bias_check"' "$BIAS_LOG" 2>/dev/null || echo "0"
    
    echo ""
    echo "Recent Checks:"
    grep '"type":"bias_check"' "$BIAS_LOG" | tail -5 | jq -r '"  \(.timestamp): \(.context) - \(.detected // .issues) issues"'
    
    echo ""
    echo "Bias Incidents:"
    grep '"type":"bias_incident"' "$BIAS_LOG" | jq -r '"  \(.timestamp): \(.bias) → \(.outcome)"' | tail -5
}

case "$1" in
    quick|"")
        quick_check
        ;;
    full)
        quick_check
        ;;
    trading)
        trading_check
        ;;
    log)
        log_bias "$2" "$3" "$4"
        ;;
    stats)
        show_stats
        ;;
    *)
        echo "Bias Check - Pre-Decision Bias Mitigation"
        echo ""
        echo "Usage: $0 [quick|full|trading|log|stats]"
        echo ""
        echo "  quick (default)  - 7-bias quick check"
        echo "  trading          - Trading-specific bias check"
        echo "  log TYPE OUTCOME - Log a bias incident"
        echo "  stats            - Show bias tracking stats"
        echo ""
        echo "Run before important decisions!"
        ;;
esac
