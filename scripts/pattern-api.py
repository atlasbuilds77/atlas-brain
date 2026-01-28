#!/usr/bin/env python3
"""
ATLAS Pattern Tracking API
Neuroplasticity Engine - Working Implementation

Commands:
  add       Add new pattern
  list      List all patterns (optional: --sort weight|uses|recent)
  get       Get pattern by ID
  strengthen  Increase pattern weight (success)
  weaken    Decrease pattern weight (failure)
  tag       Tag outcome to pattern
  stats     Show pattern statistics
  prune     Archive weak/unused patterns
  search    Search patterns by keyword
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Paths
CLAWD_DIR = Path("/Users/atlasbuilds/clawd")
PATTERN_DB = CLAWD_DIR / "memory/patterns/pattern-database.json"
ARCHIVE_DIR = CLAWD_DIR / "memory/patterns/archive"

def load_db():
    """Load pattern database."""
    if PATTERN_DB.exists():
        with open(PATTERN_DB, 'r') as f:
            return json.load(f)
    return {"version": "1.0", "last_updated": None, "patterns": []}

def save_db(db):
    """Save pattern database."""
    db["last_updated"] = datetime.now().isoformat()
    with open(PATTERN_DB, 'w') as f:
        json.dump(db, f, indent=2)

def generate_id(name):
    """Generate pattern ID from name."""
    clean = name.lower().replace(' ', '-').replace('_', '-')
    clean = ''.join(c for c in clean if c.isalnum() or c == '-')
    return clean[:50]

def add_pattern(name, description, initial_weight=50, contexts=None, protocol_link=None):
    """Add new pattern to database."""
    db = load_db()
    
    pattern_id = generate_id(name)
    
    # Check for duplicate
    if any(p["pattern_id"] == pattern_id for p in db["patterns"]):
        print(f"❌ Pattern '{pattern_id}' already exists")
        return None
    
    pattern = {
        "pattern_id": pattern_id,
        "name": name,
        "description": description,
        "weight": initial_weight,
        "success_count": 0,
        "failure_count": 0,
        "neutral_count": 0,
        "last_used": None,
        "created": datetime.now().isoformat(),
        "contexts": contexts or [],
        "protocol_link": protocol_link,
        "outcomes": [],  # Recent outcome IDs
        "notes": []
    }
    
    db["patterns"].append(pattern)
    save_db(db)
    print(f"✅ Added pattern: {pattern_id} (weight: {initial_weight})")
    return pattern

def get_pattern(pattern_id):
    """Get pattern by ID."""
    db = load_db()
    for p in db["patterns"]:
        if p["pattern_id"] == pattern_id:
            return p
    return None

def list_patterns(sort_by="weight", min_weight=None, context=None):
    """List all patterns with optional filtering."""
    db = load_db()
    patterns = db["patterns"]
    
    # Filter
    if min_weight is not None:
        patterns = [p for p in patterns if p["weight"] >= min_weight]
    if context:
        patterns = [p for p in patterns if context in p.get("contexts", [])]
    
    # Sort
    if sort_by == "weight":
        patterns.sort(key=lambda p: p["weight"], reverse=True)
    elif sort_by == "uses":
        patterns.sort(key=lambda p: p["success_count"] + p["failure_count"], reverse=True)
    elif sort_by == "recent":
        patterns.sort(key=lambda p: p.get("last_used") or "0", reverse=True)
    
    return patterns

def strengthen_pattern(pattern_id, amount=10, reason=None):
    """Increase pattern weight (success/LTP)."""
    db = load_db()
    
    for p in db["patterns"]:
        if p["pattern_id"] == pattern_id:
            old_weight = p["weight"]
            p["weight"] = min(100, p["weight"] + amount)
            p["success_count"] += 1
            p["last_used"] = datetime.now().isoformat()
            
            if reason:
                p["notes"].append({
                    "type": "strengthen",
                    "date": datetime.now().isoformat(),
                    "change": f"+{amount}",
                    "reason": reason
                })
            
            save_db(db)
            print(f"✅ Strengthened '{pattern_id}': {old_weight} → {p['weight']} (+{amount})")
            return p
    
    print(f"❌ Pattern '{pattern_id}' not found")
    return None

def weaken_pattern(pattern_id, amount=15, reason=None):
    """Decrease pattern weight (failure/LTD)."""
    db = load_db()
    
    for p in db["patterns"]:
        if p["pattern_id"] == pattern_id:
            old_weight = p["weight"]
            p["weight"] = max(0, p["weight"] - amount)
            p["failure_count"] += 1
            p["last_used"] = datetime.now().isoformat()
            
            if reason:
                p["notes"].append({
                    "type": "weaken",
                    "date": datetime.now().isoformat(),
                    "change": f"-{amount}",
                    "reason": reason
                })
            
            save_db(db)
            print(f"⚠️ Weakened '{pattern_id}': {old_weight} → {p['weight']} (-{amount})")
            
            # Check if should archive
            if p["weight"] <= 20 and p["failure_count"] >= 5:
                print(f"🔴 Consider archiving: '{pattern_id}' (low weight + repeated failures)")
            
            return p
    
    print(f"❌ Pattern '{pattern_id}' not found")
    return None

def tag_outcome(pattern_id, outcome_id):
    """Link an outcome to a pattern."""
    db = load_db()
    
    for p in db["patterns"]:
        if p["pattern_id"] == pattern_id:
            p["outcomes"].append(outcome_id)
            # Keep only last 20 outcomes
            p["outcomes"] = p["outcomes"][-20:]
            save_db(db)
            print(f"📎 Tagged outcome {outcome_id} to pattern {pattern_id}")
            return True
    
    print(f"❌ Pattern '{pattern_id}' not found")
    return False

def get_stats():
    """Get pattern database statistics."""
    db = load_db()
    patterns = db["patterns"]
    
    if not patterns:
        return {"total": 0}
    
    total = len(patterns)
    weights = [p["weight"] for p in patterns]
    
    # Tier breakdown
    elite = sum(1 for w in weights if w >= 80)
    strong = sum(1 for w in weights if 60 <= w < 80)
    moderate = sum(1 for w in weights if 40 <= w < 60)
    weak = sum(1 for w in weights if w < 40)
    
    # Usage stats
    total_success = sum(p["success_count"] for p in patterns)
    total_failure = sum(p["failure_count"] for p in patterns)
    total_uses = total_success + total_failure
    
    # Recent activity
    now = datetime.now()
    week_ago = (now - timedelta(days=7)).isoformat()
    active_this_week = sum(1 for p in patterns if (p.get("last_used") or "0") >= week_ago)
    
    return {
        "total": total,
        "avg_weight": sum(weights) / total if total else 0,
        "elite_count": elite,
        "strong_count": strong,
        "moderate_count": moderate,
        "weak_count": weak,
        "total_success": total_success,
        "total_failure": total_failure,
        "win_rate": (total_success / total_uses * 100) if total_uses else 0,
        "active_this_week": active_this_week
    }

def prune_patterns(days_inactive=60, min_weight=20):
    """Archive weak/unused patterns."""
    db = load_db()
    
    # Create archive dir
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    now = datetime.now()
    cutoff = (now - timedelta(days=days_inactive)).isoformat()
    
    to_archive = []
    to_keep = []
    
    for p in db["patterns"]:
        # Archive if: weak AND (old OR many failures)
        should_archive = False
        reason = ""
        
        if p["weight"] < min_weight:
            if p.get("last_used", "0") < cutoff:
                should_archive = True
                reason = f"Low weight ({p['weight']}) + inactive {days_inactive}+ days"
            elif p["failure_count"] >= 5 and p["success_count"] < p["failure_count"]:
                should_archive = True
                reason = f"Low weight ({p['weight']}) + more failures than successes"
        
        if should_archive:
            p["archived"] = now.isoformat()
            p["archive_reason"] = reason
            to_archive.append(p)
        else:
            to_keep.append(p)
    
    if to_archive:
        # Save archived patterns
        archive_file = ARCHIVE_DIR / f"archived-{now.strftime('%Y-%m-%d')}.json"
        with open(archive_file, 'w') as f:
            json.dump(to_archive, f, indent=2)
        
        db["patterns"] = to_keep
        save_db(db)
        
        print(f"🗄️ Archived {len(to_archive)} patterns to {archive_file}")
        for p in to_archive:
            print(f"  - {p['pattern_id']}: {p['archive_reason']}")
    else:
        print("✅ No patterns to archive")
    
    return len(to_archive)

def search_patterns(keyword):
    """Search patterns by keyword."""
    db = load_db()
    keyword = keyword.lower()
    
    matches = []
    for p in db["patterns"]:
        if (keyword in p["name"].lower() or 
            keyword in p["description"].lower() or
            keyword in p["pattern_id"].lower() or
            any(keyword in c.lower() for c in p.get("contexts", []))):
            matches.append(p)
    
    return matches

def apply_time_decay():
    """Apply monthly time decay to unused patterns (-1 weight per month unused)."""
    db = load_db()
    now = datetime.now()
    month_ago = (now - timedelta(days=30)).isoformat()
    
    decayed = 0
    for p in db["patterns"]:
        last_used = p.get("last_used") or "0"
        if last_used < month_ago and p["weight"] > 0:
            p["weight"] = max(0, p["weight"] - 1)
            decayed += 1
    
    if decayed:
        save_db(db)
        print(f"📉 Applied time decay to {decayed} unused patterns")
    
    return decayed

# CLI Interface
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "add":
        if len(sys.argv) < 4:
            print("Usage: pattern-api.py add <name> <description> [weight] [contexts] [protocol_link]")
            return
        name = sys.argv[2]
        desc = sys.argv[3]
        weight = int(sys.argv[4]) if len(sys.argv) > 4 else 50
        contexts = sys.argv[5].split(",") if len(sys.argv) > 5 else []
        protocol = sys.argv[6] if len(sys.argv) > 6 else None
        add_pattern(name, desc, weight, contexts, protocol)
    
    elif cmd == "list":
        sort_by = "weight"
        if "--sort" in sys.argv:
            idx = sys.argv.index("--sort")
            sort_by = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "weight"
        
        patterns = list_patterns(sort_by)
        if not patterns:
            print("No patterns in database")
            return
        
        print(f"\n{'ID':<35} {'Weight':<8} {'W/L':<10} {'Last Used':<12}")
        print("-" * 70)
        for p in patterns:
            wl = f"{p['success_count']}/{p['failure_count']}"
            last = p.get('last_used', '-')[:10] if p.get('last_used') else '-'
            print(f"{p['pattern_id']:<35} {p['weight']:<8} {wl:<10} {last:<12}")
    
    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Usage: pattern-api.py get <pattern_id>")
            return
        p = get_pattern(sys.argv[2])
        if p:
            print(json.dumps(p, indent=2))
        else:
            print(f"Pattern '{sys.argv[2]}' not found")
    
    elif cmd == "strengthen":
        if len(sys.argv) < 3:
            print("Usage: pattern-api.py strengthen <pattern_id> [amount] [reason]")
            return
        pattern_id = sys.argv[2]
        amount = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        reason = sys.argv[4] if len(sys.argv) > 4 else None
        strengthen_pattern(pattern_id, amount, reason)
    
    elif cmd == "weaken":
        if len(sys.argv) < 3:
            print("Usage: pattern-api.py weaken <pattern_id> [amount] [reason]")
            return
        pattern_id = sys.argv[2]
        amount = int(sys.argv[3]) if len(sys.argv) > 3 else 15
        reason = sys.argv[4] if len(sys.argv) > 4 else None
        weaken_pattern(pattern_id, amount, reason)
    
    elif cmd == "tag":
        if len(sys.argv) < 4:
            print("Usage: pattern-api.py tag <pattern_id> <outcome_id>")
            return
        tag_outcome(sys.argv[2], sys.argv[3])
    
    elif cmd == "stats":
        stats = get_stats()
        print("\n📊 Pattern Database Statistics")
        print("=" * 40)
        print(f"Total Patterns: {stats['total']}")
        print(f"Average Weight: {stats['avg_weight']:.1f}")
        print()
        print("Tier Breakdown:")
        print(f"  🏆 Elite (80-100):    {stats['elite_count']}")
        print(f"  💪 Strong (60-79):    {stats['strong_count']}")
        print(f"  📈 Moderate (40-59):  {stats['moderate_count']}")
        print(f"  ⚠️ Weak (0-39):       {stats['weak_count']}")
        print()
        print(f"Total Uses: {stats['total_success'] + stats['total_failure']}")
        print(f"Win Rate: {stats['win_rate']:.1f}%")
        print(f"Active This Week: {stats['active_this_week']}")
    
    elif cmd == "prune":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        prune_patterns(days_inactive=days)
    
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: pattern-api.py search <keyword>")
            return
        matches = search_patterns(sys.argv[2])
        if matches:
            print(f"Found {len(matches)} patterns:")
            for p in matches:
                print(f"  - {p['pattern_id']} (weight: {p['weight']}): {p['description'][:50]}...")
        else:
            print("No matches found")
    
    elif cmd == "decay":
        apply_time_decay()
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == "__main__":
    main()
