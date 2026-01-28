#!/usr/bin/env python3
"""
Example: Integrating brain visualization with pattern recognition
Demonstrates how to add brain event logging to the pattern-api.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Direct implementation instead of import
def log_brain_event(event_type: str, message: str, intensity: float = 0.5, metadata: dict = None):
    """Log a cognitive event."""
    event = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "event_type": event_type,
        "message": message,
        "intensity": max(0.0, min(1.0, intensity)),
        "metadata": metadata or {}
    }
    
    log_path = Path("logs/brain-events.jsonl")
    log_path.parent.mkdir(exist_ok=True)
    
    with open(log_path, 'a') as f:
        f.write(json.dumps(event) + '\n')


def example_pattern_match_integration():
    """
    Example of integrating with pattern recognition system.
    
    In your actual pattern-api.py, add this code:
    """
    
    # Simulated pattern match
    class PatternMatch:
        def __init__(self, name, valence, confidence):
            self.name = name
            self.valence = valence  # 'positive', 'negative', 'neutral'
            self.confidence = confidence
    
    # Example matches
    matches = [
        PatternMatch("FOMO_trade", "negative", 0.85),
        PatternMatch("bull_market_confirmation", "positive", 0.72),
        PatternMatch("overconfidence_detected", "negative", 0.68)
    ]
    
    # Log each match to brain visualization
    for match in matches:
        log_brain_event(
            "pattern_match",
            f"Pattern '{match.name}' matched - {match.valence.upper()}",
            match.confidence,
            {"pattern_name": match.name, "valence": match.valence, "confidence": match.confidence, "context": "trading_analysis"}
        )
        print(f"✓ Logged pattern: {match.name} ({match.valence})")


def example_somatic_marker_integration():
    """
    Example of integrating with somatic marker system.
    
    In your somatic-marker.py, add this code:
    """
    
    # Simulated emotional markers
    markers = [
        {"name": "anxiety", "intensity": 0.7, "trigger": "market_drop"},
        {"name": "excitement", "intensity": 0.6, "trigger": "opportunity_detected"},
        {"name": "fear", "intensity": 0.8, "trigger": "loss_approaching"}
    ]
    
    for marker in markers:
        log_brain_event(
            "emotion",
            f"Somatic marker: {marker['name']}",
            marker["intensity"],
            {"emotion": marker["name"], "intensity": marker["intensity"], "trigger": marker["trigger"], "context": "trading"}
        )
        print(f"✓ Logged emotion: {marker['name']} (intensity: {marker['intensity']})")


def example_cognitive_mode_integration():
    """
    Example of integrating with cognitive mode system.
    """
    
    # Simulated mode switches
    mode_changes = [
        ("ECN", "DMN", "Entering creative exploration mode"),
        ("DMN", "ECN", "Focused analysis required"),
        ("ECN", "MIXED", "Complex problem solving")
    ]
    
    for old_mode, new_mode, reason in mode_changes:
        log_brain_event(
            "mode_switch",
            f"{new_mode} MODE: {reason}",
            1.0,
            {"old_mode": old_mode, "new_mode": new_mode, "reason": reason}
        )
        print(f"✓ Logged mode switch: {old_mode} → {new_mode}")


def example_metacognition_integration():
    """
    Example of integrating with metacognitive checks.
    """
    
    checks = [
        "verifying_source_credibility",
        "cross_checking_facts",
        "detecting_contradictions",
        "assessing_confidence_calibration"
    ]
    
    for check in checks:
        log_brain_event(
            "metacognition",
            f"Metacognitive check: {check}",
            0.8,
            {"check_type": check, "status": "complete"}
        )
        print(f"✓ Logged metacognitive check: {check}")


def example_decision_integration():
    """
    Example of integrating with decision-making system.
    """
    
    decisions = [
        ("Execute trade: BUY NVDA", 0.85),
        ("Set stop-loss at -5%", 0.90),
        ("Skip this opportunity", 0.65),
        ("Rebalance portfolio", 0.75)
    ]
    
    for decision, confidence in decisions:
        log_brain_event(
            "decision",
            f"Decision: {decision}",
            confidence,
            {"decision": decision, "confidence": confidence, "timestamp": "now"}
        )
        print(f"✓ Logged decision: {decision} (confidence: {confidence})")


def run_full_demo():
    """Run complete demo of all integrations."""
    print("=" * 60)
    print("ATLAS BRAIN VISUALIZATION - INTEGRATION EXAMPLES")
    print("=" * 60)
    print()
    
    print("1. Pattern Recognition Integration")
    print("-" * 40)
    example_pattern_match_integration()
    print()
    
    print("2. Somatic Marker Integration")
    print("-" * 40)
    example_somatic_marker_integration()
    print()
    
    print("3. Cognitive Mode Integration")
    print("-" * 40)
    example_cognitive_mode_integration()
    print()
    
    print("4. Metacognition Integration")
    print("-" * 40)
    example_metacognition_integration()
    print()
    
    print("5. Decision-Making Integration")
    print("-" * 40)
    example_decision_integration()
    print()
    
    print("=" * 60)
    print("✓ All example events logged!")
    print("View them at: http://localhost:8765")
    print("=" * 60)


if __name__ == "__main__":
    run_full_demo()
