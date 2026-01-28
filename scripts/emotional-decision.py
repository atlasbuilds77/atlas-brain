#!/usr/bin/env python3
"""
ATLAS EMOTIONAL DECISION INTEGRATION

The unified decision system that integrates:
- Somatic markers (emotional intuition)
- Confidence calibration (realistic self-assessment)  
- Decision type classification (intuition vs analysis)
- Emotional context awareness
- Dual-process thinking (System 1 + System 2)

This is the main entry point for making emotionally-intelligent decisions.

Usage:
  emotional-decision.py "decision description" [--stakes high/medium/low] [--domain trading]
"""

import json
import sys
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Tuple, Dict, Any

CLAWD_DIR = Path.home() / "clawd"
SCRIPTS_DIR = CLAWD_DIR / "scripts"
DECISIONS_LOG = CLAWD_DIR / "memory" / "decisions" / "decision-log.jsonl"

# Context detection patterns
HIGH_STAKES_PATTERNS = [
    "all capital", "life changing", "critical", "urgent", "can't reverse",
    "major", "significant", "large position", "irreversible"
]

HIGH_PRESSURE_PATTERNS = [
    "now", "immediately", "hurry", "deadline", "expiring", "last chance",
    "closing", "running out", "quick", "fast"
]

HIGH_UNCERTAINTY_PATTERNS = [
    "unknown", "uncertain", "unpredictable", "volatile", "risky",
    "first time", "never done", "experimental", "novel"
]

def detect_emotional_context(decision: str) -> Dict[str, Any]:
    """
    Detect emotional context factors from decision description.
    """
    decision_lower = decision.lower()
    
    stakes_score = sum(1 for p in HIGH_STAKES_PATTERNS if p in decision_lower)
    pressure_score = sum(1 for p in HIGH_PRESSURE_PATTERNS if p in decision_lower)
    uncertainty_score = sum(1 for p in HIGH_UNCERTAINTY_PATTERNS if p in decision_lower)
    
    # Normalize to levels
    stakes = "high" if stakes_score >= 2 else ("medium" if stakes_score == 1 else "low")
    pressure = "high" if pressure_score >= 2 else ("medium" if pressure_score == 1 else "low")
    uncertainty = "high" if uncertainty_score >= 2 else ("medium" if uncertainty_score == 1 else "low")
    
    # Calculate emotional weight adjustment
    # High stakes + high uncertainty = trust intuition LESS
    # Low stakes + low uncertainty = trust intuition MORE
    if stakes == "high" and uncertainty == "high":
        intuition_weight = 0.3
        analysis_weight = 0.7
        recommendation = "Favor analysis. High stakes + uncertainty = don't trust gut alone."
    elif stakes == "low" and uncertainty == "low":
        intuition_weight = 0.7
        analysis_weight = 0.3
        recommendation = "Trust intuition. Low stakes routine decision."
    elif pressure == "high":
        intuition_weight = 0.6
        analysis_weight = 0.4
        recommendation = "Time pressure suggests using intuition, but verify basics."
    else:
        intuition_weight = 0.5
        analysis_weight = 0.5
        recommendation = "Balanced approach. Use both intuition and analysis."
    
    return {
        "stakes": stakes,
        "pressure": pressure,
        "uncertainty": uncertainty,
        "intuition_weight": intuition_weight,
        "analysis_weight": analysis_weight,
        "recommendation": recommendation
    }

def run_somatic_check(decision: str) -> Dict[str, Any]:
    """Run somatic marker check and parse results."""
    try:
        # Import the module directly for cleaner integration
        sys.path.insert(0, str(SCRIPTS_DIR))
        from importlib import import_module
        # We'll call it as subprocess for now for isolation
        result = subprocess.run(
            ["python3", str(SCRIPTS_DIR / "somatic-marker.py"), "check", decision],
            capture_output=True, text=True, timeout=10
        )
        
        # Parse output for score (simple extraction)
        output = result.stdout
        score = 0
        feeling = "neutral"
        
        for line in output.split("\n"):
            if "GUT FEELING:" in line:
                if "STRONGLY_POSITIVE" in line.upper():
                    feeling = "strongly_positive"
                    score = 40
                elif "STRONGLY_NEGATIVE" in line.upper():
                    feeling = "strongly_negative"
                    score = -40
                elif "POSITIVE" in line.upper():
                    feeling = "positive"
                    score = 20
                elif "NEGATIVE" in line.upper():
                    feeling = "negative"
                    score = -20
                
                # Try to extract actual score
                if "score:" in line:
                    try:
                        score_str = line.split("score:")[1].split(")")[0].strip()
                        score = float(score_str)
                    except:
                        pass
        
        return {
            "score": score,
            "feeling": feeling,
            "raw_output": output,
            "success": True
        }
    except Exception as e:
        return {
            "score": 0,
            "feeling": "unknown",
            "error": str(e),
            "success": False
        }

def classify_decision_type(decision: str, domain: str) -> str:
    """Classify whether to use intuition or analysis."""
    # Domain expertise mapping
    expertise_levels = {
        "trading": 0.65,
        "crypto": 0.55,
        "communication": 0.8,
        "research": 0.75,
        "coding": 0.8,
        "general": 0.5
    }
    
    expertise = expertise_levels.get(domain, 0.5)
    
    # Check for novelty indicators
    novel_words = ["first time", "never", "new", "unknown", "unfamiliar"]
    familiar_words = ["always", "usually", "similar", "done before", "routine"]
    
    decision_lower = decision.lower()
    novel_count = sum(1 for w in novel_words if w in decision_lower)
    familiar_count = sum(1 for w in familiar_words if w in decision_lower)
    
    novelty = novel_count - familiar_count
    
    # Decision type based on expertise and novelty
    score = expertise - (novelty * 0.15)
    
    if score > 0.6:
        return "INTUITION"
    elif score < 0.4:
        return "ANALYSIS"
    else:
        return "HYBRID"

def integrated_decision(decision: str, stakes: str = None, domain: str = "general"):
    """
    The main integrated decision function.
    Combines all emotional intelligence systems.
    """
    print("=" * 70)
    print("🧠 ATLAS EMOTIONAL DECISION SYSTEM")
    print("=" * 70)
    print(f"\n📝 Decision: {decision}")
    print(f"📂 Domain: {domain}")
    
    # Step 1: Emotional Context
    print("\n" + "-" * 50)
    print("STEP 1: EMOTIONAL CONTEXT ANALYSIS")
    context = detect_emotional_context(decision)
    if stakes:
        context["stakes"] = stakes
    
    print(f"   Stakes: {context['stakes'].upper()}")
    print(f"   Time Pressure: {context['pressure'].upper()}")
    print(f"   Uncertainty: {context['uncertainty'].upper()}")
    print(f"   Intuition Weight: {context['intuition_weight']:.0%}")
    print(f"   Analysis Weight: {context['analysis_weight']:.0%}")
    
    # Step 2: Decision Type Classification
    print("\n" + "-" * 50)
    print("STEP 2: DECISION TYPE CLASSIFICATION")
    decision_type = classify_decision_type(decision, domain)
    
    if decision_type == "INTUITION":
        print("   🎯 Type: INTUITION (System 1)")
        print("   → Familiar domain, trust pattern matching")
    elif decision_type == "ANALYSIS":
        print("   🔬 Type: ANALYSIS (System 2)")
        print("   → Novel/uncertain, use deliberate reasoning")
    else:
        print("   🔄 Type: HYBRID")
        print("   → Use both, compare results")
    
    # Step 3: Somatic Marker Check
    print("\n" + "-" * 50)
    print("STEP 3: SOMATIC MARKER CHECK (Gut Feeling)")
    somatic = run_somatic_check(decision)
    
    if somatic["success"]:
        print(f"   Gut Feeling: {somatic['feeling'].upper()}")
        print(f"   Intuition Score: {somatic['score']:.1f}")
    else:
        print(f"   ⚠️ Could not run somatic check: {somatic.get('error', 'unknown')}")
        somatic["score"] = 0
    
    # Step 4: Dual-Process Integration
    print("\n" + "-" * 50)
    print("STEP 4: DUAL-PROCESS INTEGRATION")
    
    # Weight the intuition score by context
    weighted_intuition = somatic["score"] * context["intuition_weight"]
    
    print(f"   Raw Intuition: {somatic['score']:.1f}")
    print(f"   Weighted (by context): {weighted_intuition:.1f}")
    
    # Final recommendation
    print("\n" + "=" * 70)
    print("🎯 INTEGRATED RECOMMENDATION")
    print("=" * 70)
    
    # Combine all factors
    if somatic["feeling"] == "strongly_negative":
        print("\n   🚨 STRONG NEGATIVE GUT FEELING")
        print("   → Past patterns strongly suggest caution")
        print("   → Consider NOT proceeding, or add heavy analysis")
        final_action = "CAUTION"
        
    elif somatic["feeling"] == "strongly_positive" and context["uncertainty"] != "high":
        print("\n   ✅ STRONG POSITIVE GUT FEELING")
        print("   → Pattern matching confident")
        print("   → Proceed with standard risk management")
        final_action = "PROCEED"
        
    elif decision_type == "ANALYSIS" or context["uncertainty"] == "high":
        print("\n   🔬 REQUIRES DELIBERATE ANALYSIS")
        print("   → Don't rely on gut feeling alone")
        print("   → List explicit pros/cons")
        print("   → Research similar cases")
        print("   → Consider multiple scenarios")
        final_action = "ANALYZE"
        
    elif decision_type == "INTUITION" and somatic["score"] > 10:
        print("\n   ✅ INTUITION SUGGESTS PROCEED")
        print("   → Familiar pattern, positive signals")
        print("   → Trust gut with standard checks")
        final_action = "PROCEED"
        
    elif decision_type == "INTUITION" and somatic["score"] < -10:
        print("\n   ⚠️ INTUITION SUGGESTS CAUTION")
        print("   → Familiar pattern, but negative signals")
        print("   → Investigate what's triggering the warning")
        final_action = "CAUTION"
        
    else:
        print("\n   🔄 MIXED SIGNALS - USE HYBRID APPROACH")
        print("   → Check intuition AND verify with analysis")
        print("   → If they agree: high confidence")
        print("   → If they conflict: investigate why (learning opportunity)")
        final_action = "HYBRID"
    
    # Context-specific advice
    print(f"\n   📊 Context advice: {context['recommendation']}")
    
    print("\n" + "=" * 70)
    
    # Log decision for future learning
    log_decision(decision, domain, context, somatic, decision_type, final_action)
    
    return {
        "action": final_action,
        "context": context,
        "somatic": somatic,
        "decision_type": decision_type
    }

def log_decision(decision, domain, context, somatic, decision_type, final_action):
    """Log decision for future learning and calibration."""
    DECISIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "decision": decision,
        "domain": domain,
        "context": context,
        "somatic_score": somatic.get("score", 0),
        "somatic_feeling": somatic.get("feeling", "unknown"),
        "decision_type": decision_type,
        "recommendation": final_action,
        "outcome": None,
        "resolved": False
    }
    
    with open(DECISIONS_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

def main():
    parser = argparse.ArgumentParser(
        description="ATLAS Emotional Decision Integration"
    )
    parser.add_argument("decision", help="Decision to evaluate")
    parser.add_argument("--stakes", "-s", choices=["high", "medium", "low"],
                       help="Override stakes level")
    parser.add_argument("--domain", "-d", default="general",
                       help="Decision domain (trading, communication, etc.)")
    
    args = parser.parse_args()
    
    integrated_decision(args.decision, args.stakes, args.domain)

if __name__ == "__main__":
    main()
