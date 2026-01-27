#!/usr/bin/env python3
"""
MEMORY CONSOLIDATION ENGINE
Intelligent memory consolidation inspired by hippocampal sleep replay.
Analyzes memories, scores importance, suggests consolidation actions.
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# Auto-detect workspace (parent of scripts folder)
SCRIPT_DIR = Path(__file__).parent
WORKSPACE_DIR = SCRIPT_DIR.parent
MEMORY_DIR = WORKSPACE_DIR / "memory"

# Importance scoring keywords
HIGH_PRIORITY_KEYWORDS = [
    "remember this", "important", "critical", "don't forget",
    "key insight", "decision", "money", "task", "deadline",
    "learned", "mistake", "always", "never", "rule"
]

MEDIUM_PRIORITY_KEYWORDS = [
    "note", "todo", "project", "meeting", "person",
    "contact", "preference", "workflow"
]

LOW_PRIORITY_KEYWORDS = [
    "research", "exploration", "maybe", "consider", "idea",
    "random", "thought"
]

def score_importance(content: str, filename: str) -> dict:
    """Score a memory file's importance based on content analysis."""
    content_lower = content.lower()
    score = 50  # Base score
    reasons = []
    
    for kw in HIGH_PRIORITY_KEYWORDS:
        if kw in content_lower:
            score += 15
            reasons.append(f"Contains '{kw}'")
    
    for kw in MEDIUM_PRIORITY_KEYWORDS:
        if kw in content_lower:
            score += 5
            reasons.append(f"Contains '{kw}'")
    
    for kw in LOW_PRIORITY_KEYWORDS:
        if kw in content_lower:
            score -= 3
    
    if "importance: high" in content_lower:
        score += 30
        reasons.append("Explicit high importance tag")
    elif "importance: low" in content_lower:
        score -= 20
        reasons.append("Explicit low importance tag")
    
    if re.search(r'\$\d+', content):
        score += 10
        reasons.append("Contains financial figures")
    
    today = datetime.now()
    for days_ago in range(7):
        check_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        if check_date in content:
            score += (7 - days_ago) * 2
            reasons.append(f"References recent date ({check_date})")
            break
    
    score = max(0, min(100, score))
    
    return {
        "score": score,
        "priority": "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW",
        "reasons": reasons[:5]
    }

def analyze_memories():
    """Analyze all memory files and generate importance report."""
    results = []
    
    if not MEMORY_DIR.exists():
        print(f"Memory directory not found: {MEMORY_DIR}")
        return results
    
    for md_file in MEMORY_DIR.rglob("*.md"):
        if "archive" in str(md_file):
            continue
        
        try:
            content = md_file.read_text()
            rel_path = md_file.relative_to(MEMORY_DIR)
            analysis = score_importance(content, str(rel_path))
            
            results.append({
                "file": str(rel_path),
                "size": len(content),
                "lines": len(content.splitlines()),
                **analysis
            })
        except Exception as e:
            print(f"Error analyzing {md_file}: {e}")
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

def generate_report(results):
    """Generate consolidation recommendations."""
    high = [r for r in results if r["priority"] == "HIGH"]
    medium = [r for r in results if r["priority"] == "MEDIUM"]
    low = [r for r in results if r["priority"] == "LOW"]
    
    report = []
    report.append("# Memory Importance Analysis")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")
    report.append(f"## Summary")
    report.append(f"- **HIGH priority:** {len(high)} files")
    report.append(f"- **MEDIUM priority:** {len(medium)} files")
    report.append(f"- **LOW priority:** {len(low)} files")
    report.append("")
    
    report.append("## HIGH Priority (Protect)")
    for r in high[:10]:
        report.append(f"- **{r['file']}** (score: {r['score']})")
        for reason in r['reasons'][:2]:
            report.append(f"  - {reason}")
    report.append("")
    
    report.append("## LOW Priority (Consider Archiving)")
    for r in low[:10]:
        report.append(f"- {r['file']} (score: {r['score']})")
    report.append("")
    
    report.append("## Recommendations")
    if len(low) > 10:
        report.append(f"- Archive {len(low) - 5} low-priority files")
    if len(results) > 50:
        report.append("- Memory file count high - consider merging related files")
    
    total_size = sum(r['size'] for r in results)
    if total_size > 500000:
        report.append(f"- Total memory size ({total_size/1000:.1f}KB) is large - prune aggressively")
    
    return "\n".join(report)

def main():
    print("🧠 MEMORY CONSOLIDATION ENGINE")
    print("=" * 50)
    print(f"Workspace: {WORKSPACE_DIR}")
    print(f"Memory: {MEMORY_DIR}")
    print("")
    
    results = analyze_memories()
    
    if not results:
        print("No memory files found to analyze.")
        return
    
    report = generate_report(results)
    
    report_path = MEMORY_DIR / "consolidation-analysis.md"
    report_path.write_text(report)
    
    print(report)
    print("")
    print(f"📝 Full report saved to: {report_path}")

if __name__ == "__main__":
    main()
