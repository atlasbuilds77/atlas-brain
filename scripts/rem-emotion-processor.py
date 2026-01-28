#!/usr/bin/env python3
"""
ATLAS REM EMOTIONAL PROCESSOR

Integrates with sleep cycles to process emotional outcomes.
Based on research: sleep (especially REM) consolidates emotional memories
and updates somatic markers.

This runs during sleep phases to:
1. Process recent emotional outcomes
2. Update somatic marker confidence
3. Find cross-domain emotional patterns
4. Generate emotional insights for dreams

Usage:
  rem-emotion-processor.py process  # Process recent emotional data
  rem-emotion-processor.py insights # Generate insights for dream synthesis
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

CLAWD_DIR = Path.home() / "clawd"
MARKERS_FILE = CLAWD_DIR / "memory" / "emotions" / "somatic-markers.json"
DECISIONS_LOG = CLAWD_DIR / "memory" / "decisions" / "decision-log.jsonl"
CALIBRATION_FILE = CLAWD_DIR / "memory" / "calibration" / "confidence-history.json"
REM_OUTPUT = CLAWD_DIR / "memory" / "emotions" / "rem-processing.json"

def load_json(path):
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)

def load_jsonl(path):
    if not path.exists():
        return []
    entries = []
    with open(path, "r") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def process_emotional_outcomes():
    """
    Process recent emotional outcomes and update markers.
    Called during REM sleep phases.
    """
    markers_data = load_json(MARKERS_FILE)
    decisions = load_jsonl(DECISIONS_LOG)
    calibration = load_json(CALIBRATION_FILE)
    
    # Get recent decisions (last 24 hours)
    cutoff = datetime.now() - timedelta(hours=24)
    recent = []
    for d in decisions:
        try:
            ts = datetime.fromisoformat(d["timestamp"])
            if ts > cutoff:
                recent.append(d)
        except:
            pass
    
    processing_results = {
        "timestamp": datetime.now().isoformat(),
        "phase": "REM_emotional_processing",
        "decisions_processed": len(recent),
        "pattern_updates": [],
        "emotional_insights": [],
        "confidence_adjustments": []
    }
    
    # Analyze emotional valence sequences
    valence_sequence = []
    for d in recent:
        feeling = d.get("somatic_feeling", "neutral")
        if feeling in ["strongly_positive", "positive"]:
            valence_sequence.append("positive")
        elif feeling in ["strongly_negative", "negative"]:
            valence_sequence.append("negative")
        else:
            valence_sequence.append("neutral")
    
    # Check for negative→positive sequences (from research: improves decisions)
    neg_to_pos_count = 0
    for i in range(len(valence_sequence) - 1):
        if valence_sequence[i] == "negative" and valence_sequence[i+1] == "positive":
            neg_to_pos_count += 1
    
    if neg_to_pos_count > 0:
        processing_results["emotional_insights"].append({
            "type": "valence_sequence",
            "finding": f"Found {neg_to_pos_count} negative→positive sequences",
            "implication": "Research shows this sequence improves decision quality"
        })
    
    # Find domain-specific emotional patterns
    domain_emotions = defaultdict(list)
    for d in recent:
        domain = d.get("domain", "general")
        domain_emotions[domain].append(d.get("somatic_score", 0))
    
    for domain, scores in domain_emotions.items():
        if len(scores) >= 2:
            avg = sum(scores) / len(scores)
            if avg > 15:
                processing_results["pattern_updates"].append({
                    "domain": domain,
                    "trend": "positive",
                    "avg_score": avg,
                    "recommendation": f"Intuition in {domain} domain appears reliable"
                })
            elif avg < -15:
                processing_results["pattern_updates"].append({
                    "domain": domain,
                    "trend": "negative",
                    "avg_score": avg,
                    "recommendation": f"Multiple negative signals in {domain} - caution warranted"
                })
    
    # Look for unresolved decisions that need outcome tracking
    unresolved = [d for d in recent if not d.get("resolved", False)]
    if unresolved:
        processing_results["emotional_insights"].append({
            "type": "tracking_needed",
            "finding": f"{len(unresolved)} recent decisions await outcome tracking",
            "implication": "Recording outcomes improves somatic marker calibration"
        })
    
    # Generate emotional insights for dream synthesis
    high_emotion_decisions = [d for d in recent 
                              if abs(d.get("somatic_score", 0)) > 20]
    
    for d in high_emotion_decisions[:3]:  # Top 3 most emotional
        processing_results["emotional_insights"].append({
            "type": "high_salience",
            "decision": d.get("decision", "")[:100],
            "emotional_intensity": abs(d.get("somatic_score", 0)),
            "valence": d.get("somatic_feeling", "neutral"),
            "dream_potential": "High - should appear in dream synthesis for pattern finding"
        })
    
    # Save processing results
    save_json(REM_OUTPUT, processing_results)
    
    return processing_results

def generate_dream_insights():
    """
    Generate emotional insights for dream synthesis.
    Called before Stage 4 of sleep cycle.
    """
    rem_data = load_json(REM_OUTPUT)
    markers_data = load_json(MARKERS_FILE)
    
    insights = []
    
    # Pull high-salience emotional events
    for insight in rem_data.get("emotional_insights", []):
        if insight.get("type") == "high_salience":
            insights.append(f"EMOTIONAL: {insight.get('valence', '').upper()} - {insight.get('decision', '')[:80]}")
    
    # Pull pattern updates
    for update in rem_data.get("pattern_updates", []):
        insights.append(f"PATTERN: {update.get('domain', 'general')} trend is {update.get('trend', 'neutral')} - {update.get('recommendation', '')}")
    
    # Pull markers with recent activity
    for marker in markers_data.get("markers", []):
        if marker.get("last_triggered"):
            try:
                last = datetime.strptime(marker["last_triggered"], "%Y-%m-%d")
                if (datetime.now() - last).days <= 1:
                    insights.append(f"MARKER: {marker['pattern']} (intensity {marker['intensity']}) - {marker.get('learning', '')[:60]}")
            except:
                pass
    
    print("=" * 60)
    print("🌙 REM EMOTIONAL INSIGHTS FOR DREAM SYNTHESIS")
    print("=" * 60)
    
    if insights:
        for i, insight in enumerate(insights, 1):
            print(f"\n{i}. {insight}")
    else:
        print("\nNo high-salience emotional events to process.")
        print("(This is normal when no recent decisions or outcomes)")
    
    print("\n" + "=" * 60)
    
    return insights

def main():
    if len(sys.argv) < 2:
        print("ATLAS REM EMOTIONAL PROCESSOR")
        print("=" * 40)
        print("Usage:")
        print("  rem-emotion-processor.py process  - Process emotional outcomes")
        print("  rem-emotion-processor.py insights - Generate dream insights")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "process":
        results = process_emotional_outcomes()
        print("=" * 60)
        print("🌙 REM EMOTIONAL PROCESSING COMPLETE")
        print("=" * 60)
        print(f"\nProcessed {results['decisions_processed']} recent decisions")
        print(f"Generated {len(results['emotional_insights'])} insights")
        print(f"Found {len(results['pattern_updates'])} pattern updates")
        print(f"\nResults saved to: {REM_OUTPUT}")
        
    elif cmd == "insights":
        generate_dream_insights()
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
