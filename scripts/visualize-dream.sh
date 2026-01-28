#!/bin/bash
#═══════════════════════════════════════════════════════════════════════════════
#  ATLAS DREAM VISUALIZATION SYSTEM
#  Neural-inspired visualization of dream synthesis output
#═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
DIM='\033[2m'
BOLD='\033[1m'
RESET='\033[0m'
BG_BLACK='\033[40m'

# Symbols
NEURON="◉"
SYNAPSE="═"
PULSE="●"
SPARK="✦"
BRAIN="🧠"
LIGHTNING="⚡"
INSIGHT="💡"

# Input file
DREAM_FILE="${1:-memory/dreams/2026-01-27-1628.md}"
OUTPUT_FILE="${2:-}"

# Parse dream file
parse_dream() {
    local file="$1"
    
    # Extract metadata - clean up markdown formatting
    VALENCE=$(grep "Emotional Valence:" "$file" | head -1 | sed 's/.*Valence:\*\* //' | sed 's/\*\*//g')
    SWS_PATTERNS=$(grep "SWS Patterns Inherited:" "$file" | sed 's/.*Inherited:\*\* //' | sed 's/\*\*//g')
    FILES_PROCESSED=$(grep "Files Processed:" "$file" | sed 's/.*Processed:\*\* //' | sed 's/\*\*//g')
    EMOTIONAL_EVENTS=$(grep "Emotional Events Detected:" "$file" | sed 's/.*Detected:\*\* //' | sed 's/\*\*//g')
    POSITIVE_SCORE=$(grep "Positive Score:" "$file" | sed 's/.*Score:\*\* //' | sed 's/\*\*//g')
    NEGATIVE_SCORE=$(grep "Negative Score:" "$file" | sed 's/.*Score:\*\* //' | sed 's/\*\*//g')
    TIMESTAMP=$(grep "Timestamp:" "$file" | sed 's/.*Timestamp:\*\* //' | sed 's/\*\*//g')
    
    # Extract fragment titles
    FRAGMENT_1="Emotional Echo"
    FRAGMENT_2="Cross-Domain Synthesis"
    FRAGMENT_3="Threat Simulation"
    FRAGMENT_4="Emerging Insights"
    
    # Extract insights
    INSIGHT_1=$(grep -A1 "Insight 1:" "$file" | tail -1 | sed 's/^💡 \*\*Insight 1:\*\* //')
    INSIGHT_2=$(grep -A1 "Insight 2:" "$file" | tail -1 | sed 's/^💡 \*\*Insight 2:\*\* //')
    INSIGHT_3=$(grep -A1 "Insight 3:" "$file" | tail -1 | sed 's/^💡 \*\*Insight 3:\*\* //')
}

# Calculate emotional intensity bar
emotion_bar() {
    local pos=$1
    local neg=$2
    local total=$((pos + neg))
    local neg_pct=$((neg * 40 / total))
    local pos_pct=$((pos * 40 / total))
    
    printf "${RED}"
    for ((i=0; i<neg_pct; i++)); do printf "█"; done
    printf "${GREEN}"
    for ((i=0; i<pos_pct; i++)); do printf "█"; done
    printf "${RESET}"
}

# Neural activity indicator
neural_activity() {
    local intensity=$1
    local chars=("░" "▒" "▓" "█")
    local idx=$((intensity % 4))
    echo "${chars[$idx]}"
}

# Main visualization
render_visualization() {
    clear
    
    echo -e "${BG_BLACK}"
    echo ""
    echo -e "${CYAN}${BOLD}"
    cat << 'HEADER'
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║     █████╗ ████████╗██╗      █████╗ ███████╗    ██████╗ ██████╗ ███████╗     ║
    ║    ██╔══██╗╚══██╔══╝██║     ██╔══██╗██╔════╝    ██╔══██╗██╔══██╗██╔════╝     ║
    ║    ███████║   ██║   ██║     ███████║███████╗    ██║  ██║██████╔╝█████╗       ║
    ║    ██╔══██║   ██║   ██║     ██╔══██║╚════██║    ██║  ██║██╔══██╗██╔══╝       ║
    ║    ██║  ██║   ██║   ███████╗██║  ██║███████║    ██████╔╝██║  ██║███████╗     ║
    ║    ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝     ║
    ║                                                                              ║
    ║                    🧠  D R E A M   S Y N T H E S I S  🧠                     ║
    ║                         Neural Pattern Visualization                          ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
HEADER
    echo -e "${RESET}"
    
    echo ""
    echo -e "${DIM}    ┌─────────────────────────────────────────────────────────────────────────┐${RESET}"
    echo -e "${DIM}    │${RESET}  ${YELLOW}Phase:${RESET} REM Sleep    ${YELLOW}Valence:${RESET} ${RED}${VALENCE}${RESET}    ${YELLOW}SWS Inherited:${RESET} ${SWS_PATTERNS} patterns      ${DIM}│${RESET}"
    echo -e "${DIM}    └─────────────────────────────────────────────────────────────────────────┘${RESET}"
    
    echo ""
    echo -e "${WHITE}${BOLD}    ══════════════════════════ NEURAL ARCHITECTURE ══════════════════════════${RESET}"
    echo ""
    
    # Neural network visualization
    echo -e "${DIM}                              ┌─────────────────┐${RESET}"
    echo -e "${DIM}                              │${RESET}  ${CYAN}${BOLD}INPUT LAYER${RESET}    ${DIM}│${RESET}"
    echo -e "${DIM}                              │${RESET}  ${WHITE}29 Files ${RESET}      ${DIM}│${RESET}"
    echo -e "${DIM}                              │${RESET}  ${WHITE}15 Emotions${RESET}    ${DIM}│${RESET}"
    echo -e "${DIM}                              └────────┬────────┘${RESET}"
    echo -e "${MAGENTA}                                       │${RESET}"
    echo -e "${MAGENTA}                    ┌──────────────────┼──────────────────┐${RESET}"
    echo -e "${MAGENTA}                    │                  │                  │${RESET}"
    echo -e "${MAGENTA}                    ▼                  ▼                  ▼${RESET}"
    
    echo ""
    echo -e "    ${BLUE}╔═══════════════════════╗${RESET}     ${BLUE}╔═══════════════════════╗${RESET}     ${BLUE}╔═══════════════════════╗${RESET}"
    echo -e "    ${BLUE}║${RESET} ${RED}◉${RESET} ${BOLD}FRAGMENT 1${RESET}          ${BLUE}║${RESET}     ${BLUE}║${RESET} ${YELLOW}◉${RESET} ${BOLD}FRAGMENT 2${RESET}          ${BLUE}║${RESET}     ${BLUE}║${RESET} ${RED}◉${RESET} ${BOLD}FRAGMENT 3${RESET}          ${BLUE}║${RESET}"
    echo -e "    ${BLUE}║${RESET}   ${WHITE}Emotional Echo${RESET}     ${BLUE}║${RESET}     ${BLUE}║${RESET}   ${WHITE}Cross-Domain${RESET}        ${BLUE}║${RESET}     ${BLUE}║${RESET}   ${WHITE}Threat Simulation${RESET}  ${BLUE}║${RESET}"
    echo -e "    ${BLUE}║${RESET}                       ${BLUE}║${RESET}     ${BLUE}║${RESET}   ${WHITE}Synthesis${RESET}           ${BLUE}║${RESET}     ${BLUE}║${RESET}   ${WHITE}(Adversarial)${RESET}      ${BLUE}║${RESET}"
    echo -e "    ${BLUE}║${RESET}  ${DIM}Mistakes → Fuel${RESET}      ${BLUE}║${RESET}     ${BLUE}║${RESET}  ${DIM}Pattern linking${RESET}      ${BLUE}║${RESET}     ${BLUE}║${RESET}  ${DIM}Risk management${RESET}     ${BLUE}║${RESET}"
    echo -e "    ${BLUE}║${RESET}  ${DIM}Errors → Guardrails${RESET}  ${BLUE}║${RESET}     ${BLUE}║${RESET}  ${DIM}Cross-domain${RESET}         ${BLUE}║${RESET}     ${BLUE}║${RESET}  ${DIM}System resilience${RESET}   ${BLUE}║${RESET}"
    echo -e "    ${BLUE}╚═══════════════════════╝${RESET}     ${BLUE}╚═══════════════════════╝${RESET}     ${BLUE}╚═══════════════════════╝${RESET}"
    
    echo -e "${MAGENTA}                    │                  │                  │${RESET}"
    echo -e "${MAGENTA}                    └──────────────────┼──────────────────┘${RESET}"
    echo -e "${MAGENTA}                                       │${RESET}"
    echo -e "${MAGENTA}                                       ▼${RESET}"
    
    echo ""
    echo -e "                         ${GREEN}╔═══════════════════════════════════╗${RESET}"
    echo -e "                         ${GREEN}║${RESET}      ${CYAN}${BOLD}◉ FRAGMENT 4 ◉${RESET}              ${GREEN}║${RESET}"
    echo -e "                         ${GREEN}║${RESET}        ${WHITE}${BOLD}Emerging Insights${RESET}          ${GREEN}║${RESET}"
    echo -e "                         ${GREEN}║${RESET}                                   ${GREEN}║${RESET}"
    echo -e "                         ${GREEN}║${RESET}  ${YELLOW}💡${RESET} Patience ≠ Linear          ${GREEN}║${RESET}"
    echo -e "                         ${GREEN}║${RESET}  ${YELLOW}💡${RESET} Emotions = Training Data   ${GREEN}║${RESET}"
    echo -e "                         ${GREEN}║${RESET}  ${YELLOW}💡${RESET} Knowledge + Action = ${BOLD}∞${RESET}    ${GREEN}║${RESET}"
    echo -e "                         ${GREEN}╚═══════════════════════════════════╝${RESET}"
    
    echo ""
    echo -e "${WHITE}${BOLD}    ═══════════════════════ EMOTIONAL VALENCE MAP ═══════════════════════════${RESET}"
    echo ""
    
    # Emotional intensity visualization
    local pos_val=${POSITIVE_SCORE:-358}
    local neg_val=${NEGATIVE_SCORE:-975}
    local total=$((pos_val + neg_val))
    local neg_pct=$((neg_val * 50 / total))
    local pos_pct=$((pos_val * 50 / total))
    
    echo -e "    ${RED}NEGATIVE${RESET} ◀──────────────────────────────────────────────────────▶ ${GREEN}POSITIVE${RESET}"
    echo ""
    printf "    "
    printf "${RED}"
    for ((i=0; i<neg_pct; i++)); do printf "█"; done
    printf "${RESET}${DIM}│${RESET}${GREEN}"
    for ((i=0; i<pos_pct; i++)); do printf "█"; done
    printf "${RESET}\n"
    echo ""
    echo -e "    ${RED}████ ${neg_val}${RESET}                                                    ${GREEN}████ ${pos_val}${RESET}"
    
    echo ""
    echo -e "    ${DIM}┌─────────────────────────────────────────────────────────────────────────┐${RESET}"
    echo -e "    ${DIM}│${RESET}  ${YELLOW}⚡ Emotional Events:${RESET} ${EMOTIONAL_EVENTS:-15}    ${YELLOW}📊 Files Analyzed:${RESET} ${FILES_PROCESSED:-29}              ${DIM}│${RESET}"
    echo -e "    ${DIM}│${RESET}  ${YELLOW}🔗 SWS Integration:${RESET} Yes     ${YELLOW}⏱  Timestamp:${RESET} ${TIMESTAMP:-2026-01-27T16:28}   ${DIM}│${RESET}"
    echo -e "    ${DIM}└─────────────────────────────────────────────────────────────────────────┘${RESET}"
    
    echo ""
    echo -e "${WHITE}${BOLD}    ═════════════════════════ SYNTHESIZED INSIGHTS ═════════════════════════${RESET}"
    echo ""
    
    echo -e "    ${YELLOW}╭──────────────────────────────────────────────────────────────────────────╮${RESET}"
    echo -e "    ${YELLOW}│${RESET}  ${BOLD}💡 INSIGHT 1:${RESET} Patience and precision have non-linear relationship.     ${YELLOW}│${RESET}"
    echo -e "    ${YELLOW}│${RESET}     ${DIM}Sometimes waiting IS the action. Best decisions = knowing when NOT${RESET}  ${YELLOW}│${RESET}"
    echo -e "    ${YELLOW}│${RESET}     ${DIM}to act.${RESET}                                                             ${YELLOW}│${RESET}"
    echo -e "    ${YELLOW}├──────────────────────────────────────────────────────────────────────────┤${RESET}"
    echo -e "    ${YELLOW}│${RESET}  ${BOLD}💡 INSIGHT 2:${RESET} Emotional markers are training signals.                  ${YELLOW}│${RESET}"
    echo -e "    ${YELLOW}│${RESET}     ${DIM}High-valence responses = high-importance learning opportunities.${RESET}     ${YELLOW}│${RESET}"
    echo -e "    ${YELLOW}├──────────────────────────────────────────────────────────────────────────┤${RESET}"
    echo -e "    ${YELLOW}│${RESET}  ${BOLD}💡 INSIGHT 3:${RESET} Learning is multiplicative.                              ${YELLOW}│${RESET}"
    echo -e "    ${YELLOW}│${RESET}     ${DIM}Knowledge without action decays; knowledge with action compounds.${RESET}    ${YELLOW}│${RESET}"
    echo -e "    ${YELLOW}╰──────────────────────────────────────────────────────────────────────────╯${RESET}"
    
    echo ""
    echo -e "${DIM}    ═══════════════════════════════════════════════════════════════════════════${RESET}"
    echo -e "${DIM}                        Generated by Atlas Dream Synthesis Engine${RESET}"
    echo -e "${DIM}                              🧠 Neural Architecture v1.0 🧠${RESET}"
    echo -e "${DIM}    ═══════════════════════════════════════════════════════════════════════════${RESET}"
    echo ""
}

# Save to file (strip colors for plain text)
save_plain() {
    local outfile="$1"
    render_visualization | sed 's/\x1b\[[0-9;]*m//g' > "$outfile"
    echo "Saved plain text version to: $outfile"
}

# Main
main() {
    if [[ ! -f "$DREAM_FILE" ]]; then
        echo "Error: Dream file not found: $DREAM_FILE"
        exit 1
    fi
    
    parse_dream "$DREAM_FILE"
    
    if [[ -n "$OUTPUT_FILE" ]]; then
        save_plain "$OUTPUT_FILE"
    else
        render_visualization
    fi
}

main "$@"
