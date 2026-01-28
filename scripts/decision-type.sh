#!/bin/bash
#
# ATLAS DECISION TYPE CLASSIFIER
# Based on Gigerenzer's research: heuristics vs complex models
#
# Classifies decisions into:
# - INTUITION: Familiar domain, use pattern matching + somatic markers
# - ANALYSIS: Novel domain, use deliberate reasoning
# - HYBRID: Uncertain - use both and compare
#
# Usage: decision-type.sh "decision description" [domain]
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAWD_DIR="${HOME}/clawd"
PATTERNS_DIR="${CLAWD_DIR}/memory/patterns"
DOMAINS_FILE="${CLAWD_DIR}/memory/calibration/domain-expertise.json"

# Domain expertise levels (will be updated over time)
# Using case statement for better compatibility
get_domain_expertise() {
    case "$1" in
        trading) echo "0.7" ;;
        crypto) echo "0.6" ;;
        communication) echo "0.8" ;;
        scheduling) echo "0.7" ;;
        research) echo "0.75" ;;
        coding) echo "0.8" ;;
        market_analysis) echo "0.65" ;;
        risk_management) echo "0.6" ;;
        social_media) echo "0.7" ;;
        *) echo "0.5" ;;
    esac
}

# Uncertainty indicators
UNCERTAINTY_WORDS=(
    "might" "maybe" "possibly" "uncertain" "unclear"
    "never tried" "first time" "new" "unfamiliar"
    "don't know" "not sure" "risky" "volatile"
)

# Familiar indicators
FAMILIAR_WORDS=(
    "always" "usually" "similar to" "like before"
    "standard" "routine" "typical" "common"
    "experienced" "done this" "know how"
)

decision="$1"
domain="${2:-general}"
decision_lower=$(echo "$decision" | tr '[:upper:]' '[:lower:]')

# Count uncertainty indicators
uncertainty_count=0
for word in "${UNCERTAINTY_WORDS[@]}"; do
    if [[ "$decision_lower" == *"$word"* ]]; then
        ((uncertainty_count++))
    fi
done

# Count familiarity indicators
familiar_count=0
for word in "${FAMILIAR_WORDS[@]}"; do
    if [[ "$decision_lower" == *"$word"* ]]; then
        ((familiar_count++))
    fi
done

# Get domain expertise
expertise=$(get_domain_expertise "$domain")

# Calculate decision type score
# High expertise + high familiarity + low uncertainty = INTUITION
# Low expertise + high uncertainty + low familiarity = ANALYSIS

familiarity_score=$(echo "scale=2; $familiar_count / 3" | bc)
uncertainty_score=$(echo "scale=2; $uncertainty_count / 3" | bc)
[[ "$familiarity_score" > 1 ]] && familiarity_score=1
[[ "$uncertainty_score" > 1 ]] && uncertainty_score=1

intuition_score=$(echo "scale=2; ($expertise + $familiarity_score - $uncertainty_score) / 2" | bc)

# Determine decision type
echo "=============================================="
echo "🧠 ATLAS DECISION TYPE CLASSIFIER"
echo "=============================================="
echo ""
echo "📝 Decision: $decision"
echo "📂 Domain: $domain"
echo ""
echo "📊 ANALYSIS:"
echo "   Domain expertise: ${expertise}"
echo "   Familiarity signals: $familiar_count"
echo "   Uncertainty signals: $uncertainty_count"
echo "   Intuition score: $intuition_score"
echo ""

# Classify
if (( $(echo "$intuition_score >= 0.6" | bc -l) )); then
    echo "🎯 DECISION TYPE: INTUITION (System 1)"
    echo ""
    echo "   ✅ Familiar domain with established patterns"
    echo "   ✅ Use somatic markers and gut feeling"
    echo "   ✅ Fast pattern matching appropriate"
    echo ""
    echo "   💡 ACTION: Run somatic-marker.py check first"
    echo "      If gut feeling is strong → trust it"
    echo "      If gut feeling is weak → add analysis"
    decision_type="INTUITION"

elif (( $(echo "$intuition_score <= 0.3" | bc -l) )); then
    echo "🎯 DECISION TYPE: ANALYSIS (System 2)"
    echo ""
    echo "   ⚠️ Novel/uncertain domain"
    echo "   ⚠️ Limited pattern matching available"
    echo "   ⚠️ Deliberate reasoning required"
    echo ""
    echo "   💡 ACTION: Use systematic analysis"
    echo "      - List pros/cons explicitly"
    echo "      - Research similar cases"
    echo "      - Consider multiple scenarios"
    echo "      - Don't trust gut (insufficient data)"
    decision_type="ANALYSIS"

else
    echo "🎯 DECISION TYPE: HYBRID"
    echo ""
    echo "   🔄 Mixed signals - use both systems"
    echo "   🔄 Check intuition AND verify with analysis"
    echo "   🔄 If they agree → high confidence"
    echo "   🔄 If they conflict → investigate why (learning opportunity!)"
    echo ""
    echo "   💡 ACTION:"
    echo "      1. Run somatic-marker.py check"
    echo "      2. Do explicit analysis"
    echo "      3. Compare results"
    echo "      4. Log for future calibration"
    decision_type="HYBRID"
fi

echo ""
echo "=============================================="

# Return decision type for scripting
echo "$decision_type" > /tmp/atlas_decision_type

# Also run somatic marker check if available
if [[ -x "$SCRIPT_DIR/somatic-marker.py" ]]; then
    echo ""
    echo "Running somatic marker check..."
    python3 "$SCRIPT_DIR/somatic-marker.py" check "$decision"
fi
