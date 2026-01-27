#!/usr/bin/env python3
"""
ATLAS GUT CHECK SYSTEM
Implements "somatic markers" - quick emotional assessments before decisions.
Based on Damasio's research: emotions make reasoning BETTER, not worse.

Usage: Before any significant decision, run a gut check.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

CLAWD_DIR = Path.home() / "clawd"
GUT_LOG = CLAWD_DIR / "memory" / "gut-checks.jsonl"

# Risk factors that should trigger gut-bad
RED_FLAGS = [
    "all in", "yolo", "guaranteed", "can't lose", "100%",
    "everyone is doing it", "fomo", "hurry", "last chance",
    "trust me", "no risk", "sure thing", "free money",
    "revenge trade", "double down", "make it back"
]

# Positive signals
GREEN_FLAGS = [
    "researched", "tested", "backtested", "small position",
    "risk managed", "stop loss", "diversified", "understood",
    "edge", "data shows", "historically", "probability"
]

def gut_check(decision: str, context: str = ""):
    """Run a gut check on a decision."""
    decision_lower = decision.lower()
    context_lower = context.lower()
    full_text = decision_lower + " " + context_lower
    
    red_count = sum(1 for flag in RED_FLAGS if flag in full_text)
    green_count = sum(1 for flag in GREEN_FLAGS if flag in full_text)
    
    triggered_reds = [flag for flag in RED_FLAGS if flag in full_text]
    triggered_greens = [flag for flag in GREEN_FLAGS if flag in full_text]
    
    # Calculate gut feeling
    if red_count >= 2:
        gut = "🚨 BAD"
        recommendation = "STOP. Multiple red flags detected. Reconsider."
        score = max(0, 30 - (red_count * 10))
    elif red_count == 1:
        gut = "⚠️ CAUTIOUS"
        recommendation = "Proceed with extra caution. Address the red flag first."
        score = 50
    elif green_count >= 2:
        gut = "✅ GOOD"
        recommendation = "Proceed. Multiple positive signals."
        score = min(90, 60 + (green_count * 10))
    elif green_count == 1:
        gut = "🤔 NEUTRAL-POSITIVE"
        recommendation = "Probably okay. Consider additional validation."
        score = 65
    else:
        gut = "🤔 NEUTRAL"
        recommendation = "No strong signals. Use judgment."
        score = 50
    
    # Log it
    entry = {
        "timestamp": datetime.now().isoformat(),
        "decision": decision,
        "context": context,
        "gut": gut,
        "score": score,
        "red_flags": triggered_reds,
        "green_flags": triggered_greens,
        "recommendation": recommendation
    }
    
    GUT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(GUT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    # Output
    print("=" * 50)
    print("🧠 ATLAS GUT CHECK")
    print("=" * 50)
    print(f"Decision: {decision}")
    if context:
        print(f"Context: {context}")
    print("")
    print(f"GUT FEELING: {gut} (score: {score})")
    print(f"RECOMMENDATION: {recommendation}")
    
    if triggered_reds:
        print(f"\n🚨 RED FLAGS: {', '.join(triggered_reds)}")
    if triggered_greens:
        print(f"\n✅ GREEN FLAGS: {', '.join(triggered_greens)}")
    
    print("=" * 50)
    
    return score >= 50

def review_gut_history(n: int = 10):
    """Review recent gut checks."""
    if not GUT_LOG.exists():
        print("No gut checks logged yet.")
        return
    
    entries = []
    with open(GUT_LOG, "r") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    
    print("📜 RECENT GUT CHECKS")
    print("=" * 50)
    
    for e in entries[-n:]:
        print(f"\n[{e['timestamp'][:10]}] {e['gut']} (score: {e['score']})")
        print(f"   Decision: {e['decision'][:60]}...")
        if e['red_flags']:
            print(f"   ⚠️ Red flags: {', '.join(e['red_flags'])}")

def main():
    if len(sys.argv) < 2:
        print("ATLAS GUT CHECK SYSTEM")
        print("=" * 40)
        print("Implements somatic markers for decision-making")
        print("")
        print("Usage:")
        print("  atlas-gut-check.py check <decision> [context]")
        print("  atlas-gut-check.py history [n]")
        print("")
        print("Example:")
        print('  atlas-gut-check.py check "Buy 100 TSLA calls" "Earnings tomorrow, could moon"')
        return
    
    cmd = sys.argv[1]
    
    if cmd == "check" and len(sys.argv) >= 3:
        decision = sys.argv[2]
        context = sys.argv[3] if len(sys.argv) > 3 else ""
        gut_check(decision, context)
    
    elif cmd == "history":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        review_gut_history(n)
    
    else:
        print("Unknown command. Run without args for help.")

if __name__ == "__main__":
    main()
