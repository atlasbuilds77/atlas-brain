#!/usr/bin/env python3
"""
ATLAS MEMORY CONSOLIDATION ENGINE
Intelligent memory consolidation inspired by hippocampal sleep replay.
Analyzes memories, scores importance, suggests consolidation actions.
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

CLAWD_DIR = Path.home() / "clawd"
MEMORY_DIR = CLAWD_DIR / "memory"

# Importance scoring keywords
HIGH_PRIORITY_KEYWORDS = [
    "remember this", "important", "critical", "don't forget",
    "key insight", "decision", "money", "trading", "position",
    "learned", "mistake", "always", "never", "rule"
]

MEDIUM_PRIORITY_KEYWORDS = [
    "note", "todo", "task", "project", "meeting", "person",
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
    
    # Check for high priority keywords
    for kw in HIGH_PRIORITY_KEYWORDS:
        if kw in content_lower:
            score += 15
            reasons.append(f"Contains '{kw}'")
    
    # Check for medium priority keywords
    for kw in MEDIUM_PRIORITY_KEYWORDS:
        if kw in content_lower:
            score += 5
            reasons.append(f"Contains '{kw}'")
    
    # Check for low priority keywords (slight decrease)
    for kw in LOW_PRIORITY_KEYWORDS:
        if kw in content_lower:
            score -= 3
    
    # Boost for YAML frontmatter with importance tag
    if "importance: high" in content_lower:
        score += 30
        reasons.append("Explicit high importance tag")
    elif "importance: low" in content_lower:
        score -= 20
        reasons.append("Explicit low importance tag")
    
    # Boost for trading-related files
    if "trading" in filename.lower() or "position" in filename.lower():
        score += 20
        reasons.append("Trading-related file")
    
    # Boost for files with financial figures
    if re.search(r'\$\d+', content):
        score += 10
        reasons.append("Contains financial figures")
    
    # Recency boost (check for recent dates in content)
    today = datetime.now()
    for days_ago in range(7):
        check_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        if check_date in content:
            score += (7 - days_ago) * 2
            reasons.append(f"References recent date ({check_date})")
            break
    
    # Cap score
    score = max(0, min(100, score))
    
    return {
        "score": score,
        "priority": "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW",
        "reasons": reasons[:5]  # Top 5 reasons
    }

def analyze_memories():
    """Analyze all memory files and generate importance report."""
    results = []
    
    for md_file in MEMORY_DIR.rglob("*.md"):
        # Skip archive
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
    
    # Sort by score descending
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
    
    report.append("## Consolidation Recommendations")
    if len(low) > 10:
        report.append(f"- Archive {len(low) - 5} low-priority files")
    if len(results) > 50:
        report.append("- Memory file count high - consider merging related files")
    
    total_size = sum(r['size'] for r in results)
    if total_size > 500000:  # 500KB
        report.append(f"- Total memory size ({total_size/1000:.1f}KB) is large - prune aggressively")
    
    return "\n".join(report)

def main():
    print("🧠 ATLAS MEMORY CONSOLIDATION ENGINE")
    print("=" * 50)
    
    results = analyze_memories()
    report = generate_report(results)
    
    # Save report
    report_path = MEMORY_DIR / "consolidation-analysis.md"
    report_path.write_text(report)
    
    print(report)
    print("")
    print(f"📝 Full report saved to: {report_path}")

if __name__ == "__main__":
    main()
