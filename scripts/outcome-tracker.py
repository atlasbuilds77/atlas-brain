#!/usr/bin/env python3
"""
ATLAS Outcome Tracking System
Track decision outcomes and link to patterns for learning

Commands:
  log       Log a new outcome
  list      List recent outcomes
  analyze   Analyze pattern performance from outcomes
  link      Link outcome to pattern(s)
  stats     Show outcome statistics
  export    Export outcomes for a date range
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# Paths
CLAWD_DIR = Path("/Users/atlasbuilds/clawd")
OUTCOME_LOG = CLAWD_DIR / "memory/outcomes/outcome-log.jsonl"
PATTERN_API = CLAWD_DIR / "scripts/pattern-api.py"

def ensure_file():
    """Ensure outcome log exists."""
    OUTCOME_LOG.parent.mkdir(parents=True, exist_ok=True)
    if not OUTCOME_LOG.exists():
        OUTCOME_LOG.touch()

def generate_id():
    """Generate unique outcome ID."""
    return f"out-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

def log_outcome(action, context, outcome, pattern_ids=None, learning=None, category=None, details=None):
    """
    Log a new outcome.
    
    Args:
        action: What was done (trade, decision, protocol execution)
        context: Situation/conditions
        outcome: "success", "failure", or "neutral"
        pattern_ids: List of pattern IDs used
        learning: What was learned (optional)
        category: trading/social/research/protocol (optional)
        details: Additional details dict (optional)
    """
    ensure_file()
    
    outcome_id = generate_id()
    
    # Normalize outcome
    if outcome in ["✅", "success", "win", "good"]:
        outcome_code = "success"
    elif outcome in ["❌", "failure", "loss", "bad"]:
        outcome_code = "failure"
    else:
        outcome_code = "neutral"
    
    entry = {
        "outcome_id": outcome_id,
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "context": context,
        "outcome": outcome_code,
        "pattern_ids": pattern_ids or [],
        "learning": learning,
        "category": category,
        "details": details or {}
    }
    
    with open(OUTCOME_LOG, 'a') as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"📝 Logged outcome: {outcome_id}")
    print(f"   Action: {action}")
    print(f"   Outcome: {outcome_code}")
    
    # Auto-update patterns if linked
    if pattern_ids:
        for pid in pattern_ids:
            # Call pattern-api to strengthen/weaken
            if outcome_code == "success":
                subprocess.run([sys.executable, str(PATTERN_API), "strengthen", pid, "10", f"Outcome: {outcome_id}"])
                subprocess.run([sys.executable, str(PATTERN_API), "tag", pid, outcome_id])
            elif outcome_code == "failure":
                subprocess.run([sys.executable, str(PATTERN_API), "weaken", pid, "15", f"Outcome: {outcome_id}"])
                subprocess.run([sys.executable, str(PATTERN_API), "tag", pid, outcome_id])
    
    return outcome_id

def list_outcomes(limit=20, category=None, outcome_filter=None, days=None):
    """List recent outcomes."""
    ensure_file()
    
    entries = []
    cutoff = None
    if days:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    
    with open(OUTCOME_LOG, 'r') as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                # Filter by category
                if category and entry.get("category") != category:
                    continue
                # Filter by outcome
                if outcome_filter and entry.get("outcome") != outcome_filter:
                    continue
                # Filter by date
                if cutoff and entry.get("timestamp", "") < cutoff:
                    continue
                entries.append(entry)
    
    # Sort by timestamp descending
    entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    
    return entries[:limit]

def get_outcome(outcome_id):
    """Get specific outcome by ID."""
    ensure_file()
    
    with open(OUTCOME_LOG, 'r') as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                if entry.get("outcome_id") == outcome_id:
                    return entry
    return None

def analyze_patterns():
    """Analyze pattern performance from outcomes."""
    ensure_file()
    
    pattern_stats = {}
    
    with open(OUTCOME_LOG, 'r') as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                for pid in entry.get("pattern_ids", []):
                    if pid not in pattern_stats:
                        pattern_stats[pid] = {"success": 0, "failure": 0, "neutral": 0}
                    outcome = entry.get("outcome", "neutral")
                    pattern_stats[pid][outcome] = pattern_stats[pid].get(outcome, 0) + 1
    
    # Calculate win rates
    results = []
    for pid, stats in pattern_stats.items():
        total = stats["success"] + stats["failure"]
        win_rate = (stats["success"] / total * 100) if total > 0 else 0
        results.append({
            "pattern_id": pid,
            "success": stats["success"],
            "failure": stats["failure"],
            "neutral": stats["neutral"],
            "total": total,
            "win_rate": win_rate
        })
    
    # Sort by total uses
    results.sort(key=lambda r: r["total"], reverse=True)
    
    return results

def get_stats(days=30):
    """Get outcome statistics."""
    ensure_file()
    
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    
    stats = {
        "total": 0,
        "success": 0,
        "failure": 0,
        "neutral": 0,
        "categories": {},
        "recent_learnings": []
    }
    
    with open(OUTCOME_LOG, 'r') as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                if entry.get("timestamp", "") >= cutoff:
                    stats["total"] += 1
                    outcome = entry.get("outcome", "neutral")
                    stats[outcome] = stats.get(outcome, 0) + 1
                    
                    # Category breakdown
                    cat = entry.get("category", "uncategorized")
                    if cat not in stats["categories"]:
                        stats["categories"][cat] = {"success": 0, "failure": 0, "neutral": 0}
                    stats["categories"][cat][outcome] += 1
                    
                    # Collect learnings
                    if entry.get("learning"):
                        stats["recent_learnings"].append({
                            "timestamp": entry["timestamp"][:10],
                            "learning": entry["learning"][:100]
                        })
    
    # Calculate overall win rate
    total_decisions = stats["success"] + stats["failure"]
    stats["win_rate"] = (stats["success"] / total_decisions * 100) if total_decisions > 0 else 0
    
    # Keep only last 5 learnings
    stats["recent_learnings"] = stats["recent_learnings"][-5:]
    
    return stats

def link_outcome(outcome_id, pattern_ids):
    """Link existing outcome to patterns (retroactive)."""
    ensure_file()
    
    # Read all lines
    entries = []
    found = False
    with open(OUTCOME_LOG, 'r') as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                if entry.get("outcome_id") == outcome_id:
                    found = True
                    # Add patterns
                    existing = entry.get("pattern_ids", [])
                    entry["pattern_ids"] = list(set(existing + pattern_ids))
                    
                    # Update patterns based on outcome
                    for pid in pattern_ids:
                        if entry.get("outcome") == "success":
                            subprocess.run([sys.executable, str(PATTERN_API), "strengthen", pid, "10"])
                        elif entry.get("outcome") == "failure":
                            subprocess.run([sys.executable, str(PATTERN_API), "weaken", pid, "15"])
                        subprocess.run([sys.executable, str(PATTERN_API), "tag", pid, outcome_id])
                
                entries.append(entry)
    
    if not found:
        print(f"❌ Outcome '{outcome_id}' not found")
        return False
    
    # Rewrite file
    with open(OUTCOME_LOG, 'w') as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
    
    print(f"✅ Linked outcome {outcome_id} to patterns: {pattern_ids}")
    return True

def export_outcomes(start_date=None, end_date=None, filepath=None):
    """Export outcomes to file."""
    ensure_file()
    
    entries = []
    with open(OUTCOME_LOG, 'r') as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                ts = entry.get("timestamp", "")
                
                if start_date and ts < start_date:
                    continue
                if end_date and ts > end_date:
                    continue
                entries.append(entry)
    
    if filepath:
        with open(filepath, 'w') as f:
            json.dump(entries, f, indent=2)
        print(f"✅ Exported {len(entries)} outcomes to {filepath}")
    
    return entries

# CLI Interface
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "log":
        if len(sys.argv) < 4:
            print("Usage: outcome-tracker.py log <action> <context> <outcome> [pattern_ids] [learning] [category]")
            print("  outcome: success/failure/neutral")
            print("  pattern_ids: comma-separated list")
            return
        action = sys.argv[2]
        context = sys.argv[3]
        outcome = sys.argv[4] if len(sys.argv) > 4 else "neutral"
        pattern_ids = sys.argv[5].split(",") if len(sys.argv) > 5 and sys.argv[5] else []
        learning = sys.argv[6] if len(sys.argv) > 6 else None
        category = sys.argv[7] if len(sys.argv) > 7 else None
        log_outcome(action, context, outcome, pattern_ids, learning, category)
    
    elif cmd == "list":
        limit = 20
        category = None
        outcome_filter = None
        days = None
        
        # Parse flags
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "-n" and i + 1 < len(sys.argv):
                limit = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--category" and i + 1 < len(sys.argv):
                category = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--outcome" and i + 1 < len(sys.argv):
                outcome_filter = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--days" and i + 1 < len(sys.argv):
                days = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        
        outcomes = list_outcomes(limit, category, outcome_filter, days)
        if not outcomes:
            print("No outcomes found")
            return
        
        print(f"\n{'Timestamp':<20} {'Outcome':<10} {'Action':<30} {'Patterns':<15}")
        print("-" * 80)
        for o in outcomes:
            ts = o["timestamp"][:16]
            action = o["action"][:28]
            outcome = o["outcome"]
            patterns = ",".join(o.get("pattern_ids", []))[:13]
            emoji = "✅" if outcome == "success" else "❌" if outcome == "failure" else "⚪"
            print(f"{ts:<20} {emoji} {outcome:<7} {action:<30} {patterns:<15}")
    
    elif cmd == "analyze":
        results = analyze_patterns()
        if not results:
            print("No pattern data to analyze")
            return
        
        print(f"\n{'Pattern ID':<30} {'W/L':<10} {'Win Rate':<10} {'Total':<8}")
        print("-" * 60)
        for r in results:
            wl = f"{r['success']}/{r['failure']}"
            print(f"{r['pattern_id']:<30} {wl:<10} {r['win_rate']:.1f}%     {r['total']:<8}")
    
    elif cmd == "stats":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        stats = get_stats(days)
        
        print(f"\n📊 Outcome Statistics (Last {days} Days)")
        print("=" * 40)
        print(f"Total Outcomes: {stats['total']}")
        print(f"  ✅ Success: {stats['success']}")
        print(f"  ❌ Failure: {stats['failure']}")
        print(f"  ⚪ Neutral: {stats['neutral']}")
        print(f"Win Rate: {stats['win_rate']:.1f}%")
        
        if stats["categories"]:
            print("\nBy Category:")
            for cat, data in stats["categories"].items():
                total = data["success"] + data["failure"]
                wr = (data["success"] / total * 100) if total > 0 else 0
                print(f"  {cat}: {data['success']}/{data['failure']} ({wr:.0f}%)")
        
        if stats["recent_learnings"]:
            print("\nRecent Learnings:")
            for l in stats["recent_learnings"]:
                print(f"  [{l['timestamp']}] {l['learning']}")
    
    elif cmd == "link":
        if len(sys.argv) < 4:
            print("Usage: outcome-tracker.py link <outcome_id> <pattern_id1,pattern_id2,...>")
            return
        outcome_id = sys.argv[2]
        pattern_ids = sys.argv[3].split(",")
        link_outcome(outcome_id, pattern_ids)
    
    elif cmd == "export":
        start = sys.argv[2] if len(sys.argv) > 2 else None
        end = sys.argv[3] if len(sys.argv) > 3 else None
        filepath = sys.argv[4] if len(sys.argv) > 4 else None
        export_outcomes(start, end, filepath)
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == "__main__":
    main()
