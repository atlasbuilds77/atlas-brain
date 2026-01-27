#!/usr/bin/env python3
"""
CONFIDENCE/EMOTION SYSTEM
Tracks confidence levels, uncertainty, and "gut feelings" about decisions.
Mimics somatic markers - emotional tags that guide reasoning.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Auto-detect workspace
SCRIPT_DIR = Path(__file__).parent
WORKSPACE_DIR = SCRIPT_DIR.parent
MEMORY_DIR = WORKSPACE_DIR / "memory"
CONFIDENCE_LOG = MEMORY_DIR / "confidence-log.jsonl"

# Confidence levels
CONFIDENCE_LEVELS = {
    "certain": {"score": 95, "emoji": "💯", "action": "proceed"},
    "high": {"score": 80, "emoji": "✅", "action": "proceed"},
    "moderate": {"score": 60, "emoji": "🤔", "action": "proceed with caution"},
    "low": {"score": 40, "emoji": "⚠️", "action": "verify first"},
    "uncertain": {"score": 20, "emoji": "❓", "action": "research more"},
    "gut_bad": {"score": 10, "emoji": "🚨", "action": "stop and reconsider"}
}

def log_confidence(topic: str, level: str, reasoning: str = "", source: str = ""):
    """Log a confidence assessment."""
    if level not in CONFIDENCE_LEVELS:
        print(f"Invalid level. Choose from: {list(CONFIDENCE_LEVELS.keys())}")
        return
    
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "topic": topic,
        "level": level,
        "score": CONFIDENCE_LEVELS[level]["score"],
        "reasoning": reasoning,
        "source": source
    }
    
    with open(CONFIDENCE_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    info = CONFIDENCE_LEVELS[level]
    print(f"{info['emoji']} Confidence logged: {topic}")
    print(f"   Level: {level} ({info['score']}%)")
    print(f"   Recommended action: {info['action']}")
    if reasoning:
        print(f"   Reasoning: {reasoning}")

def get_recent_confidence(n: int = 10):
    """Get recent confidence logs."""
    if not CONFIDENCE_LOG.exists():
        print("No confidence logs yet.")
        return []
    
    entries = []
    with open(CONFIDENCE_LOG, "r") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    
    return entries[-n:]

def analyze_patterns():
    """Analyze confidence patterns over time."""
    if not CONFIDENCE_LOG.exists():
        print("No confidence logs yet.")
        return
    
    entries = []
    with open(CONFIDENCE_LOG, "r") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    
    if not entries:
        print("No entries to analyze.")
        return
    
    avg_score = sum(e["score"] for e in entries) / len(entries)
    low_confidence = [e for e in entries if e["score"] < 50]
    gut_bad = [e for e in entries if e["level"] == "gut_bad"]
    
    print("📊 CONFIDENCE PATTERN ANALYSIS")
    print("=" * 40)
    print(f"Total entries: {len(entries)}")
    print(f"Average confidence: {avg_score:.1f}%")
    print(f"Low confidence decisions: {len(low_confidence)}")
    print(f"Gut-bad warnings: {len(gut_bad)}")
    
    if low_confidence:
        print("\n⚠️ Recent low-confidence topics:")
        for e in low_confidence[-5:]:
            print(f"   - {e['topic']} ({e['level']})")
    
    if gut_bad:
        print("\n🚨 Gut-bad warnings (REVIEW THESE):")
        for e in gut_bad[-5:]:
            print(f"   - {e['topic']}: {e['reasoning']}")

def main():
    if len(sys.argv) < 2:
        print("CONFIDENCE SYSTEM")
        print("=" * 40)
        print("Usage:")
        print("  confidence.py log <topic> <level> [reasoning]")
        print("  confidence.py recent [n]")
        print("  confidence.py analyze")
        print("")
        print("Levels:", list(CONFIDENCE_LEVELS.keys()))
        return
    
    cmd = sys.argv[1]
    
    if cmd == "log" and len(sys.argv) >= 4:
        topic = sys.argv[2]
        level = sys.argv[3]
        reasoning = sys.argv[4] if len(sys.argv) > 4 else ""
        log_confidence(topic, level, reasoning)
    
    elif cmd == "recent":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        entries = get_recent_confidence(n)
        for e in entries:
            info = CONFIDENCE_LEVELS.get(e["level"], {})
            emoji = info.get("emoji", "")
            print(f"{emoji} [{e['timestamp'][:10]}] {e['topic']}: {e['level']} ({e['score']}%)")
    
    elif cmd == "analyze":
        analyze_patterns()
    
    else:
        print("Unknown command. Run without args for help.")

if __name__ == "__main__":
    main()
