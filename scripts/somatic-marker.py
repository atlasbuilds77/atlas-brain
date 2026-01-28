#!/usr/bin/env python3
"""
ATLAS SOMATIC MARKER SYSTEM
Based on Damasio's somatic marker hypothesis.

Somatic markers are emotional tags attached to experiences that guide 
future decision-making through "gut feelings." This system:

1. Stores emotional markers for situation patterns
2. Retrieves markers when facing similar situations  
3. Calculates intuition strength from pattern match × emotional intensity
4. Updates confidence based on outcomes
5. Integrates with REM sleep for emotional processing

Usage:
  somatic-marker.py check "description of situation"
  somatic-marker.py add --pattern "name" --valence pos/neg/neutral --intensity 1-10
  somatic-marker.py outcome --id sm-001 --result win/loss --amount 100
  somatic-marker.py list
  somatic-marker.py analyze "decision context"
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher
import argparse

CLAWD_DIR = Path.home() / "clawd"
MARKERS_FILE = CLAWD_DIR / "memory" / "emotions" / "somatic-markers.json"
CALIBRATION_FILE = CLAWD_DIR / "memory" / "calibration" / "marker-accuracy.json"

def load_markers():
    """Load somatic markers database."""
    if not MARKERS_FILE.exists():
        return {"meta": {}, "markers": []}
    with open(MARKERS_FILE, "r") as f:
        return json.load(f)

def save_markers(data):
    """Save somatic markers database."""
    MARKERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MARKERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts."""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def find_matching_markers(situation: str, threshold: float = 0.3):
    """
    Find somatic markers that match the current situation.
    Returns markers with match confidence.
    """
    data = load_markers()
    matches = []
    situation_lower = situation.lower()
    
    for marker in data.get("markers", []):
        match_score = 0.0
        matched_triggers = []
        
        # Check trigger words
        for trigger in marker.get("triggers", []):
            if trigger.lower() in situation_lower:
                match_score += 0.2
                matched_triggers.append(trigger)
        
        # Check pattern description similarity
        desc_similarity = text_similarity(situation, marker.get("description", ""))
        match_score += desc_similarity * 0.3
        
        # Check pattern name
        pattern_similarity = text_similarity(situation, marker.get("pattern", ""))
        match_score += pattern_similarity * 0.2
        
        # Cap at 1.0
        match_score = min(1.0, match_score)
        
        if match_score >= threshold:
            matches.append({
                "marker": marker,
                "match_confidence": match_score,
                "matched_triggers": matched_triggers
            })
    
    # Sort by match confidence × emotional intensity
    matches.sort(key=lambda x: x["match_confidence"] * x["marker"].get("intensity", 5), reverse=True)
    return matches

def calculate_gut_feeling(matches):
    """
    Calculate overall gut feeling from matched markers.
    
    Gut feeling = Σ(match_confidence × intensity × valence_weight × marker_confidence)
    
    Returns score from -100 to +100 and recommendation.
    """
    if not matches:
        return 0, "neutral", "No strong patterns recognized. Use deliberate analysis."
    
    valence_weights = {"positive": 1.0, "negative": -1.0, "neutral": 0.0}
    
    total_score = 0
    total_weight = 0
    
    for m in matches:
        marker = m["marker"]
        valence = marker.get("valence", "neutral")
        intensity = marker.get("intensity", 5)
        confidence = marker.get("confidence", 0.5)
        match_conf = m["match_confidence"]
        
        weight = match_conf * confidence
        score = weight * intensity * valence_weights.get(valence, 0)
        
        total_score += score
        total_weight += weight
    
    # Normalize to -100 to +100
    if total_weight > 0:
        normalized = (total_score / total_weight) * 10
    else:
        normalized = 0
    
    # Determine gut feeling
    if normalized >= 30:
        feeling = "strongly_positive"
        rec = "Strong positive intuition. Proceed with confidence, but verify key assumptions."
    elif normalized >= 10:
        feeling = "positive"
        rec = "Positive intuition. Good to proceed with standard risk management."
    elif normalized >= -10:
        feeling = "neutral"
        rec = "Mixed/neutral signals. Rely more on deliberate analysis."
    elif normalized >= -30:
        feeling = "negative"
        rec = "Negative intuition. Caution advised. Double-check reasoning."
    else:
        feeling = "strongly_negative"
        rec = "Strong negative gut feeling. Consider NOT proceeding. Past patterns suggest danger."
    
    return normalized, feeling, rec

def check_situation(situation: str):
    """Check a situation against somatic markers and provide gut feeling."""
    matches = find_matching_markers(situation)
    score, feeling, recommendation = calculate_gut_feeling(matches)
    
    print("=" * 60)
    print("🧠 SOMATIC MARKER CHECK")
    print("=" * 60)
    print(f"\n📝 Situation: {situation}")
    print(f"\n🎯 GUT FEELING: {feeling.upper()} (score: {score:.1f})")
    print(f"💡 Recommendation: {recommendation}")
    
    if matches:
        print(f"\n📊 Matched {len(matches)} pattern(s):")
        for i, m in enumerate(matches[:5], 1):  # Top 5
            marker = m["marker"]
            print(f"\n  {i}. {marker['pattern'].replace('_', ' ').title()}")
            print(f"     Valence: {marker['valence']} | Intensity: {marker['intensity']}/10")
            print(f"     Match confidence: {m['match_confidence']:.0%}")
            print(f"     Marker reliability: {marker.get('confidence', 0.5):.0%}")
            if m["matched_triggers"]:
                print(f"     Triggered by: {', '.join(m['matched_triggers'])}")
            if marker.get("learning"):
                print(f"     💭 Learning: {marker['learning']}")
    else:
        print("\n⚠️ No matching patterns found. This is a novel situation.")
        print("   → Default to deliberate analysis (System 2 thinking)")
    
    print("\n" + "=" * 60)
    
    # Return data for programmatic use
    return {
        "score": score,
        "feeling": feeling,
        "recommendation": recommendation,
        "matches": matches
    }

def add_marker(pattern: str, description: str, triggers: list, 
               valence: str, intensity: int, learning: str = ""):
    """Add a new somatic marker."""
    data = load_markers()
    
    # Generate ID
    existing_ids = [m.get("id", "") for m in data.get("markers", [])]
    next_num = len(existing_ids) + 1
    new_id = f"sm-{next_num:03d}"
    
    new_marker = {
        "id": new_id,
        "pattern": pattern,
        "description": description,
        "triggers": triggers,
        "valence": valence,
        "intensity": intensity,
        "outcomes": [],
        "confidence": 0.5,  # Start neutral
        "learning": learning,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "last_triggered": None
    }
    
    data["markers"].append(new_marker)
    save_markers(data)
    
    print(f"✅ Added somatic marker: {new_id} - {pattern}")
    return new_id

def record_outcome(marker_id: str, result: str, amount: float = None, context: str = ""):
    """Record an outcome for a marker to calibrate its confidence."""
    data = load_markers()
    
    for marker in data.get("markers", []):
        if marker.get("id") == marker_id:
            # Add outcome
            outcome = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "result": result,
                "amount": amount,
                "context": context
            }
            marker["outcomes"].append(outcome)
            
            # Update confidence based on outcome
            # If marker predicted correctly, increase confidence
            # If marker predicted incorrectly, decrease confidence
            valence = marker.get("valence", "neutral")
            old_conf = marker.get("confidence", 0.5)
            
            if valence == "positive":
                # Positive marker should predict good outcomes
                correct = result in ["win", "success", "positive"]
            elif valence == "negative":
                # Negative marker should predict bad outcomes
                correct = result in ["loss", "failure", "negative"]
            else:
                correct = True  # Neutral markers always "correct"
            
            # Bayesian-ish update
            if correct:
                new_conf = old_conf * 0.9 + 0.1  # Move toward 1.0
            else:
                new_conf = old_conf * 0.9  # Move toward 0
            
            marker["confidence"] = round(new_conf, 3)
            marker["last_triggered"] = datetime.now().strftime("%Y-%m-%d")
            
            save_markers(data)
            print(f"✅ Recorded outcome for {marker_id}")
            print(f"   Confidence: {old_conf:.0%} → {new_conf:.0%}")
            return True
    
    print(f"❌ Marker {marker_id} not found")
    return False

def list_markers():
    """List all somatic markers."""
    data = load_markers()
    markers = data.get("markers", [])
    
    print("=" * 60)
    print("📚 SOMATIC MARKER DATABASE")
    print("=" * 60)
    
    # Group by valence
    positive = [m for m in markers if m.get("valence") == "positive"]
    negative = [m for m in markers if m.get("valence") == "negative"]
    neutral = [m for m in markers if m.get("valence") == "neutral"]
    
    print(f"\n✅ POSITIVE MARKERS ({len(positive)})")
    for m in positive:
        print(f"  [{m['id']}] {m['pattern']} (intensity: {m['intensity']}, conf: {m.get('confidence', 0.5):.0%})")
    
    print(f"\n❌ NEGATIVE MARKERS ({len(negative)})")
    for m in negative:
        print(f"  [{m['id']}] {m['pattern']} (intensity: {m['intensity']}, conf: {m.get('confidence', 0.5):.0%})")
    
    print(f"\n⚪ NEUTRAL MARKERS ({len(neutral)})")
    for m in neutral:
        print(f"  [{m['id']}] {m['pattern']} (intensity: {m['intensity']}, conf: {m.get('confidence', 0.5):.0%})")
    
    print(f"\n📊 Total: {len(markers)} markers")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(
        description="ATLAS Somatic Marker System - Emotional intuition for decisions"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check situation against markers")
    check_parser.add_argument("situation", help="Description of the situation")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add new marker")
    add_parser.add_argument("--pattern", required=True, help="Pattern name (snake_case)")
    add_parser.add_argument("--description", required=True, help="Pattern description")
    add_parser.add_argument("--triggers", required=True, help="Comma-separated trigger words")
    add_parser.add_argument("--valence", required=True, choices=["positive", "negative", "neutral"])
    add_parser.add_argument("--intensity", required=True, type=int, help="1-10 intensity")
    add_parser.add_argument("--learning", default="", help="Key learning from this pattern")
    
    # Outcome command
    outcome_parser = subparsers.add_parser("outcome", help="Record outcome for marker")
    outcome_parser.add_argument("--id", required=True, help="Marker ID (e.g., sm-001)")
    outcome_parser.add_argument("--result", required=True, help="win/loss/success/failure")
    outcome_parser.add_argument("--amount", type=float, help="Amount won/lost")
    outcome_parser.add_argument("--context", default="", help="Context description")
    
    # List command
    subparsers.add_parser("list", help="List all markers")
    
    args = parser.parse_args()
    
    if args.command == "check":
        check_situation(args.situation)
    elif args.command == "add":
        triggers = [t.strip() for t in args.triggers.split(",")]
        add_marker(args.pattern, args.description, triggers, 
                   args.valence, args.intensity, args.learning)
    elif args.command == "outcome":
        record_outcome(args.id, args.result, args.amount, args.context)
    elif args.command == "list":
        list_markers()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
